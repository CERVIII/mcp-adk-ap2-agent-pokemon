---
title: "[Phase 6.3] Multi-Merchant Support & Price Comparison"
labels: enhancement, ap2, marketplace, phase-6
assignees: CERVIII
---

## 📋 Descripción

Soporte para múltiples merchants: comparación de precios, routing inteligente de órdenes, reputation system, y agregación de inventarios.

## 🎯 Tipo de Issue

- [x] 🤖 AP2 Protocol
- [x] ✨ Nueva feature
- [x] 🏪 Marketplace

## 📦 Fase del Roadmap

**Fase 6.3: Soporte Multi-Merchant**

## ✅ Tareas

### Architecture Overview

```
┌─────────────┐
│   Shopping  │
│    Agent    │
└──────┬──────┘
       │
       ├──────────┐──────────┐──────────┐
       │          │          │          │
    ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐
    │ Poke │  │ Poke │  │ Rare │  │ Shiny│
    │ Mart │  │ Shop │  │ Mon  │  │ Dex  │
    │  #1  │  │  #2  │  │ Store│  │ Pro  │
    └──────┘  └──────┘  └──────┘  └──────┘
       │          │          │          │
       └──────────┴──────────┴──────────┘
                     │
              ┌──────▼──────┐
              │   Agent     │
              │  Aggregator │
              └─────────────┘
```

### Database Schema

```sql
CREATE TABLE merchants (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    logo_url VARCHAR(500),
    discovery_url VARCHAR(500),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Reputation
    rating DECIMAL(3,2),  -- 0.00 to 5.00
    total_reviews INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    
    -- Performance metrics
    avg_response_time_ms INTEGER,
    fulfillment_rate DECIMAL(5,2),  -- Percentage
    avg_delivery_days INTEGER,
    
    created_at TIMESTAMP,
    last_seen TIMESTAMP
);

CREATE TABLE merchant_products (
    id INTEGER PRIMARY KEY,
    merchant_id VARCHAR(100) REFERENCES merchants(id),
    product_id VARCHAR(50),  -- e.g., "25" (Pikachu numero)
    product_name VARCHAR(100),
    price INTEGER,  -- in cents
    currency VARCHAR(3) DEFAULT 'USD',
    in_stock BOOLEAN DEFAULT TRUE,
    stock_quantity INTEGER,
    
    -- Product-specific merchant data
    condition VARCHAR(20),  -- 'new' | 'used' | 'refurbished'
    shipping_cost INTEGER,
    shipping_time_days INTEGER,
    
    last_updated TIMESTAMP,
    
    INDEX idx_product_merchant (product_id, merchant_id),
    INDEX idx_price (product_id, price)
);

CREATE TABLE merchant_reviews (
    id INTEGER PRIMARY KEY,
    merchant_id VARCHAR(100) REFERENCES merchants(id),
    user_id INTEGER REFERENCES users(id),
    transaction_id INTEGER REFERENCES transactions(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP,
    
    UNIQUE(transaction_id)  -- One review per transaction
);

CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    merchant_id VARCHAR(100) REFERENCES merchants(id),
    product_id VARCHAR(50),
    price INTEGER,
    recorded_at TIMESTAMP,
    
    INDEX idx_product_time (product_id, recorded_at)
);
```

### Price Aggregation Service

```python
# ap2-integration/src/common/price_aggregator.py

from typing import List, Dict
import asyncio
import aiohttp

class PriceAggregator:
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
    
    async def compare_prices(
        self,
        product_id: str,
        merchants: List[str] = None
    ) -> List[Dict]:
        """Fetch prices from multiple merchants in parallel"""
        
        # Get merchant list
        if not merchants:
            merchants = await self._get_active_merchants()
        
        # Fetch prices concurrently
        tasks = [
            self._fetch_merchant_price(merchant_id, product_id)
            for merchant_id in merchants
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors and None
        valid_results = [r for r in results if r and not isinstance(r, Exception)]
        
        # Sort by total price (product + shipping)
        sorted_results = sorted(
            valid_results,
            key=lambda x: x['total_price']
        )
        
        return sorted_results
    
    async def _fetch_merchant_price(
        self,
        merchant_id: str,
        product_id: str
    ) -> Dict | None:
        """Fetch price from single merchant"""
        try:
            # Get merchant discovery data
            merchant = await self._get_merchant_info(merchant_id)
            
            # Fetch product price via MCP
            async with aiohttp.ClientSession() as session:
                url = f"{merchant['endpoints']['catalog']}/{product_id}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status != 200:
                        return None
                    
                    data = await resp.json()
                    
                    return {
                        'merchant_id': merchant_id,
                        'merchant_name': merchant['name'],
                        'merchant_rating': merchant.get('rating', 0),
                        'product_price': data['price'],
                        'shipping_cost': data.get('shipping_cost', 0),
                        'total_price': data['price'] + data.get('shipping_cost', 0),
                        'in_stock': data.get('in_stock', True),
                        'condition': data.get('condition', 'new'),
                        'estimated_delivery': data.get('shipping_time_days', 7)
                    }
        except Exception as e:
            print(f"Error fetching from {merchant_id}: {e}")
            return None
    
    async def find_best_deal(
        self,
        product_ids: List[str],
        preferences: Dict = None
    ) -> Dict:
        """Find best combination of merchants for multiple products"""
        prefs = preferences or {
            'optimize_for': 'price',  # 'price' | 'speed' | 'rating'
            'max_merchants': 2,  # Bundle from fewer merchants
            'min_rating': 4.0
        }
        
        # Get prices for all products
        all_prices = {}
        for product_id in product_ids:
            prices = await self.compare_prices(product_id)
            # Filter by rating
            prices = [p for p in prices if p['merchant_rating'] >= prefs['min_rating']]
            all_prices[product_id] = prices
        
        # Find optimal combination
        if prefs['optimize_for'] == 'price':
            return self._optimize_for_price(all_prices, prefs['max_merchants'])
        elif prefs['optimize_for'] == 'speed':
            return self._optimize_for_speed(all_prices, prefs['max_merchants'])
        else:
            return self._optimize_for_rating(all_prices, prefs['max_merchants'])
    
    def _optimize_for_price(self, all_prices: Dict, max_merchants: int) -> Dict:
        """Find cheapest combination"""
        # Group by merchant
        merchant_carts = {}
        
        for product_id, prices in all_prices.items():
            if not prices:
                continue
            
            # Pick cheapest
            best = min(prices, key=lambda p: p['total_price'])
            merchant_id = best['merchant_id']
            
            if merchant_id not in merchant_carts:
                merchant_carts[merchant_id] = {
                    'merchant_id': merchant_id,
                    'merchant_name': best['merchant_name'],
                    'items': [],
                    'subtotal': 0,
                    'shipping': best['shipping_cost']
                }
            
            merchant_carts[merchant_id]['items'].append({
                'product_id': product_id,
                'price': best['product_price']
            })
            merchant_carts[merchant_id]['subtotal'] += best['product_price']
        
        # Calculate totals
        for cart in merchant_carts.values():
            cart['total'] = cart['subtotal'] + cart['shipping']
        
        return {
            'carts': list(merchant_carts.values()),
            'grand_total': sum(c['total'] for c in merchant_carts.values()),
            'merchant_count': len(merchant_carts)
        }
```

### Smart Order Routing

```python
# ap2-integration/src/shopping_agent/router.py

class OrderRouter:
    def __init__(self, db: Session, aggregator: PriceAggregator):
        self.db = db
        self.aggregator = aggregator
    
    async def route_order(
        self,
        user_id: int,
        items: List[Dict],
        preferences: Dict = None
    ) -> Dict:
        """Route order to optimal merchant(s)"""
        
        prefs = preferences or {
            'max_price': None,
            'max_delivery_days': 7,
            'preferred_merchants': [],
            'avoid_merchants': [],
            'min_merchant_rating': 4.0
        }
        
        # Get product IDs
        product_ids = [item['product_id'] for item in items]
        
        # Find best deal
        best_deal = await self.aggregator.find_best_deal(
            product_ids,
            {
                'optimize_for': 'price',
                'min_rating': prefs['min_merchant_rating']
            }
        )
        
        # Validate constraints
        if prefs['max_price'] and best_deal['grand_total'] > prefs['max_price']:
            raise ValueError(f"Best price ${best_deal['grand_total']} exceeds budget")
        
        # Create carts for each merchant
        cart_ids = []
        for cart_data in best_deal['carts']:
            cart = await self._create_cart_with_merchant(
                user_id=user_id,
                merchant_id=cart_data['merchant_id'],
                items=cart_data['items']
            )
            cart_ids.append(cart.id)
        
        return {
            'status': 'routed',
            'cart_ids': cart_ids,
            'total': best_deal['grand_total'],
            'merchant_count': len(cart_ids),
            'savings': self._calculate_savings(items, best_deal)
        }
    
    async def _create_cart_with_merchant(
        self,
        user_id: int,
        merchant_id: str,
        items: List[Dict]
    ) -> Cart:
        """Create cart associated with specific merchant"""
        cart = Cart(
            user_id=user_id,
            session_id=f"multi_{merchant_id}_{int(time.time())}",
            merchant_id=merchant_id,
            status="active"
        )
        self.db.add(cart)
        self.db.flush()
        
        for item in items:
            cart_item = CartItem(
                cart_id=cart.id,
                pokemon_numero=item['product_id'],
                quantity=item.get('quantity', 1),
                price_snapshot=item['price']
            )
            self.db.add(cart_item)
        
        self.db.commit()
        return cart
```

### Reputation System

```python
@app.post("/api/merchants/{merchant_id}/reviews")
async def submit_review(
    merchant_id: str,
    transaction_id: int,
    rating: int,
    comment: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit merchant review"""
    
    # Verify transaction belongs to user
    transaction = db.query(Transaction).filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check if already reviewed
    existing = db.query(MerchantReview).filter_by(transaction_id=transaction_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already reviewed")
    
    # Create review
    review = MerchantReview(
        merchant_id=merchant_id,
        user_id=current_user.id,
        transaction_id=transaction_id,
        rating=rating,
        comment=comment
    )
    db.add(review)
    
    # Update merchant rating
    avg_rating = db.query(func.avg(MerchantReview.rating)).filter_by(
        merchant_id=merchant_id
    ).scalar()
    
    total_reviews = db.query(func.count(MerchantReview.id)).filter_by(
        merchant_id=merchant_id
    ).scalar()
    
    merchant = db.query(Merchant).get(merchant_id)
    merchant.rating = float(avg_rating)
    merchant.total_reviews = total_reviews
    
    db.commit()
    
    return review

@app.get("/api/merchants/{merchant_id}/reviews")
async def get_reviews(
    merchant_id: str,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get merchant reviews"""
    reviews = db.query(MerchantReview).filter_by(
        merchant_id=merchant_id
    ).order_by(MerchantReview.created_at.desc()).limit(limit).offset(offset).all()
    
    return reviews
```

### Frontend UI

#### Price Comparison View

```html
<div class="price-comparison">
  <h3>Pikachu - Price Comparison</h3>
  
  <div class="comparison-grid">
    <div class="merchant-price best-deal">
      <span class="badge">🏆 Best Deal</span>
      <img src="pokemart-logo.png" />
      <h4>PokeMart</h4>
      <div class="rating">⭐⭐⭐⭐⭐ 4.8 (1,234 reviews)</div>
      <div class="price">
        <span class="product-price">$51.00</span>
        <span class="shipping">+ $5.00 shipping</span>
      </div>
      <div class="total">Total: $56.00</div>
      <div class="delivery">📦 Arrives in 3-5 days</div>
      <button>Add to Cart</button>
    </div>
    
    <div class="merchant-price">
      <img src="pokeshop-logo.png" />
      <h4>PokeShop</h4>
      <div class="rating">⭐⭐⭐⭐ 4.2 (567 reviews)</div>
      <div class="price">
        <span class="product-price">$53.00</span>
        <span class="shipping">FREE shipping</span>
      </div>
      <div class="total">Total: $53.00</div>
      <div class="delivery">📦 Arrives in 7-10 days</div>
      <button>Add to Cart</button>
    </div>
    
    <div class="merchant-price fastest">
      <span class="badge">⚡ Fastest</span>
      <img src="raremon-logo.png" />
      <h4>Rare Mon Store</h4>
      <div class="rating">⭐⭐⭐⭐⭐ 4.9 (89 reviews)</div>
      <div class="price">
        <span class="product-price">$55.00</span>
        <span class="shipping">+ $15.00 express</span>
      </div>
      <div class="total">Total: $70.00</div>
      <div class="delivery">📦 Arrives tomorrow</div>
      <button>Add to Cart</button>
    </div>
  </div>
  
  <div class="price-history">
    <h4>Price History (30 days)</h4>
    <canvas id="price-chart"></canvas>
  </div>
</div>
```

#### Multi-Merchant Checkout

```html
<div class="multi-merchant-checkout">
  <h2>Checkout Summary</h2>
  <p>Your order will be split across 2 merchants for best pricing:</p>
  
  <div class="merchant-cart">
    <h3>PokeMart</h3>
    <ul>
      <li>Pikachu × 1 - $51.00</li>
      <li>Charmander × 1 - $55.00</li>
    </ul>
    <div class="subtotal">Subtotal: $106.00</div>
    <div class="shipping">Shipping: $5.00</div>
    <div class="total">Total: $111.00</div>
  </div>
  
  <div class="merchant-cart">
    <h3>Rare Mon Store</h3>
    <ul>
      <li>Mewtwo × 1 - $200.00</li>
    </ul>
    <div class="subtotal">Subtotal: $200.00</div>
    <div class="shipping">Shipping: FREE</div>
    <div class="total">Total: $200.00</div>
  </div>
  
  <div class="grand-total">
    <strong>Grand Total: $311.00</strong>
    <span class="savings">You saved $15.00 vs. single merchant!</span>
  </div>
  
  <button>Complete Purchase from All Merchants</button>
</div>
```

## 📝 Criterios de Aceptación

- [ ] Price aggregation funciona con múltiples merchants
- [ ] Smart routing encuentra mejor deal
- [ ] Reputation system con reviews
- [ ] Price history tracking
- [ ] Multi-merchant checkout
- [ ] Parallel cart processing
- [ ] Savings calculation
- [ ] Frontend muestra comparison

## 🧪 Testing

```python
async def test_price_comparison():
    aggregator = PriceAggregator(registry_url)
    prices = await aggregator.compare_prices(product_id="25")
    
    assert len(prices) >= 2
    assert prices[0]['total_price'] <= prices[1]['total_price']  # Sorted

async def test_multi_merchant_routing():
    router = OrderRouter(db, aggregator)
    result = await router.route_order(
        user_id=1,
        items=[
            {'product_id': '25', 'quantity': 1},
            {'product_id': '150', 'quantity': 1}
        ]
    )
    
    assert result['status'] == 'routed'
    assert len(result['cart_ids']) >= 1

def test_reputation_update():
    submit_review(merchant_id="pokemart", rating=5, comment="Great!")
    merchant = db.query(Merchant).get("pokemart")
    assert merchant.rating >= 4.0
```

## ⏱️ Estimación

**Tiempo:** 3-4 semanas
**Prioridad:** Medium-High
**Complejidad:** Very High

## 🔗 Issues Relacionados

Depende de: #phase-6-1-discovery
Relacionado con: #phase-7-1-ai-recommendations

## 📚 Recursos

- [Price Comparison Algorithms](https://en.wikipedia.org/wiki/Price_comparison_service)
- [Marketplace Best Practices](https://stripe.com/docs/connect)
- [Multi-Merchant Checkout UX](https://baymard.com/blog/split-shipments)

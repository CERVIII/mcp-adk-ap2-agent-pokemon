---
title: "[Phase 3.3] Promotions & Discount System"
labels: enhancement, backend, pricing, phase-3
assignees: CERVIII
---

## 📋 Descripción

Sistema de promociones con cupones, descuentos por volumen, ofertas por tiempo limitado, y bundles.

## 🎯 Tipo de Issue

- [x] ✨ Nueva feature
- [x] 🗄️ Database
- [x] 💰 Pricing

## 📦 Fase del Roadmap

**Fase 3.3: Promociones y Descuentos**

## ✅ Tareas

### Database Schema
```sql
CREATE TABLE promotions (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) UNIQUE,  -- 'PIKACHU10', 'SUMMER2024'
    type VARCHAR(20),  -- 'percentage' | 'fixed' | 'bogo' | 'bundle'
    discount_value DECIMAL(10,2),  -- 10.00 for 10%, 5.00 for $5 off
    description TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    max_uses INTEGER,  -- null = unlimited
    current_uses INTEGER DEFAULT 0,
    min_purchase_amount DECIMAL(10,2),  -- null = no minimum
    applicable_categories JSON,  -- ['pokemon', 'item'] or null for all
    applicable_products JSON,  -- [1, 25, 150] or null for all
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP
);

CREATE TABLE user_promotions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    promotion_id INTEGER REFERENCES promotions(id),
    used_at TIMESTAMP,
    cart_id INTEGER REFERENCES carts(id),
    UNIQUE(user_id, promotion_id)  -- One use per user
);

CREATE TABLE bundles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),  -- 'Starter Pack', 'Evolution Bundle'
    description TEXT,
    price INTEGER,  -- Bundle price
    discount_percentage DECIMAL(5,2),  -- Auto-calculated
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT 1,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP
);

CREATE TABLE bundle_items (
    id INTEGER PRIMARY KEY,
    bundle_id INTEGER REFERENCES bundles(id),
    product_id VARCHAR(50),  -- Pokemon numero or item ID
    quantity INTEGER DEFAULT 1
);
```

### Promotion Types

#### 1. Percentage Discount
```json
{
  "code": "PIKACHU10",
  "type": "percentage",
  "discount_value": 10.0,  // 10% off
  "description": "10% off all Electric Pokemon",
  "applicable_categories": ["pokemon"],
  "applicable_products": [25, 26, 135, 172, 181],  // Electric types
  "min_purchase_amount": null,
  "max_uses": 100,
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z"
}
```

#### 2. Fixed Amount Discount
```json
{
  "code": "SAVE5",
  "type": "fixed",
  "discount_value": 5.0,  // $5 off
  "description": "$5 off orders over $50",
  "min_purchase_amount": 50.0,
  "max_uses": null,  // Unlimited
  "applicable_categories": null  // All products
}
```

#### 3. BOGO (Buy One Get One)
```json
{
  "code": "BOGO-PIKACHU",
  "type": "bogo",
  "discount_value": 50.0,  // 50% off second item
  "description": "Buy Pikachu, get second 50% off",
  "applicable_products": [25],
  "max_uses": 50
}
```

#### 4. Bundle Deal
```json
{
  "name": "Kanto Starter Pack",
  "description": "Get Bulbasaur, Charmander, Squirtle",
  "items": [
    {"product_id": 1, "quantity": 1},
    {"product_id": 4, "quantity": 1},
    {"product_id": 7, "quantity": 1}
  ],
  "individual_price": 165,  // $55 × 3
  "bundle_price": 120,
  "discount_percentage": 27.3  // Save $45 (27%)
}
```

### Backend Endpoints

#### Promotions
- [ ] `GET /api/promotions` → List active promotions
- [ ] `POST /api/promotions/validate` → Validate promo code
- [ ] `POST /api/cart/apply-promo` → Apply promo to cart
- [ ] `DELETE /api/cart/remove-promo` → Remove promo

#### Bundles
- [ ] `GET /api/bundles` → List active bundles
- [ ] `GET /api/bundles/{id}` → Bundle details
- [ ] `POST /api/cart/add-bundle` → Add entire bundle to cart

#### Admin Endpoints (Phase 7)
- [ ] `POST /api/admin/promotions` → Create promotion
- [ ] `PATCH /api/admin/promotions/{id}` → Update
- [ ] `DELETE /api/admin/promotions/{id}` → Deactivate

### Cart Discount Logic
```python
class CartCalculator:
    def calculate_total(self, cart: Cart, promo_code: str = None) -> dict:
        subtotal = sum(item.price * item.quantity for item in cart.items)
        
        discount = 0
        applied_promo = None
        
        if promo_code:
            promo = validate_promo_code(promo_code, cart.user_id)
            if promo:
                discount = self.calculate_discount(promo, cart)
                applied_promo = promo
        
        total = max(0, subtotal - discount)
        
        return {
            "subtotal": subtotal,
            "discount": discount,
            "promo_code": applied_promo.code if applied_promo else None,
            "total": total,
            "savings_percentage": (discount / subtotal * 100) if subtotal > 0 else 0
        }
    
    def calculate_discount(self, promo: Promotion, cart: Cart) -> float:
        if promo.type == "percentage":
            applicable_items = self.get_applicable_items(promo, cart)
            applicable_total = sum(item.price * item.quantity for item in applicable_items)
            return applicable_total * (promo.discount_value / 100)
        
        elif promo.type == "fixed":
            subtotal = sum(item.price * item.quantity for item in cart.items)
            if subtotal >= (promo.min_purchase_amount or 0):
                return promo.discount_value
            return 0
        
        elif promo.type == "bogo":
            # Logic for BOGO
            applicable_items = self.get_applicable_items(promo, cart)
            total_qty = sum(item.quantity for item in applicable_items)
            free_items = total_qty // 2
            return free_items * applicable_items[0].price * (promo.discount_value / 100)
        
        return 0
```

### Frontend UI

#### Promo Code Input
```html
<div class="promo-section">
  <input 
    type="text" 
    id="promo-code" 
    placeholder="Enter promo code"
    maxlength="50"
  />
  <button onclick="applyPromo()">Apply</button>
  
  <div id="promo-feedback" class="success">
    ✅ Promo code PIKACHU10 applied! Saved $5.10 (10%)
  </div>
</div>
```

#### Cart Summary with Discount
```
Subtotal:        $51.00
Discount (SAVE5): -$5.00
─────────────────────────
Total:           $46.00
You saved 10%! 🎉
```

#### Bundle Cards
```html
<div class="bundle-card featured">
  <div class="badge">SAVE 27%</div>
  <h3>Kanto Starter Pack</h3>
  <div class="bundle-items">
    <img src="bulbasaur.png" />
    <img src="charmander.png" />
    <img src="squirtle.png" />
  </div>
  <div class="pricing">
    <span class="original">$165</span>
    <span class="bundle-price">$120</span>
  </div>
  <button>Add Bundle to Cart</button>
</div>
```

#### Active Promotions Banner
```html
<div class="promo-banner">
  🎉 Limited Time: Use code <code>SUMMER20</code> for 20% off! Ends in 2 days.
</div>
```

### Validation Logic
```python
def validate_promo_code(code: str, user_id: int, cart: Cart) -> Promotion | None:
    promo = db.query(Promotion).filter_by(code=code, is_active=True).first()
    
    if not promo:
        raise PromoError("Invalid promo code")
    
    # Check date range
    now = datetime.now(timezone.utc)
    if promo.start_date and now < promo.start_date:
        raise PromoError("Promo not started yet")
    if promo.end_date and now > promo.end_date:
        raise PromoError("Promo expired")
    
    # Check usage limits
    if promo.max_uses and promo.current_uses >= promo.max_uses:
        raise PromoError("Promo code fully redeemed")
    
    # Check per-user usage
    user_usage = db.query(UserPromotion).filter_by(
        user_id=user_id, 
        promotion_id=promo.id
    ).first()
    if user_usage:
        raise PromoError("You've already used this promo")
    
    # Check minimum purchase
    subtotal = sum(item.price * item.quantity for item in cart.items)
    if promo.min_purchase_amount and subtotal < promo.min_purchase_amount:
        raise PromoError(f"Minimum purchase ${promo.min_purchase_amount} required")
    
    return promo
```

### Notification System
- [ ] Email cuando nuevo promo disponible
- [ ] Push notification: "Your favorite Pokemon on sale!"
- [ ] Banner en homepage con promos activas

## 📝 Criterios de Aceptación

- [ ] Users pueden aplicar promo codes
- [ ] Discount se calcula correctamente
- [ ] Validation previene abuso
- [ ] Bundles se muestran en UI
- [ ] Add bundle to cart funciona
- [ ] One-time use per user enforced
- [ ] Expired promos no aplican

## 🎨 Design

**Promo Badge Colors:**
- Percentage discount: Blue
- Fixed discount: Green
- BOGO: Orange
- Bundle: Purple

**Animation:**
- Sparkle effect cuando discount applied
- Countdown timer para limited-time promos

## ⏱️ Estimación

**Tiempo:** 1.5-2 semanas
**Prioridad:** Medium
**Complejidad:** Medium (business logic)

## 🔗 Issues Relacionados

Relacionado con: #phase-3-2-product-categories (bundle items)
Prerequisito para: #phase-7-1-ai-recommendations (personalized promos)

## 📚 Recursos

- [E-commerce Discount Strategies](https://www.shopify.com/blog/discount-strategy)
- [Promo Code Best Practices](https://www.optimizely.com/insights/blog/promo-codes/)

## 🧪 Testing

```python
def test_percentage_discount():
    cart = create_cart(items=[{"id": 25, "qty": 1, "price": 51}])
    total = calculate_total(cart, promo_code="PIKACHU10")
    assert total["discount"] == 5.10
    assert total["total"] == 45.90

def test_min_purchase_requirement():
    cart = create_cart(total=30)
    with pytest.raises(PromoError, match="Minimum purchase"):
        validate_promo_code("SAVE5", user_id=1, cart=cart)

def test_one_use_per_user():
    use_promo("FIRST10", user_id=1)
    with pytest.raises(PromoError, match="already used"):
        use_promo("FIRST10", user_id=1)

def test_bogo_calculation():
    cart = create_cart(items=[
        {"id": 25, "qty": 3, "price": 51}  # Buy 3 Pikachu
    ])
    total = calculate_total(cart, promo_code="BOGO-PIKACHU")
    # Should get 1 free (50% off on second)
    assert total["discount"] == 25.50  # 51 × 50%
```

## 💡 Future Enhancements

- [ ] Tiered discounts: "Spend $100, get 10% off; $200, get 20% off"
- [ ] Referral codes: "Invite friend, both get $10"
- [ ] Seasonal sales: Automatic discounts during events
- [ ] Flash sales: 24-hour mega discounts
- [ ] Loyalty program integration (Phase 7.3)

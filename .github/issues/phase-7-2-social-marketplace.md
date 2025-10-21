---
title: "[Phase 7.2] Social Marketplace & P2P Trading"
labels: enhancement, social, trading, phase-7
assignees: CERVIII
---

## 📋 Descripción

Marketplace social: users pueden vender Pokemon a otros users (P2P), sistema de trading, reviews/ratings, wish lists públicas, y leaderboards.

## 🎯 Tipo de Issue

- [x] 🤝 Social Features
- [x] ✨ Nueva feature
- [x] 💱 Trading

## 📦 Fase del Roadmap

**Fase 7.2: Marketplace Social**

## ✅ Tareas

### Database Schema

```sql
CREATE TABLE user_inventory (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pokemon_numero INTEGER,
    quantity INTEGER DEFAULT 1,
    condition VARCHAR(20) DEFAULT 'new',  -- 'new' | 'used' | 'mint'
    obtained_from VARCHAR(50),  -- 'purchase' | 'trade' | 'gift'
    obtained_at TIMESTAMP,
    
    INDEX idx_user_pokemon (user_id, pokemon_numero)
);

CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER REFERENCES users(id),
    pokemon_numero INTEGER,
    quantity INTEGER,
    price INTEGER,  -- in cents
    condition VARCHAR(20),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',  -- 'active' | 'sold' | 'cancelled' | 'expired'
    views INTEGER DEFAULT 0,
    favorites INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    INDEX idx_pokemon_price (pokemon_numero, price),
    INDEX idx_seller_status (seller_id, status)
);

CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    initiator_id INTEGER REFERENCES users(id),
    recipient_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending' | 'accepted' | 'declined' | 'completed' | 'cancelled'
    
    -- Initiator offers
    initiator_offers JSON,  -- [{"pokemon_numero": 25, "quantity": 1}]
    
    -- Recipient wants
    recipient_offers JSON,
    
    message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    INDEX idx_recipient_status (recipient_id, status)
);

CREATE TABLE user_reviews (
    id INTEGER PRIMARY KEY,
    reviewer_id INTEGER REFERENCES users(id),
    reviewee_id INTEGER REFERENCES users(id),
    trade_id INTEGER REFERENCES trades(id),
    listing_id INTEGER REFERENCES listings(id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP,
    
    UNIQUE(reviewer_id, reviewee_id, trade_id),
    UNIQUE(reviewer_id, listing_id)
);

CREATE TABLE user_following (
    follower_id INTEGER REFERENCES users(id),
    following_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    
    PRIMARY KEY (follower_id, following_id)
);

CREATE TABLE public_wishlists (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pokemon_numero INTEGER,
    max_price INTEGER,  -- Willing to pay up to
    priority INTEGER,
    notes TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    
    INDEX idx_pokemon_public (pokemon_numero, is_public)
);

CREATE TABLE leaderboards (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    metric VARCHAR(50),  -- 'total_trades' | 'collection_value' | 'rare_pokemon' | 'reputation'
    score INTEGER,
    rank INTEGER,
    updated_at TIMESTAMP,
    
    INDEX idx_metric_rank (metric, rank)
);
```

### P2P Listing System

```python
# ap2-integration/src/marketplace/listings.py

@app.post("/api/listings")
async def create_listing(
    pokemon_numero: int,
    quantity: int,
    price: int,
    condition: str,
    description: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a listing to sell Pokemon"""
    
    # Check if user owns this Pokemon
    inventory = db.query(UserInventory).filter_by(
        user_id=current_user.id,
        pokemon_numero=pokemon_numero
    ).first()
    
    if not inventory or inventory.quantity < quantity:
        raise HTTPException(status_code=400, detail="Insufficient inventory")
    
    # Create listing
    listing = Listing(
        seller_id=current_user.id,
        pokemon_numero=pokemon_numero,
        quantity=quantity,
        price=price,
        condition=condition,
        description=description,
        status="active",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    
    db.add(listing)
    
    # Reserve inventory
    inventory.quantity -= quantity
    
    db.commit()
    
    return listing

@app.get("/api/listings")
async def browse_listings(
    pokemon_numero: int = None,
    min_price: int = None,
    max_price: int = None,
    condition: str = None,
    sort: str = "price_asc",
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Browse P2P listings"""
    
    query = db.query(Listing).filter_by(status="active")
    
    if pokemon_numero:
        query = query.filter_by(pokemon_numero=pokemon_numero)
    
    if min_price:
        query = query.filter(Listing.price >= min_price)
    
    if max_price:
        query = query.filter(Listing.price <= max_price)
    
    if condition:
        query = query.filter_by(condition=condition)
    
    # Sorting
    if sort == "price_asc":
        query = query.order_by(Listing.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Listing.price.desc())
    elif sort == "newest":
        query = query.order_by(Listing.created_at.desc())
    elif sort == "popular":
        query = query.order_by(Listing.views.desc())
    
    listings = query.limit(limit).offset(offset).all()
    
    return listings

@app.post("/api/listings/{listing_id}/purchase")
async def purchase_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase a P2P listing"""
    
    listing = db.query(Listing).get(listing_id)
    
    if not listing or listing.status != "active":
        raise HTTPException(status_code=404, detail="Listing not available")
    
    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot buy your own listing")
    
    # Process payment
    payment = await process_p2p_payment(
        buyer_id=current_user.id,
        seller_id=listing.seller_id,
        amount=listing.price
    )
    
    # Transfer Pokemon to buyer
    buyer_inventory = db.query(UserInventory).filter_by(
        user_id=current_user.id,
        pokemon_numero=listing.pokemon_numero
    ).first()
    
    if buyer_inventory:
        buyer_inventory.quantity += listing.quantity
    else:
        buyer_inventory = UserInventory(
            user_id=current_user.id,
            pokemon_numero=listing.pokemon_numero,
            quantity=listing.quantity,
            condition=listing.condition,
            obtained_from='purchase'
        )
        db.add(buyer_inventory)
    
    # Mark listing as sold
    listing.status = "sold"
    
    db.commit()
    
    # Send notifications
    await notify_seller(listing.seller_id, f"Your {listing.pokemon_name} sold for ${listing.price/100}!")
    
    return {"status": "purchased", "payment_id": payment.id}
```

### Trading System

```python
@app.post("/api/trades")
async def initiate_trade(
    recipient_id: int,
    initiator_offers: List[Dict],  # [{"pokemon_numero": 25, "quantity": 1}]
    recipient_wants: List[Dict],
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a Pokemon trade"""
    
    # Validate initiator owns offered Pokemon
    for offer in initiator_offers:
        inventory = db.query(UserInventory).filter_by(
            user_id=current_user.id,
            pokemon_numero=offer['pokemon_numero']
        ).first()
        
        if not inventory or inventory.quantity < offer['quantity']:
            raise HTTPException(status_code=400, detail=f"Insufficient {offer['pokemon_numero']}")
    
    # Create trade
    trade = Trade(
        initiator_id=current_user.id,
        recipient_id=recipient_id,
        initiator_offers=initiator_offers,
        recipient_offers=recipient_wants,
        message=message,
        status="pending"
    )
    
    db.add(trade)
    db.commit()
    
    # Notify recipient
    await notify_user(recipient_id, f"New trade offer from {current_user.name}!")
    
    return trade

@app.post("/api/trades/{trade_id}/accept")
async def accept_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a trade offer"""
    
    trade = db.query(Trade).get(trade_id)
    
    if not trade or trade.recipient_id != current_user.id:
        raise HTTPException(status_code=404)
    
    if trade.status != "pending":
        raise HTTPException(status_code=400, detail="Trade already processed")
    
    # Validate recipient owns wanted Pokemon
    for offer in trade.recipient_offers:
        inventory = db.query(UserInventory).filter_by(
            user_id=current_user.id,
            pokemon_numero=offer['pokemon_numero']
        ).first()
        
        if not inventory or inventory.quantity < offer['quantity']:
            raise HTTPException(status_code=400, detail="Insufficient Pokemon")
    
    # Execute trade
    # Transfer initiator's Pokemon to recipient
    for offer in trade.initiator_offers:
        # Subtract from initiator
        initiator_inv = db.query(UserInventory).filter_by(
            user_id=trade.initiator_id,
            pokemon_numero=offer['pokemon_numero']
        ).first()
        initiator_inv.quantity -= offer['quantity']
        
        # Add to recipient
        recipient_inv = db.query(UserInventory).filter_by(
            user_id=current_user.id,
            pokemon_numero=offer['pokemon_numero']
        ).first()
        
        if recipient_inv:
            recipient_inv.quantity += offer['quantity']
        else:
            db.add(UserInventory(
                user_id=current_user.id,
                pokemon_numero=offer['pokemon_numero'],
                quantity=offer['quantity'],
                obtained_from='trade'
            ))
    
    # Transfer recipient's Pokemon to initiator
    for offer in trade.recipient_offers:
        # Subtract from recipient
        recipient_inv = db.query(UserInventory).filter_by(
            user_id=current_user.id,
            pokemon_numero=offer['pokemon_numero']
        ).first()
        recipient_inv.quantity -= offer['quantity']
        
        # Add to initiator
        initiator_inv = db.query(UserInventory).filter_by(
            user_id=trade.initiator_id,
            pokemon_numero=offer['pokemon_numero']
        ).first()
        
        if initiator_inv:
            initiator_inv.quantity += offer['quantity']
        else:
            db.add(UserInventory(
                user_id=trade.initiator_id,
                pokemon_numero=offer['pokemon_numero'],
                quantity=offer['quantity'],
                obtained_from='trade'
            ))
    
    # Mark trade complete
    trade.status = "completed"
    trade.completed_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Notify initiator
    await notify_user(trade.initiator_id, "Trade accepted and completed!")
    
    return {"status": "completed"}
```

### User Reputation & Reviews

```python
@app.post("/api/users/{user_id}/reviews")
async def submit_user_review(
    user_id: int,
    trade_id: int,
    rating: int,
    comment: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Review another user after a trade"""
    
    # Verify trade exists and user participated
    trade = db.query(Trade).get(trade_id)
    
    if not trade or (trade.initiator_id != current_user.id and trade.recipient_id != current_user.id):
        raise HTTPException(status_code=404)
    
    if trade.status != "completed":
        raise HTTPException(status_code=400, detail="Trade not completed")
    
    # Create review
    review = UserReview(
        reviewer_id=current_user.id,
        reviewee_id=user_id,
        trade_id=trade_id,
        rating=rating,
        comment=comment
    )
    
    db.add(review)
    
    # Update reviewee's rating
    avg_rating = db.query(func.avg(UserReview.rating)).filter_by(
        reviewee_id=user_id
    ).scalar()
    
    user = db.query(User).get(user_id)
    user.rating = float(avg_rating)
    
    db.commit()
    
    return review
```

### Leaderboards

```python
@app.get("/api/leaderboards/{metric}")
async def get_leaderboard(
    metric: str,  # 'total_trades' | 'collection_value' | 'rare_pokemon' | 'reputation'
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get leaderboard for specific metric"""
    
    leaderboard = db.query(Leaderboard).filter_by(
        metric=metric
    ).order_by(Leaderboard.rank.asc()).limit(limit).all()
    
    return leaderboard

def update_leaderboards():
    """Background job to update leaderboards"""
    
    # Total trades
    trade_leaders = db.query(
        Trade.initiator_id.label('user_id'),
        func.count(Trade.id).label('total_trades')
    ).filter_by(status='completed').group_by(Trade.initiator_id).all()
    
    for i, (user_id, total) in enumerate(trade_leaders):
        update_leaderboard_entry(user_id, 'total_trades', total, i+1)
    
    # Collection value
    # ... similar logic
    
    # Reputation
    rep_leaders = db.query(
        User.id,
        User.rating
    ).filter(User.rating > 0).order_by(User.rating.desc()).all()
    
    for i, (user_id, rating) in enumerate(rep_leaders):
        update_leaderboard_entry(user_id, 'reputation', int(rating * 100), i+1)
```

### Frontend UI

```html
<!-- P2P Marketplace -->
<div class="p2p-marketplace">
  <h2>Community Marketplace</h2>
  
  <div class="filters">
    <input type="text" placeholder="Search Pokemon..." />
    <select name="condition">
      <option value="">All Conditions</option>
      <option value="mint">Mint</option>
      <option value="new">New</option>
      <option value="used">Used</option>
    </select>
    <select name="sort">
      <option value="price_asc">Price: Low to High</option>
      <option value="price_desc">Price: High to Low</option>
      <option value="newest">Newest First</option>
      <option value="popular">Most Popular</option>
    </select>
  </div>
  
  <div class="listings-grid">
    <div class="listing-card">
      <img src="pikachu.png" />
      <h4>Pikachu</h4>
      <div class="condition-badge mint">Mint Condition</div>
      <div class="price">$65.00</div>
      <div class="seller">
        <img src="avatar.png" class="avatar-small" />
        <span>Ash K.</span>
        <span class="rating">⭐⭐⭐⭐⭐ 4.9</span>
      </div>
      <p class="description">Caught personally, level 50, perfect IVs!</p>
      <div class="listing-meta">
        <span>👁️ 127 views</span>
        <span>❤️ 23 favorites</span>
      </div>
      <button onclick="purchaseListing(123)">Buy Now</button>
      <button onclick="makeOffer(123)" class="secondary">Make Offer</button>
    </div>
  </div>
</div>

<!-- Trade System -->
<div class="trade-modal" id="trade-modal">
  <h3>Initiate Trade with @MistyW</h3>
  
  <div class="trade-sides">
    <div class="your-offer">
      <h4>You Offer</h4>
      <div class="pokemon-selector">
        <button onclick="selectFromInventory()">+ Add Pokemon</button>
      </div>
      <div id="your-pokemon-list"></div>
    </div>
    
    <div class="trade-arrow">⇄</div>
    
    <div class="their-offer">
      <h4>You Want</h4>
      <div class="pokemon-selector">
        <button onclick="selectFromWishlist()">+ Add Pokemon</button>
      </div>
      <div id="their-pokemon-list"></div>
    </div>
  </div>
  
  <textarea placeholder="Message (optional)..."></textarea>
  
  <button onclick="submitTrade()">Send Trade Offer</button>
</div>

<!-- User Profile with Collection -->
<div class="user-profile">
  <div class="profile-header">
    <img src="avatar.png" class="avatar-large" />
    <div class="profile-info">
      <h2>Ash Ketchum</h2>
      <div class="reputation">
        ⭐⭐⭐⭐⭐ 4.9 (142 reviews)
      </div>
      <div class="stats">
        <span>🔁 87 trades</span>
        <span>💰 $2,340 total value</span>
        <span>🏆 #12 on leaderboard</span>
      </div>
      <button onclick="followUser()">+ Follow</button>
      <button onclick="initiateTradeWith()">📩 Trade</button>
    </div>
  </div>
  
  <div class="collection-display">
    <h3>Pokemon Collection (151/151)</h3>
    <div class="pokemon-grid">
      <!-- User's Pokemon with badges -->
    </div>
  </div>
  
  <div class="public-wishlist">
    <h3>Public Wishlist</h3>
    <ul>
      <li>Shiny Charizard - Up to $250</li>
      <li>Mewtwo (Mint) - Up to $220</li>
    </ul>
  </div>
</div>

<!-- Leaderboard -->
<div class="leaderboard">
  <h2>Top Traders</h2>
  <table>
    <thead>
      <tr>
        <th>Rank</th>
        <th>User</th>
        <th>Total Trades</th>
        <th>Rating</th>
      </tr>
    </thead>
    <tbody>
      <tr class="rank-1">
        <td>🥇 1</td>
        <td>
          <img src="avatar1.png" class="avatar-tiny" />
          ProfessorOak
        </td>
        <td>523</td>
        <td>⭐⭐⭐⭐⭐ 5.0</td>
      </tr>
      <!-- ... more rows -->
    </tbody>
  </table>
</div>
```

## 📝 Criterios de Aceptación

- [ ] Users pueden listar Pokemon for sale
- [ ] P2P marketplace con search/filters
- [ ] Trading system funciona
- [ ] User reviews y ratings
- [ ] Inventory management
- [ ] Leaderboards con rankings
- [ ] Public wishlists
- [ ] Following system
- [ ] Escrow for high-value trades

## 🧪 Testing

```python
def test_create_listing():
    # User owns Pokemon
    add_to_inventory(user_id=1, pokemon_numero=25, quantity=2)
    
    # Create listing
    listing = create_listing(user_id=1, pokemon_numero=25, price=6500)
    assert listing.status == "active"

def test_trade_execution():
    # Setup
    add_to_inventory(user_id=1, pokemon_numero=25, quantity=1)  # Pikachu
    add_to_inventory(user_id=2, pokemon_numero=4, quantity=1)   # Charmander
    
    # Initiate trade
    trade = initiate_trade(
        initiator_id=1,
        recipient_id=2,
        initiator_offers=[{"pokemon_numero": 25, "quantity": 1}],
        recipient_offers=[{"pokemon_numero": 4, "quantity": 1}]
    )
    
    # Accept
    accept_trade(trade_id=trade.id, user_id=2)
    
    # Verify
    assert get_inventory(user_id=1, pokemon_numero=4).quantity == 1
    assert get_inventory(user_id=2, pokemon_numero=25).quantity == 1
```

## ⏱️ Estimación

**Tiempo:** 4-5 semanas
**Prioridad:** Medium
**Complejidad:** Very High

## 🔗 Issues Relacionados

Relacionado con: #phase-7-3-gamification

## 📚 Recursos

- [P2P Marketplace Design](https://stripe.com/docs/connect)
- [Escrow Services](https://www.escrow.com/how-it-works)
- [Trading Card Game Economics](https://www.tcgplayer.com/)

## 🚨 Security & Trust

- Escrow system for high-value trades (>$100)
- Dispute resolution process
- Fraud detection (unusual trading patterns)
- User verification badges
- Report/block functionality
- Trade history transparency

---
title: "[Phase 7.3] Gamification & Loyalty Program"
labels: enhancement, gamification, engagement, phase-7
assignees: CERVIII
---

## 📋 Descripción

Sistema de gamificación completo: achievements/badges, loyalty points, daily challenges, streak tracking, referral program, y rewards shop.

## 🎯 Tipo de Issue

- [x] 🎮 Gamification
- [x] ✨ Nueva feature
- [x] 🎁 Rewards

## 📦 Fase del Roadmap

**Fase 7.3: Gamificación y Loyalty**

## ✅ Tareas

### Database Schema

```sql
CREATE TABLE achievements (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    icon VARCHAR(500),
    category VARCHAR(50),  -- 'collector' | 'trader' | 'spender' | 'social'
    rarity VARCHAR(20),  -- 'common' | 'rare' | 'epic' | 'legendary'
    points INTEGER,
    requirement_type VARCHAR(50),  -- 'purchase_count' | 'total_spent' | 'collection_size'
    requirement_value INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE user_achievements (
    user_id INTEGER REFERENCES users(id),
    achievement_id VARCHAR(100) REFERENCES achievements(id),
    unlocked_at TIMESTAMP,
    progress INTEGER DEFAULT 0,  -- For multi-step achievements
    
    PRIMARY KEY (user_id, achievement_id)
);

CREATE TABLE loyalty_points (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    total_points INTEGER DEFAULT 0,
    available_points INTEGER DEFAULT 0,
    lifetime_points INTEGER DEFAULT 0,
    tier VARCHAR(20) DEFAULT 'bronze',  -- 'bronze' | 'silver' | 'gold' | 'platinum' | 'diamond'
    updated_at TIMESTAMP
);

CREATE TABLE point_transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount INTEGER,  -- Positive = earned, Negative = spent
    type VARCHAR(50),  -- 'purchase' | 'daily_login' | 'challenge' | 'redemption' | 'referral'
    reference_id INTEGER,  -- Transaction ID, challenge ID, etc.
    description TEXT,
    created_at TIMESTAMP,
    
    INDEX idx_user_date (user_id, created_at)
);

CREATE TABLE challenges (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    type VARCHAR(50),  -- 'daily' | 'weekly' | 'monthly' | 'special'
    objective VARCHAR(100),  -- 'purchase_3_pokemon' | 'spend_100_dollars' | 'complete_trade'
    target_value INTEGER,
    reward_points INTEGER,
    reward_badge VARCHAR(100),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_challenges (
    user_id INTEGER REFERENCES users(id),
    challenge_id INTEGER REFERENCES challenges(id),
    progress INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    
    PRIMARY KEY (user_id, challenge_id)
);

CREATE TABLE daily_streaks (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_login_date DATE,
    total_logins INTEGER DEFAULT 0
);

CREATE TABLE referrals (
    id INTEGER PRIMARY KEY,
    referrer_id INTEGER REFERENCES users(id),
    referred_id INTEGER REFERENCES users(id),
    referral_code VARCHAR(20) UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending' | 'completed'
    reward_points INTEGER DEFAULT 100,
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    INDEX idx_referrer (referrer_id)
);

CREATE TABLE rewards_shop (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    type VARCHAR(50),  -- 'discount' | 'free_pokemon' | 'badge' | 'cosmetic'
    cost_points INTEGER,
    value_usd DECIMAL(10,2),
    stock_quantity INTEGER,  -- null = unlimited
    available_from TIMESTAMP,
    available_until TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE reward_redemptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    reward_id INTEGER REFERENCES rewards_shop(id),
    points_spent INTEGER,
    redeemed_at TIMESTAMP,
    applied_at TIMESTAMP,  -- When discount/reward was used
    
    INDEX idx_user_date (user_id, redeemed_at)
);
```

### Loyalty Points System

```python
# ap2-integration/src/gamification/loyalty.py

class LoyaltySystem:
    # Points earning rates
    POINTS_PER_DOLLAR = 10  # 10 points per $1 spent
    DAILY_LOGIN_POINTS = 5
    CHALLENGE_COMPLETION_BASE = 50
    REFERRAL_POINTS = 100
    REVIEW_POINTS = 20
    
    # Tier thresholds
    TIERS = {
        'bronze': 0,
        'silver': 1000,
        'gold': 5000,
        'platinum': 15000,
        'diamond': 50000
    }
    
    # Tier benefits (multiplier)
    TIER_MULTIPLIERS = {
        'bronze': 1.0,
        'silver': 1.2,
        'gold': 1.5,
        'platinum': 2.0,
        'diamond': 3.0
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def award_points(
        self,
        user_id: int,
        amount: int,
        type: str,
        description: str,
        reference_id: int = None
    ):
        """Award loyalty points to user"""
        
        # Get user's loyalty account
        loyalty = self.db.query(LoyaltyPoints).filter_by(user_id=user_id).first()
        if not loyalty:
            loyalty = LoyaltyPoints(user_id=user_id)
            self.db.add(loyalty)
        
        # Apply tier multiplier
        multiplier = self.TIER_MULTIPLIERS.get(loyalty.tier, 1.0)
        final_amount = int(amount * multiplier)
        
        # Update points
        loyalty.total_points += final_amount
        loyalty.available_points += final_amount
        loyalty.lifetime_points += final_amount
        
        # Check for tier upgrade
        new_tier = self._calculate_tier(loyalty.lifetime_points)
        if new_tier != loyalty.tier:
            old_tier = loyalty.tier
            loyalty.tier = new_tier
            
            # Award tier upgrade badge
            self._award_achievement(user_id, f"tier_{new_tier}")
            
            # Notify user
            notify_user(user_id, f"🎉 Tier upgraded: {old_tier.upper()} → {new_tier.upper()}!")
        
        # Record transaction
        transaction = PointTransaction(
            user_id=user_id,
            amount=final_amount,
            type=type,
            reference_id=reference_id,
            description=description
        )
        self.db.add(transaction)
        self.db.commit()
        
        return final_amount
    
    def award_purchase_points(self, transaction: Transaction):
        """Award points based on purchase amount"""
        points = int(transaction.total * self.POINTS_PER_DOLLAR)
        
        self.award_points(
            user_id=transaction.user_id,
            amount=points,
            type='purchase',
            description=f"Purchase #{transaction.id}",
            reference_id=transaction.id
        )
    
    def award_daily_login(self, user_id: int):
        """Award points for daily login"""
        today = datetime.now(timezone.utc).date()
        
        streak = self.db.query(DailyStreak).filter_by(user_id=user_id).first()
        if not streak:
            streak = DailyStreak(user_id=user_id, last_login_date=today)
            self.db.add(streak)
        
        # Check if already logged in today
        if streak.last_login_date == today:
            return 0
        
        # Update streak
        if streak.last_login_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
        
        streak.last_login_date = today
        streak.total_logins += 1
        
        # Update longest streak
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
        
        # Award points (bonus for streak)
        points = self.DAILY_LOGIN_POINTS + (streak.current_streak // 7) * 5  # +5 for each week
        
        self.award_points(
            user_id=user_id,
            amount=points,
            type='daily_login',
            description=f"Daily login (Streak: {streak.current_streak})"
        )
        
        # Achievement checks
        if streak.current_streak == 7:
            self._award_achievement(user_id, 'streak_7')
        elif streak.current_streak == 30:
            self._award_achievement(user_id, 'streak_30')
        elif streak.current_streak == 100:
            self._award_achievement(user_id, 'streak_100')
        
        self.db.commit()
        
        return points
    
    def redeem_points(
        self,
        user_id: int,
        reward_id: int
    ) -> dict:
        """Redeem points for reward"""
        
        loyalty = self.db.query(LoyaltyPoints).filter_by(user_id=user_id).first()
        reward = self.db.query(RewardsShop).get(reward_id)
        
        if not reward or not reward.is_active:
            raise ValueError("Reward not available")
        
        if loyalty.available_points < reward.cost_points:
            raise ValueError("Insufficient points")
        
        # Check stock
        if reward.stock_quantity is not None and reward.stock_quantity <= 0:
            raise ValueError("Out of stock")
        
        # Deduct points
        loyalty.available_points -= reward.cost_points
        
        # Record transaction
        transaction = PointTransaction(
            user_id=user_id,
            amount=-reward.cost_points,
            type='redemption',
            reference_id=reward_id,
            description=f"Redeemed: {reward.name}"
        )
        self.db.add(transaction)
        
        # Record redemption
        redemption = RewardRedemption(
            user_id=user_id,
            reward_id=reward_id,
            points_spent=reward.cost_points
        )
        self.db.add(redemption)
        
        # Update stock
        if reward.stock_quantity is not None:
            reward.stock_quantity -= 1
        
        self.db.commit()
        
        # Apply reward
        return self._apply_reward(user_id, reward)
    
    def _calculate_tier(self, lifetime_points: int) -> str:
        """Calculate tier based on lifetime points"""
        for tier in ['diamond', 'platinum', 'gold', 'silver', 'bronze']:
            if lifetime_points >= self.TIERS[tier]:
                return tier
        return 'bronze'
    
    def _apply_reward(self, user_id: int, reward) -> dict:
        """Apply redeemed reward"""
        if reward.type == 'discount':
            # Create discount code
            code = generate_promo_code()
            create_promotion(
                code=code,
                type='percentage',
                discount_value=reward.value_usd,
                max_uses=1,
                user_id=user_id
            )
            return {'type': 'discount_code', 'code': code}
        
        elif reward.type == 'free_pokemon':
            # Add to inventory
            add_to_inventory(user_id, reward.pokemon_numero, quantity=1)
            return {'type': 'pokemon', 'pokemon_id': reward.pokemon_numero}
        
        elif reward.type == 'badge':
            # Award badge
            self._award_achievement(user_id, reward.achievement_id)
            return {'type': 'badge', 'achievement_id': reward.achievement_id}
        
        return {'type': 'unknown'}
```

### Achievement System

```python
class AchievementSystem:
    def __init__(self, db: Session):
        self.db = db
    
    def check_achievements(self, user_id: int, event_type: str, data: dict):
        """Check if user unlocked any achievements"""
        
        unlocked = []
        
        if event_type == 'purchase':
            # Check purchase-related achievements
            total_purchases = self.db.query(func.count(Transaction.id)).filter_by(
                user_id=user_id
            ).scalar()
            
            if total_purchases == 1:
                unlocked.append(self._unlock('first_purchase', user_id))
            elif total_purchases == 10:
                unlocked.append(self._unlock('10_purchases', user_id))
            elif total_purchases == 100:
                unlocked.append(self._unlock('100_purchases', user_id))
            
            # Check spending achievements
            total_spent = self.db.query(func.sum(Transaction.total)).filter_by(
                user_id=user_id
            ).scalar() or 0
            
            if total_spent >= 100:
                unlocked.append(self._unlock('big_spender_100', user_id))
            elif total_spent >= 1000:
                unlocked.append(self._unlock('big_spender_1000', user_id))
        
        elif event_type == 'collection':
            # Check collection achievements
            collection_size = self.db.query(func.count(UserInventory.id)).filter_by(
                user_id=user_id
            ).scalar()
            
            if collection_size >= 10:
                unlocked.append(self._unlock('collector_10', user_id))
            elif collection_size >= 50:
                unlocked.append(self._unlock('collector_50', user_id))
            elif collection_size == 151:
                unlocked.append(self._unlock('gotta_catch_em_all', user_id))
        
        elif event_type == 'trade':
            total_trades = self.db.query(func.count(Trade.id)).filter(
                (Trade.initiator_id == user_id) | (Trade.recipient_id == user_id),
                Trade.status == 'completed'
            ).scalar()
            
            if total_trades == 1:
                unlocked.append(self._unlock('first_trade', user_id))
            elif total_trades == 50:
                unlocked.append(self._unlock('master_trader', user_id))
        
        # Notify user
        for achievement in unlocked:
            if achievement:
                notify_user(user_id, f"🏆 Achievement Unlocked: {achievement.name}!")
        
        return [a for a in unlocked if a is not None]
    
    def _unlock(self, achievement_id: str, user_id: int):
        """Unlock achievement for user"""
        
        # Check if already unlocked
        existing = self.db.query(UserAchievement).filter_by(
            user_id=user_id,
            achievement_id=achievement_id
        ).first()
        
        if existing:
            return None
        
        # Get achievement
        achievement = self.db.query(Achievement).get(achievement_id)
        if not achievement:
            return None
        
        # Unlock
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.now(timezone.utc)
        )
        self.db.add(user_achievement)
        
        # Award points
        loyalty = LoyaltySystem(self.db)
        loyalty.award_points(
            user_id=user_id,
            amount=achievement.points,
            type='achievement',
            description=f"Achievement: {achievement.name}"
        )
        
        self.db.commit()
        
        return achievement
```

### Daily Challenges

```python
@app.get("/api/challenges/daily")
async def get_daily_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's challenges"""
    today = datetime.now(timezone.utc).date()
    
    challenges = db.query(Challenge).filter(
        Challenge.type == 'daily',
        Challenge.start_date <= today,
        Challenge.end_date >= today,
        Challenge.is_active == True
    ).all()
    
    # Get user's progress
    result = []
    for challenge in challenges:
        user_challenge = db.query(UserChallenge).filter_by(
            user_id=current_user.id,
            challenge_id=challenge.id
        ).first()
        
        result.append({
            'challenge': challenge,
            'progress': user_challenge.progress if user_challenge else 0,
            'completed': user_challenge.completed if user_challenge else False
        })
    
    return result

def update_challenge_progress(
    user_id: int,
    event_type: str,
    value: int = 1
):
    """Update user's progress on challenges"""
    
    # Get active challenges matching event type
    challenges = db.query(Challenge).filter(
        Challenge.objective.like(f"%{event_type}%"),
        Challenge.is_active == True
    ).all()
    
    for challenge in challenges:
        user_challenge = db.query(UserChallenge).filter_by(
            user_id=user_id,
            challenge_id=challenge.id
        ).first()
        
        if not user_challenge:
            user_challenge = UserChallenge(
                user_id=user_id,
                challenge_id=challenge.id,
                progress=0
            )
            db.add(user_challenge)
        
        # Skip if already completed
        if user_challenge.completed:
            continue
        
        # Update progress
        user_challenge.progress += value
        
        # Check completion
        if user_challenge.progress >= challenge.target_value:
            user_challenge.completed = True
            user_challenge.completed_at = datetime.now(timezone.utc)
            
            # Award rewards
            loyalty = LoyaltySystem(db)
            loyalty.award_points(
                user_id=user_id,
                amount=challenge.reward_points,
                type='challenge',
                description=f"Challenge: {challenge.title}"
            )
            
            if challenge.reward_badge:
                achievement_system = AchievementSystem(db)
                achievement_system._unlock(challenge.reward_badge, user_id)
            
            # Notify
            notify_user(user_id, f"✅ Challenge Complete: {challenge.title}!")
    
    db.commit()
```

### Referral Program

```python
@app.post("/api/referrals/generate")
async def generate_referral_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate unique referral code"""
    
    # Check if user already has code
    existing = db.query(Referral).filter_by(
        referrer_id=current_user.id
    ).first()
    
    if existing:
        return {"code": existing.referral_code}
    
    # Generate code
    code = f"POKEMON-{current_user.id}-{secrets.token_urlsafe(4).upper()}"
    
    referral = Referral(
        referrer_id=current_user.id,
        referral_code=code
    )
    db.add(referral)
    db.commit()
    
    return {"code": code}

@app.post("/api/referrals/apply")
async def apply_referral_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply referral code (for new users)"""
    
    # Find referral
    referral = db.query(Referral).filter_by(referral_code=code).first()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Invalid code")
    
    if referral.referrer_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot use own code")
    
    # Check if user already used a referral
    existing_use = db.query(Referral).filter_by(referred_id=current_user.id).first()
    if existing_use:
        raise HTTPException(status_code=400, detail="Already used referral")
    
    # Apply referral
    referral.referred_id = current_user.id
    referral.status = 'completed'
    referral.completed_at = datetime.now(timezone.utc)
    
    # Award points to both users
    loyalty = LoyaltySystem(db)
    
    # Referrer gets 100 points
    loyalty.award_points(
        user_id=referral.referrer_id,
        amount=100,
        type='referral',
        description=f"Referral: {current_user.name}"
    )
    
    # Referred gets 50 points
    loyalty.award_points(
        user_id=current_user.id,
        amount=50,
        type='referral',
        description="Welcome bonus"
    )
    
    db.commit()
    
    return {"success": True, "bonus_points": 50}
```

### Frontend UI

```html
<!-- Achievements Page -->
<div class="achievements-page">
  <h2>Your Achievements</h2>
  <div class="stats-row">
    <div class="stat">
      <span class="value">42/87</span>
      <span class="label">Unlocked</span>
    </div>
    <div class="stat">
      <span class="value">2,340</span>
      <span class="label">Points Earned</span>
    </div>
  </div>
  
  <div class="achievement-grid">
    <div class="achievement-card unlocked rarity-legendary">
      <div class="icon">🏆</div>
      <h4>Gotta Catch 'Em All</h4>
      <p>Collect all 151 Gen 1 Pokemon</p>
      <div class="points">+500 points</div>
      <div class="unlocked-date">Unlocked: Jan 15, 2025</div>
    </div>
    
    <div class="achievement-card locked">
      <div class="icon">🔒</div>
      <h4>Master Trader</h4>
      <p>Complete 50 trades</p>
      <div class="progress-bar">
        <div class="progress" style="width: 60%"></div>
      </div>
      <div class="progress-text">30/50</div>
    </div>
  </div>
</div>

<!-- Loyalty Dashboard -->
<div class="loyalty-dashboard">
  <div class="tier-card gold">
    <h3>Gold Tier</h3>
    <div class="tier-icon">⭐⭐⭐</div>
    <div class="benefits">
      <span>1.5x Points Multiplier</span>
      <span>Exclusive Rewards</span>
      <span>Priority Support</span>
    </div>
    <div class="progress-to-next">
      2,340 / 15,000 points to Platinum
      <div class="progress-bar">
        <div class="progress" style="width: 15.6%"></div>
      </div>
    </div>
  </div>
  
  <div class="points-summary">
    <h3>Your Points</h3>
    <div class="points-balance">2,340</div>
    <div class="points-breakdown">
      <span>Lifetime: 5,678</span>
      <span>Spent: 3,338</span>
    </div>
  </div>
</div>

<!-- Daily Challenges -->
<div class="daily-challenges">
  <h3>Daily Challenges</h3>
  <div class="challenge-list">
    <div class="challenge-item completed">
      <div class="icon">✅</div>
      <div class="details">
        <h4>Daily Login</h4>
        <p>Log in to the marketplace</p>
      </div>
      <div class="reward">+5 points</div>
    </div>
    
    <div class="challenge-item in-progress">
      <div class="icon">🎯</div>
      <div class="details">
        <h4>Make 3 Purchases</h4>
        <p>Buy at least 3 Pokemon today</p>
        <div class="progress-bar">
          <div class="progress" style="width: 66%"></div>
        </div>
        <span class="progress-text">2/3</span>
      </div>
      <div class="reward">+50 points</div>
    </div>
    
    <div class="challenge-item">
      <div class="icon">💬</div>
      <div class="details">
        <h4>Leave a Review</h4>
        <p>Review a purchase or trade</p>
      </div>
      <div class="reward">+20 points</div>
    </div>
  </div>
</div>

<!-- Rewards Shop -->
<div class="rewards-shop">
  <h2>Rewards Shop</h2>
  <div class="your-points">Available Points: 2,340</div>
  
  <div class="rewards-grid">
    <div class="reward-card">
      <img src="discount-10.png" />
      <h4>10% Discount Code</h4>
      <p>Valid for 30 days</p>
      <div class="cost">500 points</div>
      <button onclick="redeemReward(1)">Redeem</button>
    </div>
    
    <div class="reward-card special">
      <span class="badge">Limited</span>
      <img src="shiny-pikachu.png" />
      <h4>Shiny Pikachu</h4>
      <p>Exclusive reward Pokemon</p>
      <div class="cost">2,000 points</div>
      <div class="stock">Only 5 left!</div>
      <button onclick="redeemReward(2)">Redeem</button>
    </div>
  </div>
</div>

<!-- Referral Program -->
<div class="referral-section">
  <h3>Invite Friends, Earn Points!</h3>
  <p>You get 100 points, they get 50 points</p>
  
  <div class="referral-code-box">
    <span class="code">POKEMON-123-A7GF</span>
    <button onclick="copyCode()">Copy</button>
    <button onclick="shareCode()">Share</button>
  </div>
  
  <div class="referral-stats">
    <span>🎉 12 friends joined</span>
    <span>💰 1,200 points earned</span>
  </div>
</div>
```

## 📝 Criterios de Aceptación

- [ ] Achievements system con badges
- [ ] Loyalty points earn & redeem
- [ ] Tier system (Bronze → Diamond)
- [ ] Daily challenges
- [ ] Streak tracking
- [ ] Referral program
- [ ] Rewards shop
- [ ] Leaderboards integration
- [ ] Notifications for unlocks

## 🧪 Testing

```python
def test_loyalty_points():
    loyalty = LoyaltySystem(db)
    
    # Award points
    points = loyalty.award_purchase_points(transaction_id=1)
    assert points == 510  # $51 × 10 points
    
    # Check tier
    user_loyalty = db.query(LoyaltyPoints).filter_by(user_id=1).first()
    assert user_loyalty.available_points == 510

def test_achievement_unlock():
    achievements = AchievementSystem(db)
    
    # Make first purchase
    unlocked = achievements.check_achievements(user_id=1, event_type='purchase', data={})
    
    assert any(a.achievement_id == 'first_purchase' for a in unlocked)

def test_daily_challenge():
    challenge = create_challenge(
        title="Buy 3 Pokemon",
        objective="purchase_3_pokemon",
        target_value=3,
        reward_points=50
    )
    
    # Make purchases
    for _ in range(3):
        update_challenge_progress(user_id=1, event_type='purchase')
    
    # Check completion
    user_challenge = db.query(UserChallenge).filter_by(
        user_id=1,
        challenge_id=challenge.id
    ).first()
    
    assert user_challenge.completed == True
```

## ⏱️ Estimación

**Tiempo:** 3-4 semanas
**Prioridad:** Medium
**Complejidad:** High

## 🔗 Issues Relacionados

Relacionado con: #phase-7-1-ai-recommendations, #phase-7-2-social-marketplace

## 📚 Recursos

- [Gamification Design](https://www.gamify.com/)
- [Loyalty Program Best Practices](https://www.smile.io/blog/loyalty-program-guide)
- [Achievement Systems](https://www.gamedeveloper.com/design/achievement-design-101)

## 💡 Engagement Metrics

Track:
- Daily Active Users (DAU)
- Challenge completion rate
- Points redemption rate
- Referral conversion rate
- Achievement unlock rate
- Tier distribution

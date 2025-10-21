---
title: "[Phase 6.2] IntentMandates for Autonomous Purchases"
labels: enhancement, ap2, automation, phase-6
assignees: CERVIII
---

## 📋 Descripción

Implementar IntentMandates para compras autónomas: el usuario autoriza al agente a realizar compras automáticamente dentro de límites predefinidos (presupuesto, categorías, frecuencia).

## 🎯 Tipo de Issue

- [x] 🤖 AP2 Protocol AVANZADO
- [x] ✨ Nueva feature
- [x] 🔐 Autorización

## 📦 Fase del Roadmap

**Fase 6.2: IntentMandates (Compras Autónomas)**

## ✅ Tareas

### IntentMandate Data Structure

```typescript
interface IntentMandate {
  id: string;
  user_id: number;
  agent_id: string;
  status: "active" | "paused" | "expired" | "revoked";
  
  // Authorization scope
  intent: {
    type: "recurring_purchase" | "price_alert" | "inventory_monitor" | "bundle_optimizer";
    description: string;
  };
  
  // Budget constraints
  budget: {
    max_amount_per_transaction: number;
    max_amount_per_day: number;
    max_amount_per_month: number;
    currency: "USD";
  };
  
  // Product constraints
  products: {
    categories?: string[];  // ['pokemon', 'items']
    specific_ids?: number[];  // [1, 4, 7] (starters only)
    exclude_ids?: number[];
    max_price_per_item?: number;
  };
  
  // Time constraints
  schedule: {
    frequency?: "daily" | "weekly" | "monthly";
    time_window?: {
      start: string;  // "09:00"
      end: string;    // "17:00"
    };
    timezone: string;
  };
  
  // Notification preferences
  notifications: {
    before_purchase: boolean;
    after_purchase: boolean;
    budget_threshold: number;  // Notify at 80% budget used
    channels: ("email" | "push" | "sms")[];
  };
  
  // Validity
  valid_from: string;
  valid_until: string;
  
  // Signatures
  user_signature: string;  // WebAuthn signature
  agent_signature: string;
  
  created_at: string;
  last_used?: string;
  total_spent: number;
}
```

### Database Schema

```sql
CREATE TABLE intent_mandates (
    id VARCHAR(100) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    agent_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    intent_type VARCHAR(50),
    intent_description TEXT,
    
    -- Budget limits (in cents)
    max_per_transaction INTEGER,
    max_per_day INTEGER,
    max_per_month INTEGER,
    
    -- Product filters
    allowed_categories JSON,
    allowed_product_ids JSON,
    excluded_product_ids JSON,
    max_price_per_item INTEGER,
    
    -- Schedule
    frequency VARCHAR(20),
    time_window_start TIME,
    time_window_end TIME,
    timezone VARCHAR(50),
    
    -- Notifications
    notify_before BOOLEAN DEFAULT TRUE,
    notify_after BOOLEAN DEFAULT TRUE,
    notify_at_budget_pct INTEGER DEFAULT 80,
    notification_channels JSON,
    
    -- Validity
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    
    -- Signatures
    user_signature TEXT,
    agent_signature TEXT,
    
    -- Tracking
    created_at TIMESTAMP,
    last_used TIMESTAMP,
    total_spent INTEGER DEFAULT 0,
    
    INDEX idx_user_status (user_id, status),
    INDEX idx_expires (valid_until)
);

CREATE TABLE intent_mandate_transactions (
    id INTEGER PRIMARY KEY,
    mandate_id VARCHAR(100) REFERENCES intent_mandates(id),
    transaction_id INTEGER REFERENCES transactions(id),
    amount INTEGER,
    approved_automatically BOOLEAN,
    created_at TIMESTAMP
);
```

### Backend Endpoints

#### Mandate Creation
```python
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, validator

class CreateIntentMandateRequest(BaseModel):
    intent_type: str
    description: str
    max_per_transaction: int
    max_per_day: int
    max_per_month: int
    allowed_categories: list[str] = None
    allowed_product_ids: list[int] = None
    frequency: str = None
    valid_until: datetime
    user_signature: str

    @validator('max_per_transaction')
    def validate_transaction_limit(cls, v, values):
        if v > values.get('max_per_day', float('inf')):
            raise ValueError("Per-transaction limit exceeds daily limit")
        return v

@app.post("/api/intent-mandates")
async def create_intent_mandate(
    request: CreateIntentMandateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user signature
    if not verify_webauthn_signature(request.user_signature, current_user):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Generate mandate ID
    mandate_id = f"mandate_{secrets.token_urlsafe(16)}"
    
    # Create mandate
    mandate = IntentMandate(
        id=mandate_id,
        user_id=current_user.id,
        agent_id=request.agent_id,
        status="active",
        intent_type=request.intent_type,
        intent_description=request.description,
        max_per_transaction=request.max_per_transaction,
        max_per_day=request.max_per_day,
        max_per_month=request.max_per_month,
        allowed_categories=request.allowed_categories,
        allowed_product_ids=request.allowed_product_ids,
        frequency=request.frequency,
        valid_from=datetime.now(timezone.utc),
        valid_until=request.valid_until,
        user_signature=request.user_signature,
        total_spent=0
    )
    
    db.add(mandate)
    db.commit()
    
    # Send confirmation email
    send_mandate_created_email(current_user.email, mandate)
    
    return mandate

@app.get("/api/intent-mandates")
async def list_mandates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user's mandates"""
    mandates = db.query(IntentMandate).filter_by(user_id=current_user.id).all()
    return mandates

@app.patch("/api/intent-mandates/{mandate_id}/pause")
async def pause_mandate(
    mandate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pause an active mandate"""
    mandate = db.query(IntentMandate).filter_by(
        id=mandate_id,
        user_id=current_user.id
    ).first()
    
    if not mandate:
        raise HTTPException(status_code=404)
    
    mandate.status = "paused"
    db.commit()
    
    return {"status": "paused"}

@app.delete("/api/intent-mandates/{mandate_id}")
async def revoke_mandate(
    mandate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently revoke a mandate"""
    mandate = db.query(IntentMandate).filter_by(
        id=mandate_id,
        user_id=current_user.id
    ).first()
    
    if not mandate:
        raise HTTPException(status_code=404)
    
    mandate.status = "revoked"
    db.commit()
    
    return {"status": "revoked"}
```

#### Autonomous Purchase Execution

```python
class AutomatedPurchaseService:
    def __init__(self, db: Session):
        self.db = db
    
    async def execute_autonomous_purchase(
        self,
        mandate_id: str,
        items: list[dict]
    ) -> dict:
        """Execute a purchase under an IntentMandate"""
        
        # Get mandate
        mandate = self.db.query(IntentMandate).filter_by(id=mandate_id).first()
        if not mandate:
            raise ValueError("Mandate not found")
        
        # Validate mandate
        validation = self._validate_mandate(mandate, items)
        if not validation["valid"]:
            raise ValueError(f"Mandate validation failed: {validation['reason']}")
        
        # Calculate total
        total = sum(item["price"] * item["quantity"] for item in items)
        
        # Check budget
        budget_check = self._check_budget(mandate, total)
        if not budget_check["allowed"]:
            raise ValueError(f"Budget exceeded: {budget_check['reason']}")
        
        # Create cart
        cart = Cart(
            user_id=mandate.user_id,
            session_id=f"mandate_{mandate_id}_{int(time.time())}",
            status="active"
        )
        self.db.add(cart)
        self.db.flush()
        
        # Add items
        for item in items:
            cart_item = CartItem(
                cart_id=cart.id,
                pokemon_numero=item["id"],
                quantity=item["quantity"],
                price_snapshot=item["price"]
            )
            self.db.add(cart_item)
        
        # Execute payment (using default payment method)
        user = self.db.query(User).get(mandate.user_id)
        default_payment = self.db.query(PaymentMethod).filter_by(
            user_id=user.id,
            is_default=True
        ).first()
        
        if not default_payment:
            raise ValueError("No default payment method")
        
        # Process payment
        payment = await self._process_payment(cart, default_payment)
        
        # Update mandate tracking
        mandate.total_spent += total
        mandate.last_used = datetime.now(timezone.utc)
        
        # Record transaction
        mandate_tx = IntentMandateTransaction(
            mandate_id=mandate_id,
            transaction_id=payment.transaction_id,
            amount=total,
            approved_automatically=True
        )
        self.db.add(mandate_tx)
        self.db.commit()
        
        # Send notification
        if mandate.notify_after:
            await self._send_purchase_notification(mandate, cart, total)
        
        return {
            "status": "success",
            "transaction_id": payment.transaction_id,
            "amount": total,
            "mandate_id": mandate_id
        }
    
    def _validate_mandate(self, mandate: IntentMandate, items: list[dict]) -> dict:
        """Validate mandate constraints"""
        now = datetime.now(timezone.utc)
        
        # Check status
        if mandate.status != "active":
            return {"valid": False, "reason": f"Mandate status: {mandate.status}"}
        
        # Check validity period
        if now < mandate.valid_from or now > mandate.valid_until:
            return {"valid": False, "reason": "Mandate expired"}
        
        # Check time window
        if mandate.time_window_start and mandate.time_window_end:
            current_time = now.time()
            if not (mandate.time_window_start <= current_time <= mandate.time_window_end):
                return {"valid": False, "reason": "Outside time window"}
        
        # Check product constraints
        if mandate.allowed_product_ids:
            for item in items:
                if item["id"] not in mandate.allowed_product_ids:
                    return {"valid": False, "reason": f"Product {item['id']} not allowed"}
        
        if mandate.excluded_product_ids:
            for item in items:
                if item["id"] in mandate.excluded_product_ids:
                    return {"valid": False, "reason": f"Product {item['id']} excluded"}
        
        # Check price per item
        if mandate.max_price_per_item:
            for item in items:
                if item["price"] > mandate.max_price_per_item:
                    return {"valid": False, "reason": f"Item price ${item['price']} exceeds limit"}
        
        return {"valid": True}
    
    def _check_budget(self, mandate: IntentMandate, amount: int) -> dict:
        """Check budget constraints"""
        now = datetime.now(timezone.utc)
        
        # Per-transaction limit
        if amount > mandate.max_per_transaction:
            return {
                "allowed": False,
                "reason": f"Amount ${amount} exceeds per-transaction limit ${mandate.max_per_transaction}"
            }
        
        # Daily limit
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_spent = self.db.query(func.sum(IntentMandateTransaction.amount)).filter(
            IntentMandateTransaction.mandate_id == mandate.id,
            IntentMandateTransaction.created_at >= today_start
        ).scalar() or 0
        
        if daily_spent + amount > mandate.max_per_day:
            return {
                "allowed": False,
                "reason": f"Daily limit ${mandate.max_per_day} would be exceeded (spent: ${daily_spent})"
            }
        
        # Monthly limit
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_spent = self.db.query(func.sum(IntentMandateTransaction.amount)).filter(
            IntentMandateTransaction.mandate_id == mandate.id,
            IntentMandateTransaction.created_at >= month_start
        ).scalar() or 0
        
        if monthly_spent + amount > mandate.max_per_month:
            return {
                "allowed": False,
                "reason": f"Monthly limit ${mandate.max_per_month} would be exceeded (spent: ${monthly_spent})"
            }
        
        return {"allowed": True}
```

### Frontend UI

#### Mandate Creation Page

```html
<div class="intent-mandate-creator">
  <h2>Create Autonomous Purchase Mandate</h2>
  <p>Authorize the AI agent to make purchases on your behalf within limits you define.</p>
  
  <form id="mandate-form">
    <div class="form-section">
      <h3>Intent Type</h3>
      <select name="intent_type" required>
        <option value="recurring_purchase">Recurring Purchase (buy daily)</option>
        <option value="price_alert">Price Alert (buy when price drops)</option>
        <option value="inventory_monitor">Inventory Monitor (buy when in stock)</option>
        <option value="bundle_optimizer">Bundle Optimizer (find best deals)</option>
      </select>
      
      <textarea name="description" placeholder="Describe your intent..." required></textarea>
    </div>
    
    <div class="form-section">
      <h3>Budget Limits</h3>
      <label>
        Max per transaction: $<input type="number" name="max_per_transaction" value="100" required />
      </label>
      <label>
        Max per day: $<input type="number" name="max_per_day" value="200" required />
      </label>
      <label>
        Max per month: $<input type="number" name="max_per_month" value="1000" required />
      </label>
    </div>
    
    <div class="form-section">
      <h3>Product Filters</h3>
      <label>
        <input type="checkbox" name="category_pokemon" checked />
        Pokemon
      </label>
      <label>
        <input type="checkbox" name="category_items" />
        Items
      </label>
      
      <label>
        Max price per item: $<input type="number" name="max_price_per_item" value="150" />
      </label>
      
      <label>
        Specific Pokemon IDs (comma-separated):
        <input type="text" name="allowed_ids" placeholder="1,4,7" />
      </label>
    </div>
    
    <div class="form-section">
      <h3>Schedule</h3>
      <select name="frequency">
        <option value="">One-time</option>
        <option value="daily">Daily</option>
        <option value="weekly">Weekly</option>
        <option value="monthly">Monthly</option>
      </select>
      
      <label>
        Active hours:
        <input type="time" name="time_start" value="09:00" />
        to
        <input type="time" name="time_end" value="17:00" />
      </label>
    </div>
    
    <div class="form-section">
      <h3>Validity Period</h3>
      <label>
        Valid until:
        <input type="date" name="valid_until" required />
      </label>
    </div>
    
    <div class="form-section">
      <h3>Notifications</h3>
      <label>
        <input type="checkbox" name="notify_before" checked />
        Notify before each purchase
      </label>
      <label>
        <input type="checkbox" name="notify_after" checked />
        Notify after each purchase
      </label>
      <label>
        Alert at: <input type="number" name="budget_threshold" value="80" />% budget used
      </label>
    </div>
    
    <div class="warning-box">
      ⚠️ By creating this mandate, you authorize the AI agent to make autonomous purchases
      within the limits you've set. You can pause or revoke this mandate at any time.
    </div>
    
    <button type="button" onclick="authenticateAndCreate()">
      🔐 Authenticate & Create Mandate
    </button>
  </form>
</div>

<script>
async function authenticateAndCreate() {
    const formData = new FormData(document.getElementById('mandate-form'));
    
    // Get WebAuthn signature
    const challenge = await fetch('/api/auth/challenge').then(r => r.json());
    const credential = await navigator.credentials.get({
        publicKey: {
            challenge: Uint8Array.from(challenge.challenge, c => c.charCodeAt(0)),
            rpId: window.location.hostname,
            userVerification: 'required'
        }
    });
    
    const signature = btoa(String.fromCharCode(...new Uint8Array(credential.response.signature)));
    
    // Submit mandate
    const response = await fetch('/api/intent-mandates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ...Object.fromEntries(formData),
            user_signature: signature
        })
    });
    
    if (response.ok) {
        alert('✅ Mandate created successfully!');
        window.location.href = '/my-account/mandates';
    } else {
        alert('❌ Failed to create mandate');
    }
}
</script>
```

#### Mandate Management Page

```html
<div class="mandates-list">
  <h2>Your Autonomous Purchase Mandates</h2>
  
  <div id="mandates-grid"></div>
</div>

<script>
async function loadMandates() {
    const response = await fetch('/api/intent-mandates');
    const mandates = await response.json();
    
    const grid = document.getElementById('mandates-grid');
    mandates.forEach(mandate => {
        const card = document.createElement('div');
        card.className = `mandate-card status-${mandate.status}`;
        card.innerHTML = `
            <div class="mandate-header">
                <h3>${mandate.intent_description}</h3>
                <span class="badge badge-${mandate.status}">${mandate.status}</span>
            </div>
            
            <div class="mandate-stats">
                <div class="stat">
                    <span class="label">Spent This Month</span>
                    <span class="value">$${(mandate.total_spent / 100).toFixed(2)}</span>
                    <span class="limit">/ $${(mandate.max_per_month / 100).toFixed(2)}</span>
                </div>
                
                <div class="progress-bar">
                    <div class="progress" style="width: ${(mandate.total_spent / mandate.max_per_month * 100)}%"></div>
                </div>
            </div>
            
            <div class="mandate-details">
                <p>📅 Valid until: ${new Date(mandate.valid_until).toLocaleDateString()}</p>
                <p>💰 Limits: $${mandate.max_per_transaction}/tx, $${mandate.max_per_day}/day</p>
                <p>🕐 Last used: ${mandate.last_used ? new Date(mandate.last_used).toLocaleString() : 'Never'}</p>
            </div>
            
            <div class="mandate-actions">
                ${mandate.status === 'active' 
                    ? `<button onclick="pauseMandate('${mandate.id}')">⏸️ Pause</button>`
                    : `<button onclick="resumeMandate('${mandate.id}')">▶️ Resume</button>`
                }
                <button onclick="revokeMandate('${mandate.id}')" class="danger">🗑️ Revoke</button>
            </div>
        `;
        grid.appendChild(card);
    });
}
</script>
```

## 📝 Criterios de Aceptación

- [ ] Users pueden crear IntentMandates
- [ ] WebAuthn signature required
- [ ] Budget limits enforced
- [ ] Product filters enforced
- [ ] Time window validation
- [ ] Autonomous purchases ejecutan correctamente
- [ ] Notifications enviadas
- [ ] Users pueden pause/resume/revoke mandates
- [ ] Dashboard muestra mandates activos y spending

## 🧪 Testing

```python
def test_create_intent_mandate():
    mandate = create_mandate(
        user_id=1,
        max_per_transaction=10000,  # $100
        max_per_day=20000,
        max_per_month=100000,
        allowed_product_ids=[1, 4, 7]
    )
    assert mandate.status == "active"

def test_autonomous_purchase_within_limits():
    service = AutomatedPurchaseService(db)
    result = service.execute_autonomous_purchase(
        mandate_id="mandate_abc123",
        items=[{"id": 1, "quantity": 1, "price": 5500}]
    )
    assert result["status"] == "success"

def test_budget_exceeded():
    with pytest.raises(ValueError, match="Budget exceeded"):
        service.execute_autonomous_purchase(
            mandate_id="mandate_abc123",
            items=[{"id": 1, "quantity": 10, "price": 20000}]  # Exceeds limit
        )

def test_unauthorized_product():
    with pytest.raises(ValueError, match="Product .* not allowed"):
        service.execute_autonomous_purchase(
            mandate_id="mandate_abc123",
            items=[{"id": 150, "quantity": 1, "price": 5000}]  # Mewtwo not in allowed_ids
        )
```

## ⏱️ Estimación

**Tiempo:** 3-4 semanas
**Prioridad:** High (killer feature)
**Complejidad:** Very High

## 🔗 Issues Relacionados

Depende de: #phase-4-3-real-authorization, #phase-6-1-discovery
Relacionado con: #phase-7-1-ai-recommendations

## 📚 Recursos

- [OAuth 2.0 Token Exchange](https://datatracker.ietf.org/doc/html/rfc8693)
- [Open Banking Consent Management](https://www.openbanking.org.uk/)
- [Plaid Link](https://plaid.com/docs/link/)

## 🚨 Security Considerations

**CRÍTICO:**
- IntentMandate MUST have user WebAuthn signature
- Budget limits MUST be enforced server-side
- Agent CANNOT modify mandate parameters
- User can revoke at any time
- All autonomous transactions logged
- Email/push notification for each purchase
- Budget threshold alerts (e.g., at 80% spent)

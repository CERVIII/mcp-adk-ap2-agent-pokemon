---
title: "[Phase 5.1] Stripe Integration for Real Payments"
labels: enhancement, payments, backend, phase-5
assignees: CERVIII
---

## 📋 Descripción

Integrar Stripe como payment processor real, reemplazando mock payment processor con Stripe Payment Intents, webhooks, 3D Secure, y gestión de refunds.

## 🎯 Tipo de Issue

- [x] 💳 Payments CRÍTICO
- [x] ✨ Nueva feature
- [x] 🔐 PCI-DSS

## 📦 Fase del Roadmap

**Fase 5.1: Integración con Stripe**

## ✅ Tareas

### Stripe Account Setup
- [ ] Crear cuenta en [Stripe Dashboard](https://dashboard.stripe.com)
- [ ] Obtener API keys: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`
- [ ] Configurar webhook endpoint: `https://yourdomain.com/webhooks/stripe`
- [ ] Activar Stripe Testing Mode (usar test keys)

### Backend Dependencies
```bash
pip install stripe
```

### Environment Variables
```bash
# .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Database Schema
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id),
    user_id INTEGER REFERENCES users(id),
    stripe_payment_intent_id VARCHAR(100) UNIQUE,
    amount INTEGER,  -- en centavos (e.g., 5100 = $51.00)
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(20),  -- 'pending' | 'succeeded' | 'failed' | 'canceled' | 'refunded'
    payment_method_id VARCHAR(100),
    client_secret VARCHAR(200),
    error_code VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE refunds (
    id INTEGER PRIMARY KEY,
    payment_id INTEGER REFERENCES payments(id),
    stripe_refund_id VARCHAR(100) UNIQUE,
    amount INTEGER,
    reason VARCHAR(50),  -- 'requested_by_customer' | 'duplicate' | 'fraudulent'
    status VARCHAR(20),
    created_at TIMESTAMP
);
```

### Backend Endpoints

#### Payment Intent Creation
```python
@app.post("/api/cart/checkout/create-payment-intent")
async def create_payment_intent(
    cart_id: int,
    payment_method_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = get_cart(cart_id)
    
    # Create Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=int(cart.total * 100),  # Convert USD to cents
        currency="usd",
        payment_method=payment_method_id,
        confirm=True,
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
        metadata={
            "cart_id": cart_id,
            "user_id": current_user.id,
            "pokemon_names": ",".join([item.pokemon_name for item in cart.items])
        }
    )
    
    # Store in database
    payment = Payment(
        cart_id=cart_id,
        user_id=current_user.id,
        stripe_payment_intent_id=intent.id,
        amount=intent.amount,
        status=intent.status,
        payment_method_id=payment_method_id,
        client_secret=intent.client_secret
    )
    db.add(payment)
    db.commit()
    
    return {"client_secret": intent.client_secret, "status": intent.status}
```

#### Webhook Handler
```python
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event.type == "payment_intent.succeeded":
        handle_payment_success(event.data.object, db)
    elif event.type == "payment_intent.payment_failed":
        handle_payment_failure(event.data.object, db)
    elif event.type == "charge.refunded":
        handle_refund(event.data.object, db)
    
    return {"status": "success"}

def handle_payment_success(payment_intent, db: Session):
    payment = db.query(Payment).filter_by(
        stripe_payment_intent_id=payment_intent.id
    ).first()
    
    payment.status = "succeeded"
    
    # Mark cart as completed
    cart = db.query(Cart).get(payment.cart_id)
    cart.status = "completed"
    
    # Update inventory
    for item in cart.items:
        pokemon = get_pokemon_by_numero(item.pokemon_numero)
        pokemon.inventario["disponibles"] -= item.quantity
        pokemon.inventario["vendidos"] += item.quantity
    
    # Create transaction record
    transaction = Transaction(
        user_id=payment.user_id,
        cart_id=payment.cart_id,
        total=payment.amount / 100,
        status="completed"
    )
    db.add(transaction)
    
    db.commit()
    
    # Send confirmation email
    send_purchase_confirmation_email(payment.user_id, transaction.id)
```

#### Refund Endpoint
```python
@app.post("/api/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).get(payment_id)
    
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create Stripe refund
    refund = stripe.Refund.create(
        payment_intent=payment.stripe_payment_intent_id,
        reason=reason
    )
    
    # Store in database
    refund_record = Refund(
        payment_id=payment_id,
        stripe_refund_id=refund.id,
        amount=refund.amount,
        reason=reason,
        status=refund.status
    )
    db.add(refund_record)
    
    payment.status = "refunded"
    db.commit()
    
    return {"status": "refunded", "refund_id": refund.id}
```

### Frontend Integration

#### Stripe Elements
```html
<!-- Load Stripe.js -->
<script src="https://js.stripe.com/v3/"></script>
```

```javascript
// Initialize Stripe
const stripe = Stripe('pk_test_...');

// Create Payment Element
const elements = stripe.elements();
const paymentElement = elements.create('payment', {
  layout: 'tabs'
});
paymentElement.mount('#payment-element');

// Handle form submission
async function handleCheckout(event) {
  event.preventDefault();
  
  // Create PaymentIntent on backend
  const response = await fetch('/api/cart/checkout/create-payment-intent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cart_id: cartId })
  });
  
  const { client_secret } = await response.json();
  
  // Confirm payment with Stripe
  const { error, paymentIntent } = await stripe.confirmPayment({
    elements,
    clientSecret: client_secret,
    confirmParams: {
      return_url: 'https://yourdomain.com/payment-success'
    }
  });
  
  if (error) {
    showError(error.message);
  } else if (paymentIntent.status === 'succeeded') {
    window.location.href = '/payment-success';
  }
}
```

### 3D Secure (SCA Compliance)
- [ ] Stripe automáticamente maneja 3DS cuando necesario
- [ ] Frontend debe estar preparado para redirect flow
- [ ] `return_url` debe manejar post-authentication

### Testing with Stripe Test Cards
```
Success: 4242 4242 4242 4242
3DS Required: 4000 0027 6000 3184
Decline: 4000 0000 0000 0002
Insufficient Funds: 4000 0000 0000 9995
```

## 📝 Criterios de Aceptación

- [ ] PaymentIntent creation funciona
- [ ] Stripe Elements UI integrado en checkout
- [ ] Webhooks procesan eventos correctamente
- [ ] Payments succeed con test card
- [ ] 3D Secure flow funciona
- [ ] Refunds pueden procesarse
- [ ] Inventory se actualiza después de payment
- [ ] Confirmation email se envía

## 🧪 Testing

### Test Scenarios
- [ ] Successful payment con 4242 card
- [ ] 3DS required con 3184 card
- [ ] Declined payment con 0002 card
- [ ] Insufficient funds con 9995 card
- [ ] Webhook verification
- [ ] Refund processing

### Integration Tests
```python
def test_stripe_payment_flow():
    # Create cart
    cart = create_test_cart()
    
    # Create PaymentIntent
    response = client.post("/api/cart/checkout/create-payment-intent", json={
        "cart_id": cart.id,
        "payment_method_id": "pm_card_visa"
    })
    
    assert response.status_code == 200
    assert "client_secret" in response.json()
    
    # Simulate webhook
    simulate_stripe_webhook("payment_intent.succeeded", payment_intent_id)
    
    # Verify cart completed
    cart = get_cart(cart.id)
    assert cart.status == "completed"
```

## ⏱️ Estimación

**Tiempo:** 1.5-2 semanas
**Prioridad:** CRÍTICA (core payment functionality)

## 🔗 Issues Relacionados

Depende de: #phase-4-2-user-profiles (payment methods)
Prerequisito para: #phase-5-2-alternative-payments
Relacionado con: #phase-5-3-pci-compliance

## 📚 Recursos

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Payment Intents](https://stripe.com/docs/payments/payment-intents)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe Elements](https://stripe.com/docs/payments/elements)
- [Stripe Testing](https://stripe.com/docs/testing)
- [3D Secure](https://stripe.com/docs/strong-customer-authentication)

## 🚨 Security & Compliance

**PCI-DSS:**
- [ ] NUNCA manejar raw card numbers en backend
- [ ] Stripe.js tokeniza cards en frontend
- [ ] Backend solo recibe payment_method_id
- [ ] HTTPS obligatorio

**Error Handling:**
- [ ] No exponer detalles técnicos al user
- [ ] Log errors para debugging
- [ ] User-friendly messages: "Payment failed. Please try again."

**Rate Limiting:**
- [ ] Limit PaymentIntent creation: 10 per minute por user
- [ ] Prevent rapid refund requests

## 💰 Stripe Fees

**Pricing (USA):**
- 2.9% + $0.30 per successful card charge
- No monthly fees en cuenta estándar
- Refunds: fees NOT returned

**Calculations:**
```python
def calculate_stripe_fee(amount_usd: float) -> float:
    return (amount_usd * 0.029) + 0.30

# Example: $51.00 Pokemon purchase
# Fee: $1.78
# Net: $49.22
```

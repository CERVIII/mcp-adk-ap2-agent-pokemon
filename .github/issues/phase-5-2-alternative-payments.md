---
title: "[Phase 5.2] Alternative Payment Methods"
labels: enhancement, payments, integration, phase-5
assignees: CERVIII
---

## 📋 Descripción

Agregar métodos de pago alternativos: PayPal, Apple Pay, Google Pay, cryptocurrency (Bitcoin, Ethereum), y transferencia bancaria.

## 🎯 Tipo de Issue

- [x] 💳 Payments
- [x] ✨ Nueva feature
- [x] 🌐 Integration

## 📦 Fase del Roadmap

**Fase 5.2: Métodos de Pago Alternativos**

## ✅ Tareas

### 1. PayPal Integration

#### Setup
- [ ] Crear cuenta en [PayPal Developer](https://developer.paypal.com/)
- [ ] Obtener API credentials: `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`
- [ ] SDK: `pip install paypalrestsdk`

#### Backend Implementation
```python
import paypalrestsdk

paypalrestsdk.configure({
    "mode": "sandbox",  # or "live"
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_SECRET
})

@app.post("/api/cart/checkout/paypal")
async def create_paypal_payment(cart_id: int, db: Session = Depends(get_db)):
    cart = get_cart(cart_id)
    
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "https://yourdomain.com/payment/paypal/success",
            "cancel_url": "https://yourdomain.com/payment/paypal/cancel"
        },
        "transactions": [{
            "amount": {
                "total": str(cart.total),
                "currency": "USD"
            },
            "description": f"Pokemon purchase - Cart #{cart.id}",
            "item_list": {
                "items": [
                    {
                        "name": item.pokemon_name,
                        "price": str(item.price),
                        "currency": "USD",
                        "quantity": item.quantity
                    }
                    for item in cart.items
                ]
            }
        }]
    })
    
    if payment.create():
        # Store payment ID
        return {"approval_url": payment.links[1].href}
    else:
        raise HTTPException(status_code=400, detail=payment.error)
```

#### Frontend
```javascript
// PayPal JavaScript SDK
<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID"></script>

paypal.Buttons({
  createOrder: async () => {
    const response = await fetch('/api/cart/checkout/paypal', {
      method: 'POST',
      body: JSON.stringify({ cart_id: cartId })
    });
    const data = await response.json();
    return data.order_id;
  },
  onApprove: async (data) => {
    // Execute payment
    await fetch(`/api/payment/paypal/execute/${data.orderID}`);
    window.location.href = '/payment-success';
  }
}).render('#paypal-button-container');
```

### 2. Apple Pay Integration

#### Requirements
- [ ] Apple Developer Account
- [ ] Domain verification con Apple
- [ ] Stripe Apple Pay (integrado con Stripe)

#### Implementation
```javascript
const paymentRequest = stripe.paymentRequest({
  country: 'US',
  currency: 'usd',
  total: {
    label: 'Pokemon Purchase',
    amount: cartTotal * 100  // cents
  },
  requestPayerName: true,
  requestPayerEmail: true
});

const prButton = elements.create('paymentRequestButton', {
  paymentRequest: paymentRequest
});

// Check if Apple Pay available
const result = await paymentRequest.canMakePayment();
if (result && result.applePay) {
  prButton.mount('#apple-pay-button');
}

paymentRequest.on('paymentmethod', async (ev) => {
  // Confirm payment with Stripe
  const {paymentIntent, error} = await stripe.confirmCardPayment(
    clientSecret,
    {payment_method: ev.paymentMethod.id},
    {handleActions: false}
  );
  
  if (error) {
    ev.complete('fail');
  } else {
    ev.complete('success');
    window.location.href = '/payment-success';
  }
});
```

### 3. Google Pay Integration

#### Setup
- [ ] Google Pay Business Console
- [ ] Merchant ID
- [ ] Stripe Google Pay (integrado con Stripe)

#### Implementation
```javascript
const paymentsClient = new google.payments.api.PaymentsClient({
  environment: 'TEST'  // or 'PRODUCTION'
});

const paymentDataRequest = {
  apiVersion: 2,
  apiVersionMinor: 0,
  allowedPaymentMethods: [{
    type: 'CARD',
    parameters: {
      allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
      allowedCardNetworks: ['MASTERCARD', 'VISA']
    },
    tokenizationSpecification: {
      type: 'PAYMENT_GATEWAY',
      parameters: {
        gateway: 'stripe',
        'stripe:version': '2018-10-31',
        'stripe:publishableKey': STRIPE_PUBLISHABLE_KEY
      }
    }
  }],
  merchantInfo: {
    merchantName: 'PokeMart',
    merchantId: GOOGLE_MERCHANT_ID
  },
  transactionInfo: {
    totalPriceStatus: 'FINAL',
    totalPrice: cartTotal.toFixed(2),
    currencyCode: 'USD'
  }
};

const button = paymentsClient.createButton({
  onClick: onGooglePayButtonClicked
});
document.getElementById('google-pay-container').appendChild(button);
```

### 4. Cryptocurrency Payments

#### BTCPay Server Setup
- [ ] Self-hosted BTCPay Server o usar hosted service
- [ ] Support: Bitcoin (BTC), Lightning Network, Ethereum (ETH)
- [ ] API keys: `BTCPAY_URL`, `BTCPAY_API_KEY`

#### Backend
```python
import requests

@app.post("/api/cart/checkout/crypto")
async def create_crypto_invoice(
    cart_id: int,
    currency: str,  # 'BTC' | 'ETH'
    db: Session = Depends(get_db)
):
    cart = get_cart(cart_id)
    
    # Create BTCPay invoice
    response = requests.post(
        f"{BTCPAY_URL}/api/v1/invoices",
        headers={
            "Authorization": f"token {BTCPAY_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "amount": cart.total,
            "currency": "USD",
            "checkout": {
                "redirectURL": "https://yourdomain.com/payment/crypto/success",
                "paymentMethods": [currency]
            },
            "metadata": {
                "cart_id": cart.id,
                "user_id": cart.user_id
            }
        }
    )
    
    invoice = response.json()
    
    # Store invoice
    crypto_payment = CryptoPayment(
        cart_id=cart.id,
        invoice_id=invoice["id"],
        currency=currency,
        status="pending"
    )
    db.add(crypto_payment)
    db.commit()
    
    return {"checkout_url": invoice["checkoutLink"]}
```

#### Database
```sql
CREATE TABLE crypto_payments (
    id INTEGER PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id),
    invoice_id VARCHAR(100) UNIQUE,
    currency VARCHAR(10),  -- 'BTC' | 'ETH'
    amount_crypto DECIMAL(18,8),  -- Amount in BTC/ETH
    amount_usd DECIMAL(10,2),
    exchange_rate DECIMAL(18,8),
    status VARCHAR(20),  -- 'pending' | 'paid' | 'expired' | 'invalid'
    tx_hash VARCHAR(100),  -- Blockchain transaction hash
    confirmations INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);
```

### 5. Bank Transfer (ACH/SEPA)

#### Stripe ACH Direct Debit (US)
```python
@app.post("/api/cart/checkout/ach")
async def create_ach_payment(cart_id: int, bank_account_id: str):
    cart = get_cart(cart_id)
    
    # Create ACH payment
    payment_intent = stripe.PaymentIntent.create(
        amount=int(cart.total * 100),
        currency="usd",
        payment_method_types=["us_bank_account"],
        payment_method=bank_account_id,
        confirm=True
    )
    
    # ACH takes 3-5 business days
    return {
        "status": payment_intent.status,  # 'processing'
        "estimated_arrival": "3-5 business days"
    }
```

#### SEPA Direct Debit (Europe)
```python
payment_intent = stripe.PaymentIntent.create(
    amount=int(cart.total * 100),
    currency="eur",
    payment_method_types=["sepa_debit"],
    payment_method=sepa_account_id
)
```

### Database Schema
```sql
CREATE TABLE payment_methods_extended (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(20),  -- 'card' | 'paypal' | 'crypto' | 'bank_account'
    provider VARCHAR(50),  -- 'stripe' | 'paypal' | 'btcpay'
    external_id VARCHAR(100),  -- PayPal email, crypto address, bank account token
    details JSON,  -- Provider-specific details
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP
);
```

### Frontend Payment Selection UI
```html
<div class="payment-methods">
  <div class="payment-option" data-method="card">
    <input type="radio" name="payment" value="card" checked />
    <label>💳 Credit/Debit Card</label>
  </div>
  
  <div class="payment-option" data-method="paypal">
    <input type="radio" name="payment" value="paypal" />
    <label>
      <img src="paypal-logo.svg" height="20" />
      PayPal
    </label>
  </div>
  
  <div class="payment-option" data-method="apple-pay">
    <input type="radio" name="payment" value="apple-pay" />
    <label>
      <img src="apple-pay-logo.svg" height="20" />
      Apple Pay
    </label>
  </div>
  
  <div class="payment-option" data-method="google-pay">
    <input type="radio" name="payment" value="google-pay" />
    <label>
      <img src="google-pay-logo.svg" height="20" />
      Google Pay
    </label>
  </div>
  
  <div class="payment-option" data-method="crypto">
    <input type="radio" name="payment" value="crypto" />
    <label>₿ Cryptocurrency</label>
    <select name="crypto-currency">
      <option value="BTC">Bitcoin</option>
      <option value="ETH">Ethereum</option>
    </select>
  </div>
  
  <div class="payment-option" data-method="bank">
    <input type="radio" name="payment" value="bank" />
    <label>🏦 Bank Transfer (ACH)</label>
    <span class="badge">3-5 days</span>
  </div>
</div>
```

## 📝 Criterios de Aceptación

- [ ] PayPal checkout funciona
- [ ] Apple Pay disponible en iOS/Safari
- [ ] Google Pay disponible en Android/Chrome
- [ ] Crypto payments con BTCPay
- [ ] Bank transfer con Stripe ACH
- [ ] UI muestra métodos disponibles según device/browser
- [ ] Payment status tracking para cada método

## 🎨 UI/UX

**Dynamic Payment Options:**
- Apple Pay solo visible en Safari/iOS
- Google Pay solo visible en Chrome/Android
- Crypto option con selector de moneda
- Bank transfer con warning "Processing time: 3-5 days"

**Payment Icons:**
- High-quality SVG logos
- Hover effects
- Selected state styling

## ⏱️ Estimación

**Tiempo:** 2.5-3 semanas
**Prioridad:** Medium-High
**Complejidad:** High (multiple integrations)

## 🔗 Issues Relacionados

Depende de: #phase-5-1-stripe-integration
Relacionado con: #phase-5-3-pci-compliance
Prerequisito para: #phase-6-2-intent-mandates (autonomous crypto payments)

## 📚 Recursos

- [PayPal REST API](https://developer.paypal.com/docs/api/overview/)
- [Apple Pay Web](https://developer.apple.com/apple-pay/implementation/)
- [Google Pay Web](https://developers.google.com/pay/api/web)
- [BTCPay Server](https://docs.btcpayserver.org/)
- [Stripe ACH](https://stripe.com/docs/ach)
- [Stripe SEPA](https://stripe.com/docs/payments/sepa-debit)

## 🧪 Testing

### Test Scenarios
- [ ] PayPal sandbox payment
- [ ] Apple Pay test card (Safari)
- [ ] Google Pay test card (Chrome)
- [ ] Bitcoin testnet payment
- [ ] ACH test account

### Test Cards/Accounts
```
PayPal Sandbox:
  Email: buyer@test.com
  Password: testpass123

Apple Pay:
  Use Safari on iOS/macOS
  Test card: 4242 4242 4242 4242

Google Pay:
  Use Chrome
  Test card: 4242 4242 4242 4242

Bitcoin Testnet:
  Network: testnet3
  Faucet: https://testnet-faucet.mempool.co/
```

## 🚨 Security Considerations

**PayPal:**
- Validate IPN (Instant Payment Notification)
- Verify payment amount matches cart

**Crypto:**
- Confirm blockchain confirmations (BTC: 6, ETH: 12)
- Monitor for double-spend attacks
- Price volatility: lock rate for 15 minutes

**Bank Transfer:**
- Longer processing time = risk of fraud
- Hold order fulfillment until payment clears
- Stripe handles ACH verification

## 💰 Fees Comparison

| Method | Fee | Processing Time |
|--------|-----|-----------------|
| Stripe Card | 2.9% + $0.30 | Instant |
| PayPal | 2.9% + $0.30 | Instant |
| Apple Pay | 2.9% + $0.30 | Instant |
| Google Pay | 2.9% + $0.30 | Instant |
| Crypto (BTC) | 1% + network fee | 10-60 min |
| ACH | 0.8% (max $5) | 3-5 days |

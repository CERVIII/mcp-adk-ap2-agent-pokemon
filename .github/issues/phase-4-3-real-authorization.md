---
title: "[Phase 4.3] Real User Authorization with Device Signing"
labels: enhancement, security, ap2, phase-4
assignees: CERVIII
---

## 📋 Descripción

Implementar autorización de usuario REAL con firma criptográfica basada en dispositivo usando WebAuthn/FIDO2, reemplazando mock signatures con claves privadas del usuario.

## 🎯 Tipo de Issue

- [x] 🔐 Seguridad CRÍTICA
- [x] ✨ Nueva feature
- [x] 🤖 AP2 Protocol

## 📦 Fase del Roadmap

**Fase 4.3: Autorización Real de Usuario**

## ✅ Tareas

### WebAuthn/FIDO2 Implementation
- [ ] Librería backend: `py_webauthn` o `webauthn`
- [ ] Librería frontend: `@simplewebauthn/browser`
- [ ] Registro de dispositivo al login

### Database Schema
```sql
CREATE TABLE user_credentials (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    credential_id BLOB,  -- WebAuthn credential ID
    public_key BLOB,     -- COSE encoded public key
    counter INTEGER,     -- Signature counter
    device_name VARCHAR(100),  -- "Chrome on MacBook Pro"
    device_type VARCHAR(20),   -- 'platform' | 'cross-platform'
    created_at TIMESTAMP,
    last_used TIMESTAMP
);
```

### Backend Endpoints

#### Device Registration
- [ ] `POST /api/auth/register-device/begin` → Generate challenge
- [ ] `POST /api/auth/register-device/complete` → Verify attestation, store credential

#### Signing Flow
- [ ] `POST /api/cart/checkout/begin` → Generate PaymentRequest + challenge
- [ ] `POST /api/cart/checkout/sign` → Verify signature, process payment
- [ ] Signature validation con public key almacenada

### AP2 Integration

**CartMandate Changes:**
```typescript
// ANTES (mock):
user_signature_required: false
user_signature: null

// DESPUÉS (real):
user_signature_required: true
user_signature: {
  type: "webauthn",
  challenge: "base64_challenge",
  credential_id: "base64_credential_id",
  authenticator_data: "base64_data",
  client_data_json: "base64_json",
  signature: "base64_signature"
}
```

**PaymentRequest Signing:**
```python
def create_payment_request_to_sign(cart: Cart) -> dict:
    """Crea objeto CanonicalPaymentRequest para firma"""
    return {
        "merchant": "PokeMart",
        "amount": str(cart.total),
        "currency": "USD",
        "items": [{"id": item.pokemon_numero, "qty": item.quantity} for item in cart.items],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nonce": secrets.token_urlsafe(32)
    }

def verify_payment_signature(
    payment_request: dict,
    signature: dict,
    user: User
) -> bool:
    """Verifica que user firmó payment_request con su credential"""
    credential = get_user_credential(user.id, signature["credential_id"])
    
    # Verify WebAuthn signature
    verification = verify_authentication_response(
        credential=credential,
        expected_challenge=signature["challenge"],
        expected_origin="https://pokemart.example.com",
        expected_rp_id="pokemart.example.com",
        credential_public_key=credential.public_key,
        credential_current_sign_count=credential.counter,
        authenticator_data=signature["authenticator_data"],
        client_data_json=signature["client_data_json"],
        signature=signature["signature"]
    )
    
    return verification.verified
```

### Frontend Flow

#### Device Registration (First Time)
1. User completes OAuth login
2. Prompt: "Register this device for secure payments?"
3. Browser WebAuthn API → User gestures (Touch ID, Windows Hello, YubiKey)
4. Store credential ID + public key

#### Checkout Signing
1. User clicks "Complete Purchase"
2. Backend generates PaymentRequest + challenge
3. Frontend calls `navigator.credentials.get()`
4. User authenticates (biometric/PIN/security key)
5. Browser returns signed challenge
6. Frontend sends signature to backend
7. Backend verifies, processes payment

### UI Components
- [ ] Device registration modal con iconos (🔐 Touch ID, 🪟 Windows Hello, 🔑 YubiKey)
- [ ] "Trusted Devices" page en `/my-account/devices`
- [ ] List de devices registrados con "Last Used" timestamp
- [ ] "Revoke Device" button con confirmación
- [ ] Checkout: "Authenticate to complete purchase" prompt

### Fallback Mechanisms
- [ ] Si no hay device registrado → force registration
- [ ] Si device no disponible → "Register new device" option
- [ ] Si WebAuthn no soportado → fallback a email confirmation (menos seguro)

### Email Verification (Secondary)
- [ ] `POST /api/auth/verify-email/send` → Envía código 6 dígitos
- [ ] `POST /api/auth/verify-email/confirm` → Valida código
- [ ] 2FA opcional con TOTP (Google Authenticator)

## 🔧 Detalles Técnicos

**WebAuthn Registration Flow:**
```javascript
// Frontend
const credential = await navigator.credentials.create({
  publicKey: {
    challenge: Uint8Array.from(challenge, c => c.charCodeAt(0)),
    rp: { name: "PokeMart", id: "pokemart.example.com" },
    user: {
      id: Uint8Array.from(userId),
      name: userEmail,
      displayName: userName
    },
    pubKeyCredParams: [{ alg: -7, type: "public-key" }],  // ES256
    authenticatorSelection: {
      authenticatorAttachment: "platform",  // prefer built-in
      userVerification: "required"
    }
  }
});
```

**Security Considerations:**
- Challenge debe ser único y expire en 5 minutos
- Counter incrementa con cada signature → detecta credential cloning
- Public key nunca sale del backend
- Private key nunca sale del authenticator (TPM/Secure Enclave)

## 📝 Criterios de Aceptación

- [ ] User puede registrar device al login
- [ ] Checkout requiere firma WebAuthn
- [ ] Signature verification funciona
- [ ] CartMandate contiene signature real
- [ ] User puede gestionar devices registrados
- [ ] Fallback a email verification funciona
- [ ] AP2 merchant agent acepta signed CartMandates

## 🧪 Testing

### Unit Tests
- [ ] Signature verification con test keypair
- [ ] Challenge generation + expiration
- [ ] Counter increment validation

### Integration Tests
- [ ] End-to-end: register device → checkout → verify signature
- [ ] Test con Chrome (Touch ID), Firefox (Windows Hello), Safari (Face ID)

### Security Tests
- [ ] Replay attack: usar misma signature dos veces → reject
- [ ] Expired challenge → reject
- [ ] Wrong credential_id → reject
- [ ] Counter rollback → reject (credential cloned)

## ⏱️ Estimación

**Tiempo:** 2.5-3 semanas
**Prioridad:** CRÍTICA (para AP2 production)
**Complejidad:** Alta (criptografía, cross-browser)

## 🔗 Issues Relacionados

Depende de: #phase-4-1-authentication, #phase-4-2-user-profiles
Prerequisito para: #phase-6-2-intent-mandates (autonomous payments)
Relacionado con: #phase-5-1-stripe-integration

## 📚 Recursos

- [WebAuthn Guide](https://webauthn.guide/)
- [py_webauthn Documentation](https://github.com/duo-labs/py_webauthn)
- [SimpleWebAuthn Library](https://simplewebauthn.dev/)
- [FIDO2 Specification](https://fidoalliance.org/specs/fido-v2.0-ps-20190130/fido-client-to-authenticator-protocol-v2.0-ps-20190130.html)
- [AP2 Signature Requirements](https://github.com/google/android-payments-protocol)

## 🚨 Security Warnings

**CRÍTICO:**
- [ ] HTTPS obligatorio (WebAuthn no funciona en HTTP)
- [ ] RP ID debe coincidir con domain
- [ ] Origin validation estricta
- [ ] Challenge única por request
- [ ] Counter validation para detectar cloning
- [ ] Rate limiting en endpoints de verificación

**Browser Compatibility:**
- Chrome 67+
- Firefox 60+
- Safari 13+
- Edge 18+

**Mobile Support:**
- iOS 14.5+ (Face ID / Touch ID)
- Android 7+ (Fingerprint / PIN)

---
title: "[Phase 4.2] User Profiles & Management"
labels: enhancement, database, frontend, phase-4
assignees: CERVIII
---

## 📋 Descripción

Sistema completo de perfiles de usuario con preferencias, direcciones de envío, métodos de pago, wishlist y gestión de cuenta.

## 🎯 Tipo de Issue

- [x] ✨ Nueva feature
- [x] 🗄️ Database
- [x] 🎨 Frontend

## 📦 Fase del Roadmap

**Fase 4.2: Perfiles de Usuario**

## ✅ Tareas

### Database Schema Extensions
```sql
-- Extend users table
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN preferences JSON;  -- theme, language, notifications

CREATE TABLE shipping_addresses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP
);

CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(20),  -- 'card' | 'paypal' | 'crypto'
    last_four VARCHAR(4),
    brand VARCHAR(20),  -- 'visa' | 'mastercard' | 'amex'
    stripe_payment_method_id VARCHAR(100),
    is_default BOOLEAN DEFAULT 0,
    expires_at DATE,
    created_at TIMESTAMP
);

CREATE TABLE wishlists (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    pokemon_numero INTEGER,
    priority INTEGER DEFAULT 0,  -- 1=low, 2=medium, 3=high
    notes TEXT,
    added_at TIMESTAMP
);
```

### Backend Endpoints

#### Profile Management
- [ ] `GET /api/users/me` → Full profile con addresses, payment methods
- [ ] `PATCH /api/users/me` → Update name, phone, preferences
- [ ] `DELETE /api/users/me` → Delete account (GDPR)

#### Shipping Addresses
- [ ] `GET /api/users/me/addresses`
- [ ] `POST /api/users/me/addresses`
- [ ] `PATCH /api/users/me/addresses/{id}`
- [ ] `DELETE /api/users/me/addresses/{id}`
- [ ] `POST /api/users/me/addresses/{id}/set-default`

#### Payment Methods
- [ ] `GET /api/users/me/payment-methods`
- [ ] `POST /api/users/me/payment-methods` → Tokenizar con Stripe
- [ ] `DELETE /api/users/me/payment-methods/{id}`
- [ ] `POST /api/users/me/payment-methods/{id}/set-default`

#### Wishlist
- [ ] `GET /api/users/me/wishlist`
- [ ] `POST /api/users/me/wishlist` → Add Pokemon
- [ ] `DELETE /api/users/me/wishlist/{pokemon_id}`
- [ ] `PATCH /api/users/me/wishlist/{id}` → Update priority/notes

### Frontend Pages

#### `/my-account` - Main Profile Page
- [ ] Avatar display con option de cambiar (upload)
- [ ] Edit personal info form (name, email, phone)
- [ ] Theme selector (light/dark/auto)
- [ ] Language selector (en/es)
- [ ] Notification preferences (email on purchase, promotions)

#### `/my-account/addresses` - Addresses Management
- [ ] List de addresses con "Default" badge
- [ ] Add new address form con validación
- [ ] Edit/Delete con confirmación
- [ ] Set as default button
- [ ] Address validation con API (opcional)

#### `/my-account/payment-methods` - Payment Methods
- [ ] List de tarjetas con "•••• •••• •••• 1234"
- [ ] Brand icons (Visa, Mastercard, Amex)
- [ ] Add new card con Stripe Elements
- [ ] Delete con confirmación
- [ ] Set as default

#### `/my-wishlist` - Wishlist Page
- [ ] Grid de Pokemon cards
- [ ] Priority badges (⭐⭐⭐)
- [ ] "Add to Cart" button rápido
- [ ] Notes display
- [ ] Sort by: priority, date added, price, name
- [ ] "Buy All" button (adds todos al cart)

### Preferences System
```json
{
  "theme": "dark",
  "language": "es",
  "notifications": {
    "email_on_purchase": true,
    "promotional_emails": false,
    "price_alerts": true
  },
  "display": {
    "grid_size": "medium",
    "show_prices_in_usd": true
  }
}
```

### Avatar Upload
- [ ] Endpoint `POST /api/users/me/avatar` → Upload image
- [ ] Storage: filesystem o S3 bucket
- [ ] Image processing: resize to 200x200, webp format
- [ ] Fallback: Gravatar o avatar placeholder
- [ ] CDN serving (opcional Phase 7)

## 🔧 Detalles Técnicos

**Payment Methods Security:**
- NUNCA almacenar números completos de tarjeta
- Usar Stripe Payment Methods API
- Almacenar solo: `stripe_payment_method_id`, `last_four`, `brand`, `expires_at`
- PCI-DSS compliance (ver Phase 5.3)

**Address Validation:**
```python
# Opcional: Google Maps Address Validation API
import googlemaps
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
result = gmaps.addressvalidation(address_lines=["1600 Amphitheatre Parkway", "Mountain View, CA"])
```

**Wishlist Notifications (opcional):**
- Cuando Pokemon en wishlist baja de precio → email
- Cuando Pokemon out-of-stock vuelve disponible → email

## 📝 Criterios de Aceptación

- [ ] User puede editar su perfil
- [ ] User puede agregar múltiples direcciones
- [ ] User puede agregar múltiples payment methods
- [ ] User puede crear wishlist
- [ ] Preferences se persisten y aplican
- [ ] Delete account funciona correctamente (cascade)
- [ ] Avatar upload funciona

## 🎨 UI/UX Considerations

**Navbar Changes:**
- [ ] Avatar en navbar (clickeable)
- [ ] Dropdown menu:
  - My Account
  - My Wishlist
  - My Purchases (Phase 2.4)
  - Settings
  - Logout

**Checkout Flow Integration:**
- [ ] Checkout auto-completa con default address
- [ ] Checkout auto-completa con default payment method
- [ ] "Use different address" option
- [ ] "Use different payment method" option

## ⏱️ Estimación

**Tiempo:** 2-2.5 semanas
**Prioridad:** Alta (prerequisito para checkout real)

## 🔗 Issues Relacionados

Depende de: #phase-4-1-authentication
Prerequisito para: #phase-5-1-stripe-integration
Relacionado con: #phase-2-4-purchase-history

## 📚 Recursos

- [Stripe Payment Methods API](https://stripe.com/docs/payments/payment-methods)
- [Google Address Validation](https://developers.google.com/maps/documentation/address-validation)
- [GDPR Right to Erasure](https://gdpr-info.eu/art-17-gdpr/)
- [Gravatar API](https://en.gravatar.com/site/implement/)

## 🧪 Testing

- [ ] Unit tests para CRUD operations
- [ ] Integration test: crear profile completo
- [ ] Integration test: delete account (cascade)
- [ ] UI test: address form validation
- [ ] UI test: payment method tokenization

## 🚨 Data Privacy

**GDPR Compliance:**
- [ ] User consent para almacenar payment methods
- [ ] Privacy policy actualizada
- [ ] Delete account elimina:
  - User data
  - Addresses
  - Payment methods (revoke en Stripe)
  - Wishlist
  - Transacciones anonimizadas (keep for records, remove PII)

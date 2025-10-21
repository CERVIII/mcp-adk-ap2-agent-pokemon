---
title: "[Phase 5.3] PCI-DSS Compliance & Security Audit"
labels: security, compliance, critical, phase-5
assignees: CERVIII
---

## 📋 Descripción

Asegurar cumplimiento con PCI-DSS Level 1 para procesamiento seguro de tarjetas, implementar tokenización, auditoría de seguridad, y mejores prácticas.

## 🎯 Tipo de Issue

- [x] 🔐 Seguridad CRÍTICA
- [x] 📋 Compliance
- [x] 🧪 Auditoría

## 📦 Fase del Roadmap

**Fase 5.3: Cumplimiento PCI-DSS**

## ✅ Tareas

### PCI-DSS Requirements (12 Principles)

#### 1. Build and Maintain Secure Network
- [ ] **Firewall Configuration**
  - [ ] UFW/iptables configurado en server
  - [ ] Solo puertos necesarios abiertos (80, 443, 22)
  - [ ] Fail2ban para prevenir brute-force
  
- [ ] **No Default Passwords**
  - [ ] Todas contraseñas por defecto cambiadas
  - [ ] Database credentials únicos y complejos
  - [ ] SSH key authentication (disable password login)

#### 2. Protect Cardholder Data
- [ ] **Data Encryption**
  - [ ] TLS 1.2+ para toda comunicación (HTTPS obligatorio)
  - [ ] Database encryption at rest (SQLCipher o AWS RDS encryption)
  - [ ] Backup encryption con GPG
  
- [ ] **Tokenization**
  - [ ] NUNCA almacenar full PAN (Primary Account Number)
  - [ ] Usar Stripe Payment Methods API (tokens únicos)
  - [ ] Solo almacenar: last 4 digits, expiration, brand
  
```python
# ❌ NUNCA HACER ESTO
card_number = "4242424242424242"
db.save(card_number)

# ✅ CORRECTO
payment_method = stripe.PaymentMethod.create(type="card", card={...})
db.save({
    "stripe_pm_id": payment_method.id,  # pm_1ABC...
    "last_four": payment_method.card.last4,
    "brand": payment_method.card.brand
})
```

#### 3. Vulnerability Management
- [ ] **Anti-Virus**
  - [ ] ClamAV instalado en server
  - [ ] Scans automáticos diarios
  
- [ ] **Secure Software**
  - [ ] Dependabot habilitado en GitHub
  - [ ] `npm audit` y `pip-audit` en CI/CD
  - [ ] Actualizar librerías regularmente
  
```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Python Security Scan
        run: |
          pip install pip-audit
          pip-audit
      - name: NPM Audit
        run: npm audit --audit-level=high
      - name: Snyk Scan
        uses: snyk/actions/python@master
```

#### 4. Implement Strong Access Controls
- [ ] **Need-to-Know Basis**
  - [ ] Roles: Admin, Manager, Customer
  - [ ] Admin puede ver full payment logs
  - [ ] Customer solo ve sus propias transacciones
  
- [ ] **Unique IDs**
  - [ ] Cada user tiene ID único
  - [ ] Session IDs rotados después de login
  - [ ] API keys rotadas cada 90 días
  
- [ ] **Physical Access**
  - [ ] Server en datacenter seguro (AWS, GCP)
  - [ ] No production data en laptops de desarrollo

#### 5. Monitor and Test Networks
- [ ] **Logging**
  - [ ] Logs de todos access attempts
  - [ ] Logs de payment transactions
  - [ ] Log retention: 1 año mínimo
  
```python
import logging

payment_logger = logging.getLogger("payment")
payment_logger.info(f"Payment initiated: user={user_id}, amount={amount}, method={method}")
payment_logger.info(f"Payment succeeded: payment_id={payment.id}, stripe_id={stripe_id}")
```

- [ ] **Log Analysis**
  - [ ] Elasticsearch + Kibana (ELK stack)
  - [ ] Alertas para patrones sospechosos
  - [ ] Failed login attempts > 5 → IP ban
  
- [ ] **Penetration Testing**
  - [ ] Quarterly security audits
  - [ ] Vulnerability scanning con OWASP ZAP
  - [ ] Bug bounty program (opcional)

#### 6. Maintain Security Policy
- [ ] **Security Policy Document**
  - [ ] `SECURITY.md` en repositorio
  - [ ] Responsible disclosure policy
  - [ ] Incident response plan
  
- [ ] **Employee Training**
  - [ ] Todos developers conocen PCI-DSS basics
  - [ ] Anual security training
  - [ ] Phishing awareness

### Tokenization Implementation

#### Database Schema
```sql
-- ❌ NUNCA almacenar esto
CREATE TABLE payment_cards_WRONG (
    card_number VARCHAR(16),  -- VIOLACIÓN PCI-DSS
    cvv VARCHAR(3),           -- VIOLACIÓN PCI-DSS
    expiration VARCHAR(5)
);

-- ✅ CORRECTO
CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    stripe_payment_method_id VARCHAR(100),  -- Token
    last_four VARCHAR(4),                   -- Solo últimos 4
    brand VARCHAR(20),                      -- 'visa', 'mastercard'
    exp_month INTEGER,
    exp_year INTEGER,
    billing_zip VARCHAR(10),
    is_default BOOLEAN,
    created_at TIMESTAMP
);
```

#### Payment Method Creation
```python
@app.post("/api/payment-methods")
async def add_payment_method(
    token: str,  # Stripe token from frontend
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create PaymentMethod in Stripe
    payment_method = stripe.PaymentMethod.attach(
        token,
        customer=current_user.stripe_customer_id
    )
    
    # Store ONLY token and metadata
    pm = PaymentMethod(
        user_id=current_user.id,
        stripe_payment_method_id=payment_method.id,
        last_four=payment_method.card.last4,
        brand=payment_method.card.brand,
        exp_month=payment_method.card.exp_month,
        exp_year=payment_method.card.exp_year
    )
    db.add(pm)
    db.commit()
    
    return {"id": pm.id, "last_four": pm.last_four}
```

### HTTPS/TLS Configuration

#### Nginx SSL
```nginx
server {
    listen 443 ssl http2;
    server_name pokemart.example.com;
    
    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/pokemart.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pokemart.example.com/privkey.pem;
    
    # TLS Configuration (PCI-DSS compliant)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    
    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Other security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name pokemart.example.com;
    return 301 https://$host$request_uri;
}
```

### Secure Logging

#### Log Sanitization
```python
import re

def sanitize_log_data(data: dict) -> dict:
    """Remove sensitive data from logs"""
    sensitive_fields = ["card_number", "cvv", "password", "secret"]
    
    sanitized = data.copy()
    for key in sanitized:
        if key in sensitive_fields:
            sanitized[key] = "***REDACTED***"
        # Mask email
        if key == "email":
            sanitized[key] = mask_email(sanitized[key])
        # Mask phone
        if key == "phone":
            sanitized[key] = mask_phone(sanitized[key])
    
    return sanitized

def mask_email(email: str) -> str:
    """user@example.com → u***@example.com"""
    local, domain = email.split("@")
    return f"{local[0]}***@{domain}"

# Usage
payment_logger.info(sanitize_log_data({
    "user_id": 123,
    "amount": 51.00,
    "card_number": "4242424242424242",  # Will be redacted
    "email": "ash@pokemon.com"  # Will be masked
}))
```

### Database Encryption

#### SQLCipher (SQLite encryption)
```python
from sqlalchemy import create_engine

# Encrypted database
engine = create_engine(
    "sqlite+pysqlcipher:///database.db?cipher=aes-256-cfb&kdf_iter=64000",
    connect_args={"check_same_thread": False, "key": DB_ENCRYPTION_KEY}
)
```

#### Backup Encryption
```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_FILE="backup_${DATE}.sql"

# Dump database
sqlite3 database.db .dump > $BACKUP_FILE

# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 --output ${BACKUP_FILE}.gpg $BACKUP_FILE

# Remove plaintext
rm $BACKUP_FILE

# Upload to S3 (encrypted at rest)
aws s3 cp ${BACKUP_FILE}.gpg s3://backups/pokemon/ --sse AES256
```

### Rate Limiting & DDoS Protection

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/cart/checkout")
@limiter.limit("5/minute")  # Max 5 checkout attempts per minute
async def checkout(request: Request, ...):
    pass

@app.post("/api/auth/login")
@limiter.limit("10/hour")  # Max 10 login attempts per hour
async def login(request: Request, ...):
    pass
```

### Intrusion Detection

#### Fail2Ban Configuration
```ini
# /etc/fail2ban/jail.local
[fastapi-auth]
enabled = true
port = http,https
filter = fastapi-auth
logpath = /var/log/pokemon/app.log
maxretry = 5
bantime = 3600  # 1 hour ban

# /etc/fail2ban/filter.d/fastapi-auth.conf
[Definition]
failregex = ^.*Login failed.*ip=<HOST>.*$
ignoreregex =
```

## 📝 Criterios de Aceptación

- [ ] HTTPS enabled con TLS 1.2+
- [ ] No PAN almacenado (solo tokens)
- [ ] Logs sanitizados
- [ ] Database encryption
- [ ] Rate limiting implementado
- [ ] Security headers configurados
- [ ] Vulnerability scanning automated
- [ ] PCI-DSS SAQ (Self-Assessment Questionnaire) completado

## 🧪 Security Testing

### Automated Scans
```bash
# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://pokemart.example.com

# Nmap port scan
nmap -sV -sC pokemart.example.com

# SSL Labs test
https://www.ssllabs.com/ssltest/analyze.html?d=pokemart.example.com
```

### Manual Testing
- [ ] SQL injection attempts
- [ ] XSS attempts
- [ ] CSRF token validation
- [ ] Session hijacking tests
- [ ] Authentication bypass tests

## ⏱️ Estimación

**Tiempo:** 2-3 semanas
**Prioridad:** CRÍTICA (legal requirement)
**Complejidad:** Very High

## 🔗 Issues Relacionados

Depende de: #phase-5-1-stripe-integration, #phase-5-2-alternative-payments
Prerequisito para: Production deployment
Relacionado con: #phase-4-3-real-authorization

## 📚 Recursos

- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/document_library)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Stripe Security Best Practices](https://stripe.com/docs/security/guide)
- [Let's Encrypt](https://letsencrypt.org/)
- [SSL Labs](https://www.ssllabs.com/)

## 🚨 CRITICAL Reminders

**NUNCA:**
- ❌ Almacenar full card numbers
- ❌ Almacenar CVV
- ❌ Transmitir datos sin TLS
- ❌ Log sensitive data
- ❌ Usar HTTP en producción

**SIEMPRE:**
- ✅ Usar Stripe tokenization
- ✅ HTTPS everywhere
- ✅ Sanitize logs
- ✅ Encrypt databases
- ✅ Rate limit endpoints
- ✅ Monitor for anomalies

## 📋 PCI-DSS Compliance Checklist

- [ ] Requirement 1: Firewall ✅
- [ ] Requirement 2: No defaults ✅
- [ ] Requirement 3: Protect data ✅
- [ ] Requirement 4: Encrypt transmission ✅
- [ ] Requirement 5: Anti-virus ✅
- [ ] Requirement 6: Secure code ✅
- [ ] Requirement 7: Access control ✅
- [ ] Requirement 8: Unique IDs ✅
- [ ] Requirement 9: Physical access ✅
- [ ] Requirement 10: Logging ✅
- [ ] Requirement 11: Testing ✅
- [ ] Requirement 12: Security policy ✅

## 💰 Compliance Costs

- SSL Certificate: FREE (Let's Encrypt)
- PCI Compliance Scanning: $50-200/month
- Security Audit: $5,000-10,000/year
- Bug Bounty: Variable
- Insurance: $1,000-5,000/year

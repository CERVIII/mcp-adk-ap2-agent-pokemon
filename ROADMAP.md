# 🗺️ Pokemon MCP + AP2 - Roadmap

Hoja de ruta para el desarrollo del proyecto Pokemon Marketplace con MCP y AP2.

---

## 📍 Estado Actual (v3.0)

### ✅ Completado

- ✅ MCP Server con 6 tools funcionales
- ✅ Integración con PokeAPI
- ✅ Catálogo local de 151 Pokemon Gen 1
- ✅ Shopping Web UI completa
- ✅ Shopping cart con persistencia en memoria
- ✅ 4 agentes AP2 (Shopping, Merchant, Credentials, Processor)
- ✅ JWT RS256 implementation (merchant signature + user authorization)
- ✅ Flujo completo de pago AP2
- ✅ Imágenes de Pokemon en todas las vistas
- ✅ Búsqueda avanzada con filtros
- ✅ Documentación completa (todos los READMEs)

### ⚠️ Limitaciones Conocidas

- ~~Merchant signature desde Python (debería venir del MCP server)~~ ✅ RESUELTO en v3.0
- ~~Claves RSA generadas al inicio (no persistentes)~~ ✅ RESUELTO en v3.1
- ~~Sin validación de firmas JWT~~ ✅ RESUELTO en v3.2
- Carrito solo en memoria (se pierde al reiniciar)
- Sin autenticación de usuarios
- Sin persistencia de transacciones
- Payment processor simulado (no real)

---

## 🎯 Roadmap por Fases

### 🔴 Fase 1: Estabilización y Seguridad (CRÍTICO)
**Objetivo**: Hacer el sistema production-ready básico  
**Duración estimada**: 2-3 semanas

### 🔴 Fase 1: Estabilización y Seguridad (CRÍTICO)
**Objetivo**: Hacer el sistema production-ready básico  
**Duración estimada**: 2-3 semanas

#### ✅ 1.1 JWT Signatures desde MCP Server ⭐ COMPLETADO
- [x] Mover generación de merchant_signature al MCP server (TypeScript)
- [x] Generar claves RSA en TypeScript y exportar pública
- [x] Actualizar `create_pokemon_cart` tool para retornar JWT real
- [x] Verificar que merchant_signature tenga 3 partes (header.payload.signature)
- [x] Tests unitarios de JWT generation en TypeScript (`test_jwt_signature.py`)

**✅ COMPLETADO**: El merchant signature ahora es un JWT RS256 real generado en TypeScript con todos los claims correctos (iss, sub, iat, exp, cart_id, merchant).

**Verificado**:
- JWT con 3 partes: header.payload.signature
- Algoritmo: RS256
- Firma criptográfica de 594 caracteres (antes: 30 chars mock)
- Claims válidos: issuer="PokeMart", expiration=3600s, cart_id incluido

#### ✅ 1.2 Persistencia de Claves RSA ⭐ COMPLETADO
- [x] Guardar claves privadas en archivos seguros (`merchant_key.pem`, `user_key.pem`)
- [x] Cargar claves al inicio (no regenerar cada vez)
- [x] Exportar claves públicas para validación
- [x] Documentar rotación de claves

**✅ COMPLETADO**: Las claves RSA ahora persisten en disco (mcp-server/keys/). El servidor carga las claves existentes al iniciar o genera nuevas si no existen.

**Verificado**:
- Claves guardadas en mcp-server/keys/ con permisos seguros (600/644)
- loadOrGenerateRSAKeys() carga claves existentes o genera nuevas
- Claves consistentes entre reinicios
- Test automatizado (test_rsa_persistence.py) valida todo el flujo
- Documentación completa en keys/README.md

**Beneficio**: Las firmas son consistentes entre reinicios, permitiendo validación futura.

#### ✅ 1.3 Validación de Firmas JWT ⭐ COMPLETADO
- [x] Implementar verificación de merchant_signature en Shopping Agent
- [x] Validar user_authorization en Payment Processor
- [x] Usar claves públicas para verificar
- [x] Rechazar mandates con firmas inválidas
- [x] Logging de intentos de validación fallidos

**✅ COMPLETADO**: Los agentes ahora validan todas las firmas JWT antes de procesar transacciones.

**Verificado**:
- JWTValidator class carga claves públicas del MCP server
- Shopping Agent valida merchant_signature antes de aceptar CartMandate
- Payment Processor valida user_authorization antes de procesar pago
- Detección de tampering mediante verificación de hashes
- JWTs expirados, malformados o inválidos son rechazados
- Test suite completo (test_jwt_validation.py) con 6 tests pasando

**Seguridad**: Sistema ahora detecta y rechaza CartMandates o PaymentMandates falsificados.

#### 1.4 Base de Datos para Transacciones
- [ ] Setup PostgreSQL o SQLite
- [ ] Schema para transacciones (cart_id, payment_id, status, items, total)
- [ ] Schema para inventario (actualizar stock)
- [ ] Migrar pokemon-gen1.json a DB
- [ ] API endpoints para consultar historial

**Beneficio**: Auditoría completa de todas las transacciones.

---

### 🟡 Fase 2: Mejoras de Experiencia de Usuario
**Objetivo**: Hacer la Web UI más profesional  
**Duración estimada**: 2 semanas

#### 2.1 Persistencia del Carrito
- [ ] Guardar carrito en localStorage (frontend)
- [ ] O en base de datos con session ID
- [ ] Recuperar carrito al recargar página
- [ ] Mostrar tiempo de expiración del carrito

#### 2.2 Mejoras de UI/UX
- [ ] Loading states cuando carga Pokemon (spinners)
- [ ] Paginación para resultados de búsqueda
- [ ] Ordenar por: precio, nombre, número, popularidad
- [ ] Filtros múltiples combinados (tipo + rango precio)
- [ ] Modal de confirmación antes de checkout
- [ ] Animaciones suaves (transitions CSS)
- [ ] Modo oscuro/claro (theme switcher)

#### 2.3 Vista de Detalles Mejorada
- [ ] Modal o página dedicada para cada Pokemon
- [ ] Mostrar evoluciones
- [ ] Mostrar estadísticas en gráficos
- [ ] Comparar Pokemon (vs mode)
- [ ] Reviews o ratings simulados

#### 2.4 Historial de Compras
- [ ] Página de "Mis Compras"
- [ ] Ver transacciones pasadas
- [ ] Descargar recibos en PDF
- [ ] Re-comprar items anteriores

---

### 🟢 Fase 3: Expansión del Catálogo
**Objetivo**: Más Pokemon y productos  
**Duración estimada**: 1-2 semanas

#### 3.1 Generaciones 2-9
- [ ] Expandir pokemon-gen1.json a todas las generaciones
- [ ] Actualizar límites en MCP server (1-1025 Pokemon)
- [ ] Generar precios e inventario para nuevos Pokemon
- [ ] Filtrar por generación en búsqueda

#### 3.2 Categorías de Productos
- [ ] Shiny variants (precios más altos)
- [ ] Pokemon Items (pokeballs, potions, TMs)
- [ ] Mega evolutions
- [ ] Regional forms (Alola, Galar, etc.)

#### 3.3 Promociones y Descuentos
- [ ] Sistema de cupones
- [ ] Descuentos por cantidad
- [ ] Ofertas limitadas por tiempo
- [ ] Bundle deals (compra 3, paga 2)

---

### 🔵 Fase 4: Autenticación y Usuarios
**Objetivo**: Multi-usuario real  
**Duración estimada**: 2-3 semanas

#### 4.1 Sistema de Autenticación
- [ ] OAuth2 con Google/GitHub
- [ ] JWT para sesiones de usuario
- [ ] Login/Logout en Web UI
- [ ] Registro de nuevos usuarios

#### 4.2 Perfiles de Usuario
- [ ] Base de datos de usuarios
- [ ] Preferencias personalizadas
- [ ] Dirección de envío
- [ ] Métodos de pago guardados (tokenizados)
- [ ] Wishlist de Pokemon

#### 4.3 User Authorization Real
- [ ] user_authorization firmado en dispositivo del usuario
- [ ] WebAuthn/FIDO2 para firma biométrica
- [ ] 2FA opcional
- [ ] Verificación de email

---

### 🟣 Fase 5: Integración de Pagos Real
**Objetivo**: Procesar pagos reales  
**Duración estimada**: 3-4 semanas

#### 5.1 Stripe Integration
- [ ] Cuenta de Stripe (sandbox primero)
- [ ] Payment Intents API
- [ ] Webhooks para confirmaciones
- [ ] Manejo de 3D Secure
- [ ] Reembolsos

#### 5.2 Métodos de Pago Alternativos
- [ ] PayPal
- [ ] Apple Pay / Google Pay
- [ ] Criptomonedas (opcional)
- [ ] Transferencia bancaria

#### 5.3 Cumplimiento PCI DSS
- [ ] Nunca almacenar datos de tarjetas
- [ ] Usar tokens de Stripe
- [ ] HTTPS obligatorio
- [ ] Logging seguro (no logs de tarjetas)
- [ ] Auditoría de seguridad

---

### 🟠 Fase 6: A2A Protocol Completo
**Objetivo**: Comunicación real entre agentes  
**Duración estimada**: 2-3 semanas

#### 6.1 Discovery Protocol
- [ ] Agent registry/directory
- [ ] Well-known endpoints (.well-known/agent-card.json)
- [ ] Agent capabilities negotiation
- [ ] Service discovery dinámico

#### 6.2 IntentMandates
- [ ] Compras autónomas del agente
- [ ] Budget limits
- [ ] Pre-autorización de compras
- [ ] Notificaciones al usuario

#### 6.3 Multi-Merchant Support
- [ ] Conectar con múltiples merchants
- [ ] Comparar precios entre merchants
- [ ] Routing de pagos
- [ ] Merchant reputation system

---

### ⚫ Fase 7: Características Avanzadas
**Objetivo**: Diferenciadores competitivos  
**Duración estimada**: Variable

#### 7.1 Recomendaciones con IA
- [ ] Sistema de recomendaciones basado en compras
- [ ] "Los que compraron esto también compraron..."
- [ ] Chatbot para ayuda en selección
- [ ] Búsqueda por lenguaje natural mejorada

#### 7.2 Trading/Marketplace Social
- [ ] Usuarios pueden vender Pokemon
- [ ] Sistema de trades entre usuarios
- [ ] Reseñas y ratings
- [ ] Leaderboards

#### 7.3 Gamificación
- [ ] Puntos por compras
- [ ] Badges/Achievements
- [ ] Niveles de trainer
- [ ] Recompensas por fidelidad

#### 7.4 Mobile App
- [ ] React Native o Flutter
- [ ] Push notifications
- [ ] Offline mode
- [ ] QR codes para checkout rápido

#### 7.5 Analytics y Reporting
- [ ] Dashboard de ventas
- [ ] Métricas de usuarios
- [ ] Reportes de inventario
- [ ] A/B testing

---

## 🚀 Quick Wins (Implementación Rápida)

Cosas que puedes hacer **HOY** con alto impacto:

### 1. Fix Merchant Signature (1-2 horas)
```bash
# En mcp-server/src/index.ts
# Mover la generación de JWT del Python al TypeScript
```
**Impacto**: ⭐⭐⭐⭐⭐ Sistema más coherente y correcto

### 2. Persistir Carrito en localStorage (30 min)
```javascript
// En el frontend, guardar cart en localStorage
localStorage.setItem('pokemon_cart', JSON.stringify(cart));
```
**Impacto**: ⭐⭐⭐⭐ UX mucho mejor

### 3. Loading Spinners (20 min)
```html
<div class="spinner">Cargando Pokemon...</div>
```
**Impacto**: ⭐⭐⭐ Feedback visual para el usuario

### 4. Validación de Stock (30 min)
```python
# Verificar stock antes de añadir al carrito
if quantity > available_stock:
    raise HTTPException(400, "Stock insuficiente")
```
**Impacto**: ⭐⭐⭐⭐ Previene errores en checkout

### 5. Configurar SQLite (1 hora)
```python
import sqlite3
# Migrar pokemon-gen1.json a SQLite
```
**Impacto**: ⭐⭐⭐⭐⭐ Base para muchas features futuras

---

## 📊 Priorización Recomendada

### Semana 1-2: Estabilización
1. ✅ Fix merchant signature en MCP server ← **COMPLETADO**
2. Persistir claves RSA a archivos
3. Setup SQLite básico
4. Validación de stock

### Semana 3-4: UX Básico
1. ✅ Persistencia de carrito
2. ✅ Loading states
3. ✅ Historial de compras
4. ✅ Mejoras visuales

### Mes 2: Catálogo
1. ✅ Agregar más generaciones
2. ✅ Categorías de productos
3. ✅ Sistema de búsqueda mejorado

### Mes 3: Usuarios
1. ✅ Autenticación OAuth2
2. ✅ Perfiles de usuario
3. ✅ User authorization real

### Mes 4+: Pagos y A2A
1. ✅ Stripe integration
2. ✅ A2A protocol completo
3. ✅ Features avanzadas

---

## 🎯 OKRs (Objectives & Key Results)

### Q1 2026: Foundation
**Objetivo**: Sistema estable y seguro

**KRs**:
- ✅ 100% de transacciones con JWT válido
- ✅ Base de datos implementada
- ✅ 0 errores críticos en producción
- ✅ Documentación completa

### Q2 2026: Growth
**Objetivo**: Expandir catálogo y usuarios

**KRs**:
- ✅ 1000+ Pokemon disponibles
- ✅ 100+ usuarios registrados
- ✅ 50+ transacciones reales
- ✅ 4.5+ rating en UX

### Q3 2026: Scale
**Objetivo**: Multi-merchant y pagos reales

**KRs**:
- ✅ 3+ merchants integrados
- ✅ Stripe live mode activo
- ✅ PCI DSS compliant
- ✅ 1000+ transacciones/mes

---

## 🛠️ Tech Stack Evolution

### Actual (v3.0)
```
Frontend: HTML + CSS + Vanilla JS
Backend: FastAPI + Python 3.14
MCP: TypeScript + Node.js
Database: JSON file (pokemon-gen1.json)
Auth: None
Payments: Simulado
```

### Target (v5.0)
```
Frontend: React + TypeScript + TailwindCSS
Backend: FastAPI + Python 3.14 + SQLAlchemy
MCP: TypeScript + Node.js
Database: PostgreSQL
Auth: OAuth2 + JWT
Payments: Stripe + PayPal
Cache: Redis
Queue: Celery
Monitoring: Sentry + Grafana
```

---

## 📚 Recursos de Aprendizaje

### Para JWT y Seguridad
- [JWT.io](https://jwt.io/) - Debugger de JWT
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PCI DSS Standards](https://www.pcisecuritystandards.org/)

### Para AP2 Protocol
- [AP2 Specification](https://google-agentic-commerce.github.io/AP2/)
- [A2A Protocol](https://a2a-protocol.org/)

### Para Stripe
- [Stripe Docs](https://stripe.com/docs)
- [Stripe Elements](https://stripe.com/docs/payments/elements)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)

### Para React (si migras frontend)
- [React Docs](https://react.dev/)
- [Next.js](https://nextjs.org/) - SSR framework
- [TailwindCSS](https://tailwindcss.com/)

---

## 🐛 Known Issues a Resolver

1. **Merchant signature no es JWT real** → Fase 1.1
2. **Carrito se pierde al recargar** → Fase 2.1
3. **Sin validación de firmas** → Fase 1.3
4. **Stock no se actualiza en DB** → Fase 1.4
5. **Solo Gen 1 Pokemon** → Fase 3.1
6. **No hay autenticación** → Fase 4
7. **Pagos simulados** → Fase 5

---

## 🎓 Habilidades a Desarrollar

Para completar el roadmap necesitarás:

- [x] TypeScript (ya tienes)
- [x] Python (ya tienes)
- [x] FastAPI (ya tienes)
- [ ] **PostgreSQL/SQLAlchemy** - Para persistencia
- [ ] **OAuth2/JWT** - Para autenticación
- [ ] **Stripe API** - Para pagos
- [ ] **React** (opcional) - Para mejor frontend
- [ ] **Docker** - Para deployment
- [ ] **GitHub Actions** - Para CI/CD
- [ ] **Testing** - pytest, jest

---

## 🤝 Contribuciones Bienvenidas

Si esto fuera open source, áreas donde se necesitaría ayuda:

- 🎨 **UI/UX Design** - Mejorar la interfaz
- 🔐 **Security** - Auditoría de seguridad
- 📱 **Mobile** - App nativa
- 🌍 **i18n** - Internacionalización
- 📖 **Documentation** - Tutoriales y ejemplos
- 🧪 **Testing** - Cobertura de tests

---

## 📈 Métricas de Éxito

### Técnicas
- ✅ 95%+ uptime
- ✅ <200ms response time
- ✅ 80%+ code coverage
- ✅ 0 critical vulnerabilities

### Negocio
- ✅ 100+ usuarios activos/mes
- ✅ 500+ transacciones/mes
- ✅ 90%+ checkout completion rate
- ✅ <5% error rate

### Satisfacción
- ✅ 4.5+ stars rating
- ✅ <2s load time
- ✅ 60%+ return users
- ✅ 3+ avg items per order

---

## 🚦 Siguiente Paso Recomendado

### 👉 HAZLO AHORA: Fix Merchant Signature

**Por qué**: Es el issue más crítico que afecta la arquitectura.

**Cómo**:
1. Agregar `jsonwebtoken` a mcp-server/package.json
2. Generar RSA keys en TypeScript
3. Firmar CartMandate en `create_pokemon_cart` tool
4. Quitar generación de firma del Python
5. Test que JWT tenga 3 partes

**Tiempo**: 1-2 horas  
**Dificultad**: Media  
**Impacto**: ⭐⭐⭐⭐⭐

```bash
# Paso 1: Install dependencies
cd mcp-server
npm install jsonwebtoken @types/jsonwebtoken

# Paso 2: Editar src/index.ts y agregar JWT generation

# Paso 3: Test
npm run build
python tests/test_get_cart.py
```

---

**Versión**: 1.1  
**Última actualización**: 22 de Enero de 2025  
**Autor**: CERVIII

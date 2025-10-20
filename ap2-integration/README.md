# Pokemon AP2 Integration

Esta carpeta contiene la implementación completa del protocolo **AP2 (Agent Payments Protocol)** para el marketplace de Pokemon.

## 🏗️ Arquitectura

```
┌─────────────────┐
│   User/Claude   │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│     Shopping Agent (Port 8000)       │  ← Orquestador principal
│  - Interactúa con usuario            │
│  - Llama MCP tools (catálogo)        │
│  - Coordina con otros agentes        │
└──────────┬───────────────────────────┘
           │
           ├──────────────────────────────┐
           │                              │
           ▼                              ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│  Merchant Agent (8001)  │    │ Credentials Provider    │
│  - Gestiona CartMandates│    │      (Port 8002)        │
│  - Valida inventario    │    │  - Métodos de pago      │
│  - Firma carritos       │    │  - Tokens de pago       │
└──────────┬──────────────┘    └─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│ Payment Processor (8003)│
│  - Procesa pagos        │
│  - Valida mandatos      │
└─────────────────────────┘
```

## 🔑 Conceptos Clave de AP2

### Verifiable Digital Credentials (VDCs)

1. **CartMandate**: Carrito firmado por el merchant con productos y precio exacto
   - Ya implementado en tu MCP server (`create_pokemon_cart`)
   - Contiene: items, precios, merchant_signature, timestamp

2. **PaymentMandate**: Autorización de pago del usuario
   - Contiene: método de pago, shipping, autorización del usuario
   - Se firma en "trusted surface" (ej: dispositivo del usuario)

3. **IntentMandate**: Para compras autónomas (futuro, no en este proyecto)

### Flujo de Compra (Human-Present)

1. Usuario: "Quiero comprar un Pikachu"
2. Shopping Agent busca en catálogo (vía MCP)
3. Merchant Agent crea CartMandate firmado
4. Shopping Agent solicita métodos de pago
5. Credentials Provider devuelve opciones
6. Usuario selecciona método y confirma
7. Se crea PaymentMandate
8. Payment Processor ejecuta el pago
9. Usuario recibe recibo

## 📁 Estructura

```
ap2-integration/
├── src/
│   ├── common/                  # Utilidades compartidas
│   │   ├── ap2_types.py        # Tipos AP2 (CartMandate, PaymentMandate, etc)
│   │   ├── mcp_client.py       # Cliente para conectar con MCP server
│   │   └── utils.py            # Helpers generales
│   │
│   ├── shopping_agent/         # Shopping Agent (ADK/Gemini)
│   │   ├── __main__.py         # Entry point
│   │   ├── agent.py            # Lógica del agente
│   │   ├── web_ui.py           # 🌟 FastAPI Web UI
│   │   └── tools.py            # Tools específicas
│   │
│   ├── merchant_agent/         # Merchant Agent (FastAPI)
│   │   ├── __main__.py
│   │   ├── server.py           # API endpoints
│   │   └── cart_manager.py    # Gestión de carritos
│   │
│   ├── credentials_provider/   # Credentials Provider (FastAPI)
│   │   ├── __main__.py
│   │   └── server.py           # Métodos de pago simulados
│   │
│   ├── payment_processor/      # Payment Processor (FastAPI)
│   │   ├── __main__.py
│   │   └── server.py           # Procesamiento de pagos
│   │
│   └── common/                 # Utilidades compartidas
│       ├── ap2_types.py        # Tipos AP2 (CartMandate, PaymentMandate, etc)
│       ├── mcp_client.py       # Cliente para conectar con MCP server
│       └── utils.py            # 🔐 JWT RS256 generation
│
├── pyproject.toml              # Dependencias (incluye pyjwt, cryptography)
├── .env.example                # Variables de entorno
└── README.md                   # Esta documentación
```

## 🔐 JWT Implementation (RS256)

Este proyecto implementa **firmas digitales reales** usando JWT con algoritmo RS256:

### Merchant Signature (CartMandate)

```python
# En utils.py - Generación de claves RSA 2048-bit
MERCHANT_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# JWT firmado con RS256
def generate_merchant_signature(cart_id: str) -> str:
    payload = {
        "iss": "PokeMart",              # Issuer
        "sub": cart_id,                 # Subject (cart ID)
        "iat": int(now.timestamp()),    # Issued at
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "cart_id": cart_id,
        "merchant": "PokeMart - Primera Generación"
    }
    return jwt.encode(payload, MERCHANT_PRIVATE_PEM, algorithm="RS256")
```

### User Authorization (PaymentMandate)

```python
# JWT-VC (Verifiable Credential) firmado por el usuario
def generate_user_authorization(cart_hash: str, payment_hash: str) -> str:
    payload = {
        "iss": "user_device",
        "sub": "trainer@pokemon.com",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
        "cart_hash": cart_hash,
        "payment_hash": payment_hash,
        "vc": {  # Verifiable Credential
            "type": ["VerifiableCredential", "PaymentAuthorization"],
            "credentialSubject": {
                "id": "did:example:user123",
                "cart_hash": cart_hash,
                "payment_hash": payment_hash,
                "consent": "explicit"
            }
        }
    }
    return jwt.encode(payload, USER_PRIVATE_PEM, algorithm="RS256")
```

**Características**:
- ✅ RSA 2048-bit private keys
- ✅ RS256 algorithm (RSA + SHA-256)
- ✅ Proper expiration times (1h merchant, 15min user)
- ✅ Verifiable Credential format (JWT-VC)
- ✅ Complete claims structure

## 🌐 Web UI - Shopping Interface

El Shopping Agent incluye una **interfaz web completa** para comprar Pokemon:

### Características de la Web UI

- **Catálogo visual**: Lista de Pokemon con imágenes y detalles
- **Búsqueda avanzada**: Por nombre, tipo, precio, disponibilidad
- **Shopping cart**: Agregar/remover items, persistente
- **Checkout AP2**: Flujo completo de pago con CartMandate/PaymentMandate
- **Responsive design**: Interfaz moderna con CSS personalizado

### Endpoints disponibles

```
GET  /                      # Interfaz web principal
GET  /api/search            # Buscar Pokemon
POST /api/cart/add          # Agregar al carrito
GET  /api/cart              # Ver carrito actual
POST /api/cart/checkout     # Procesar pago (AP2)
DELETE /api/cart/clear      # Limpiar carrito
GET  /api/types             # Lista de tipos Pokemon
```

### Iniciar Web UI

```bash
# Desde la raíz del proyecto
./scripts/run-shopping-agent.sh

# O manualmente
cd ap2-integration
uv run python src/shopping_agent/web_ui.py

# Abrir en navegador
open http://localhost:8000
```

### Demo rápido

```bash
# GET /api/quick-demo - Compra automática de Pikachu
curl http://localhost:8000/api/quick-demo
```

## 🛠️ Estructura de Archivos (Actualizada)

## 🚀 Instalación

### 1. Requisitos previos

```bash
# Instalar uv (gestor de paquetes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh

# API Key de Google AI Studio
# Obtén tu key en: https://aistudio.google.com/apikey
```

### 2. Configurar entorno

```bash
cd ap2-integration

# Copiar .env de ejemplo
cp .env.example .env

# Editar .env y agregar tu GOOGLE_API_KEY
nano .env
```

### 3. Instalar dependencias

```bash
# Desde la raíz del proyecto
make setup

# O manualmente
uv sync
```

## 🎮 Uso

### Opción 1: Script automatizado (Recomendado)

```bash
# Desde la raíz del proyecto
./scripts/run-ap2-demo.sh
```

Este script:
- Inicia todos los agentes en terminales separadas
- Configura los puertos correctos
- Muestra logs en tiempo real

### Opción 2: Manual (para desarrollo)

```bash
# Terminal 1 - Merchant Agent
uv run python -m src.merchant_agent

# Terminal 2 - Credentials Provider
uv run python -m src.credentials_provider

# Terminal 3 - Payment Processor
uv run python -m src.payment_processor

# Terminal 4 - Shopping Agent (con UI)
uv run python -m src.shopping_agent
```

Luego abre: http://localhost:8000/dev-ui

### Opción 3: Desde Claude Desktop

1. El MCP server ya está configurado en `claude_desktop_config.json`
2. Reinicia Claude Desktop
3. Las tools de Pokemon estarán disponibles automáticamente
4. Ejemplo de prompt:

```
Quiero comprar un Pikachu. Búscalo, crea un carrito y procesa el pago.
```

## 🧪 Testing

```bash
# Test rápido de MCP
python tests/test_mcp_simple.py

# Test de creación de carrito
python tests/test_get_cart.py

# Test completo de integración
./tests/test_unified_mcp.sh
```

## 📚 Endpoints de los Agentes

### Merchant Agent (8001)

- `POST /a2a/merchant_agent/create_cart` - Crea CartMandate
- `GET /a2a/merchant_agent/cart/{cart_id}` - Obtiene carrito
- `GET /a2a/merchant_agent/.well-known/agent-card.json` - AgentCard

### Credentials Provider (8002)

- `GET /a2a/credentials_provider/payment_methods` - Lista métodos de pago
- `POST /a2a/credentials_provider/tokenize` - Tokeniza método de pago
- `GET /a2a/credentials_provider/.well-known/agent-card.json` - AgentCard

### Payment Processor (8003)

- `POST /a2a/processor/charge` - Procesa pago con PaymentMandate
- `POST /a2a/processor/validate` - Valida mandatos
- `GET /a2a/processor/.well-known/agent-card.json` - AgentCard

## 🔐 Seguridad (Simplificada para Demo)

⚠️ **NOTA**: Esta es una implementación de demostración. En producción deberías:

1. **Firmas reales**: Usar JWT/JWS con claves privadas reales
2. **Validación de firmas**: Verificar todas las signatures con claves públicas
3. **HTTPS**: Todos los endpoints deben usar TLS
4. **Autenticación**: OAuth2/OpenID Connect para usuarios
5. **Rate limiting**: Prevenir abuso
6. **PCI compliance**: Para datos de tarjetas reales
7. **Logging seguro**: No logear datos sensibles

Actualmente:
- Las firmas son simuladas (`sig_merchant_pokemon_xxx`)
- No hay validación criptográfica real
- HTTP en lugar de HTTPS
- Sin autenticación de usuarios

## 🐛 Troubleshooting

### Error: "Connection refused" al conectar con MCP server

```bash
# Verificar que el MCP server esté compilado
cd mcp-server
npm run build
```

### Error: "GOOGLE_API_KEY not found"

```bash
# Asegúrate de tener el .env configurado
cat ap2-integration/.env
# Debe contener: GOOGLE_API_KEY=tu_key_aqui
```

### Error: "Port already in use"

```bash
# Matar procesos en puertos específicos
lsof -ti:8000 | xargs kill -9  # Shopping Agent
lsof -ti:8001 | xargs kill -9  # Merchant Agent
lsof -ti:8002 | xargs kill -9  # Credentials Provider
lsof -ti:8003 | xargs kill -9  # Payment Processor
```

### Los agentes no se comunican

```bash
# Verificar que todos estén corriendo
curl http://localhost:8001/a2a/merchant_agent/.well-known/agent-card.json
curl http://localhost:8002/a2a/credentials_provider/.well-known/agent-card.json
curl http://localhost:8003/a2a/processor/.well-known/agent-card.json
```

## 📖 Referencias

- [AP2 Protocol Official Docs](https://ap2-protocol.org)
- [AP2 GitHub Repository](https://github.com/google-agentic-commerce/AP2)
- [MCP Protocol](https://modelcontextprotocol.io)
- [A2A Protocol](https://a2a-protocol.org)
- [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)

## 🤝 Contribuciones

Este proyecto está basado en:
- Google AP2 Protocol (Apache 2.0)
- Model Context Protocol (MIT)
- Datos de PokeAPI

## 📝 TODO / Roadmap

- [ ] Implementar IntentMandate (human-not-present)
- [ ] Agregar manejo de shipping/direcciones
- [ ] Implementar refunds/devoluciones
- [ ] Agregar persistencia (DB real en lugar de in-memory)
- [ ] Firmas criptográficas reales
- [ ] Tests unitarios completos
- [ ] UI web mejorada
- [ ] Soporte para múltiples currencies
- [ ] Integración con x402 protocol (stablecoins)

## 🔐 NOTA DE SEGURIDAD:
   Esta es una implementación de DEMOSTRACIÓN. Para producción necesitas:
- Firmas criptográficas reales (JWT/JWS)
- HTTPS en todos los endpoints
- Autenticación OAuth2/OIDC
- PCI compliance para tarjetas reales

## 📖 APRENDE MÁS:
- AP2 Protocol: https://ap2-protocol.org
- AP2 GitHub: https://github.com/google-agentic-commerce/AP2
- MCP Protocol: https://modelcontextprotocol.io

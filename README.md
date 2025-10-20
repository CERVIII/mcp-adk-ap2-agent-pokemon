# 🎮 Pokemon MCP + AP2 Agent

Marketplace de Pokemon implementando **Model Context Protocol (MCP)** con **Agent Payments Protocol (AP2)**. Sistema completo con servidor MCP, agentes inteligentes y flujo de pagos con JWT tokens reales.

## 🎯 Descripción

Este proyecto combina tres tecnologías clave:

- **🔧 MCP (Model Context Protocol)**: Servidor TypeScript que expone herramientas de Pokemon  
- **🤖 Google ADK**: Agentes conversacionales con Gemini 2.5 Flash  
- **💳 AP2 (Agent Payments Protocol)**: Protocolo completo de pagos entre agentes con JWT RS256

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                      Cliente MCP                             │
│        (Claude Desktop, GitHub Copilot, Shopping UI)         │
└─────────────────────────┬────────────────────────────────────┘
                          │ MCP Protocol (stdio)
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                   MCP Pokemon Server                         │
│                   Node.js/TypeScript                         │
│                                                              │
│  Tools:                        AP2 Features:                 │
│  • get_pokemon_info           • create_pokemon_cart          │
│  • get_pokemon_price          • get_pokemon_product          │
│  • search_pokemon                                            │
│  • list_pokemon_types                                        │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   │ APIs & Data
                   ▼
┌──────────────────┬──────────────────┐
│    PokeAPI       │ pokemon-gen1.json│
│ pokeapi.co/api   │ (151 Pokemon)    │
└──────────────────┴──────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    AP2 Integration                           │
│                    Python + FastAPI                          │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│Shopping Agent   │ │ Merchant Agent   │ │Payment Processor │
│Port 8000        │ │ Port 8001        │ │ Port 8003        │
│Web UI + Gemini  │ │ CartMandate      │ │ AP2 Processor    │
└─────────────────┘ └──────────────────┘ └──────────────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │Credentials       │
                   │Provider          │
                   │Port 8002         │
                   └──────────────────┘
```

## ✨ Características Principales

### 🛍️ Shopping Web UI
- **Interfaz visual completa** para comprar Pokemon  
- **Shopping cart** con add/remove/checkout  
- **Búsqueda avanzada** por nombre, tipo, precio, disponibilidad  
- **Vista de detalles** de cada Pokemon con sprites e información  
- **Integración AP2** con flujo de pago completo

### 🔐 JWT Tokens Reales (RS256)
- **Merchant Signature**: JWT firmado con clave privada RSA del merchant  
- **User Authorization**: JWT-VC (Verifiable Credential) firmado por usuario  
- **Algoritmo RS256**: RSA-SHA256 para máxima seguridad  
- **Claims completos**: iss, sub, iat, exp, cart_hash, payment_hash  
- **Expiración**: 1 hora (merchant), 15 minutos (user)

### 🤖 Agentes Inteligentes
- **Shopping Agent**: Asistente conversacional con Web UI  
- **Merchant Agent**: Gestión de catálogo y CartMandates  
- **Payment Processor**: Procesa transacciones AP2  
- **Credentials Provider**: Gestión de métodos de pago

### 🛠️ MCP Tools
- `get_pokemon_info` - Información desde PokeAPI (tipos, stats, habilidades)  
- `get_pokemon_price` - Precio e inventario local  
- `search_pokemon` - Búsqueda combinada con filtros  
- `list_pokemon_types` - Lista de tipos disponibles  
- `create_pokemon_cart` - **CartMandate AP2 con merchant signature JWT**  
- `get_pokemon_product` - Información completa de producto

## 📦 Estructura del Proyecto

```
mcp-adk-ap2-agent-pokemon/
├── README.md                          # Este archivo
├── pokemon-gen1.json                  # Catálogo de 151 Pokemon Gen 1
├── Makefile                           # Comandos de build
│
├── mcp-server/                        # Servidor MCP
│   ├── src/index.ts                   # Implementación completa
│   ├── build/                         # Código compilado
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md                      # Docs del servidor MCP
│
├── ap2-integration/                   # Implementación AP2
│   ├── src/
│   │   ├── common/                    # Utilidades
│   │   │   ├── utils.py              # JWT generation (RS256)
│   │   │   ├── ap2_types.py          # Modelos Pydantic
│   │   │   └── mcp_client.py         # Cliente MCP Python
│   │   ├── shopping_agent/
│   │   │   ├── agent.py              # Lógica del shopping agent
│   │   │   └── web_ui.py             # FastAPI web interface
│   │   ├── merchant_agent/
│   │   │   └── server.py             # Merchant AP2 agent
│   │   ├── payment_processor/
│   │   │   └── server.py             # Payment processor
│   │   └── credentials_provider/
│   │       └── server.py             # Credentials provider
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md                      # Docs de AP2
│
├── scripts/                           # Scripts de automatización
│   ├── setup.sh                       # Instalación completa
│   ├── run-ap2-agents.sh             # Inicia agentes AP2
│   ├── run-shopping-agent.sh         # Inicia shopping web UI
│   └── README.md
│
└── tests/                             # Tests
    ├── test_mcp.py                    # Test MCP completo
    ├── test_mcp_simple.py             # Test básico
    ├── test_unified_mcp.sh            # Test bash
    └── README.md
```

## 🚀 Instalación Rápida

### Requisitos Previos

- **Node.js** 18+ y npm
- **Python** 3.10+
- **uv** package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Google API Key** de [AI Studio](https://aistudio.google.com/apikey)

### Instalación con Make

```bash
# Instalación completa (recomendado)
make setup

# O manualmente:
./scripts/setup.sh
```

### Configuración de API Key

```bash
# Crear archivo .env
echo "GOOGLE_API_KEY=tu_api_key_aqui" > ap2-integration/.env
```

## 🎮 Guías de Uso

### Opción 1: Web UI (Más Visual) 🌟 **RECOMENDADO**

La forma más fácil de probar todo el sistema:

```bash
# Terminal 1: Iniciar agentes AP2 (Merchant, Credentials, Processor)
./scripts/run-ap2-agents.sh

# Terminal 2: Iniciar Shopping Web UI
./scripts/run-shopping-agent.sh

# Abrir en el navegador
open http://localhost:8000
```

**Características de la Web UI:**
- 🔍 Búsqueda de Pokemon con filtros  
- 🛒 Shopping cart persistente  
- 💳 Checkout con AP2 protocol  
- 📊 Vista de CartMandate y PaymentMandate  
- 🎨 Interfaz moderna y responsiva

### Opción 2: GitHub Copilot / Claude Desktop

Integración directa con tu editor:

```bash
# 1. El MCP server ya está configurado en .vscode/mcp.json
# 2. Reinicia GitHub Copilot: Ctrl+Shift+P → "Restart Chat"
# 3. Usa lenguaje natural:
```

**Ejemplos de prompts:**

```
"Busca pokemon de tipo fire por menos de 100 USD"
"Muéstrame información de Charizard"
"Añade 2 Pikachu al carrito"
"Crea un CartMandate con 3 Pokemon diferentes"
```

### Opción 3: Tests Rápidos

```bash
# Test simple del MCP server
python tests/test_mcp_simple.py

# Test completo
python tests/test_mcp.py

# Test bash
./tests/test_unified_mcp.sh
```

## 💳 AP2 Protocol - JWT Implementation

### CartMandate con Merchant Signature JWT

Cuando creas un carrito, el merchant firma con JWT RS256:

```json
{
  "contents": {
    "id": "cart_pokemon_abc123",
    "user_cart_confirmation_required": false,
    "payment_request": {
      "method_data": [{
        "supported_methods": "CARD",
        "data": {
          "payment_processor_url": "http://localhost:8003/a2a/processor"
        }
      }],
      "details": {
        "id": "order_pokemon_xyz789",
        "displayItems": [
          {
            "label": "Charizard (x1)",
            "amount": { "currency": "USD", "value": 51 }
          }
        ],
        "total": {
          "label": "Total",
          "amount": { "currency": "USD", "value": 51 }
        }
      }
    }
  },
  "merchant_signature": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "timestamp": "2025-10-20T12:00:00.000Z",
  "merchant_name": "PokeMart - Primera Generación"
}
```

### PaymentMandate con User Authorization JWT

El usuario autoriza el pago con JWT-VC:

```json
{
  "payment_mandate_contents": {
    "payment_mandate_id": "pm_123456",
    "payment_details_id": "order_pokemon_xyz789",
    "payment_details_total": { "currency": "USD", "value": 51 },
    "payment_response": {
      "request_id": "order_pokemon_xyz789",
      "method_name": "CARD",
      "details": { "token": "tok_abc123" }
    }
  },
  "user_authorization": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "timestamp": "2025-10-20T12:00:15.000Z"
}
```

### JWT Token Details

**Merchant Signature JWT:**
- **Algoritmo**: RS256 (RSA + SHA-256)
- **Issuer**: "PokeMart"
- **Claims**: cart_id, merchant, iat, exp
- **Expiración**: 1 hora
- **Clave**: RSA 2048-bit private key

**User Authorization JWT:**
- **Algoritmo**: RS256 (RSA + SHA-256)
- **Issuer**: "user_device"
- **Claims**: cart_hash, payment_hash, verifiable credential
- **Expiración**: 15 minutos (seguridad)
- **Clave**: RSA 2048-bit private key
- **Formato**: JWT-VC (Verifiable Credential)

## 🧪 Testing

Ver documentación completa en [`tests/README.md`](tests/README.md)

```bash
# Test rápido del MCP server
python tests/test_mcp_simple.py

# Test completo con todos los tools
python tests/test_mcp.py

# Test bash del servidor unificado
./tests/test_unified_mcp.sh
```

## 📖 Documentación Detallada

Cada componente tiene su propio README:

- **MCP Server**: [`mcp-server/README.md`](mcp-server/README.md)
- **AP2 Integration**: [`ap2-integration/README.md`](ap2-integration/README.md)
- **Scripts**: [`scripts/README.md`](scripts/README.md)
- **Tests**: [`tests/README.md`](tests/README.md)

## 🌐 URLs de Servicios

Cuando todo está corriendo:

- **Shopping Web UI**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Merchant Agent**: http://localhost:8001
- **Credentials Provider**: http://localhost:8002
- **Payment Processor**: http://localhost:8003

### Agent Cards (A2A Protocol)

```bash
curl http://localhost:8001/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json
curl http://localhost:8003/.well-known/agent-card.json
```

## 🔐 Seguridad

**⚠️ IMPORTANTE**: Este es un proyecto de demostración educativa.

**Implementado (Demo)**:
- ✅ JWT tokens RS256 con claves RSA 2048-bit
- ✅ Estructura completa de CartMandate/PaymentMandate
- ✅ Flujo AP2 completo
- ✅ Verifiable Credentials (JWT-VC)

**Para producción se requiere**:
- ⚠️ Key Management System (KMS) para claves privadas
- ⚠️ Certificados SSL/TLS para comunicaciones
- ⚠️ Validación de firma con claves públicas
- ⚠️ Integración con payment processor real (Stripe, PayPal)
- ⚠️ Cumplimiento PCI DSS
- ⚠️ Auditoría y logging de transacciones
- ⚠️ Rate limiting y protección DDoS
- ⚠️ Manejo seguro de credenciales (no en memoria)

## 📚 Referencias

### Protocolos
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [AP2 Protocol Specification](https://google-agentic-commerce.github.io/AP2/)
- [Google ADK Documentation](https://google.github.io/adk-docs/)

### APIs
- [PokeAPI Documentation](https://pokeapi.co/docs/v2)
- [Google AI Studio](https://aistudio.google.com/)

### Tecnologías
- [JWT.io](https://jwt.io/) - JSON Web Tokens
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [PyJWT](https://pyjwt.readthedocs.io/)

## 🐛 Troubleshooting

### MCP Server no compila

```bash
cd mcp-server
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Error: GOOGLE_API_KEY no configurada

```bash
# Verifica que existe el archivo .env
cat ap2-integration/.env

# Si no existe, créalo
echo "GOOGLE_API_KEY=tu_api_key_aqui" > ap2-integration/.env
```

### Puerto ya en uso (8000, 8001, etc)

```bash
# Encontrar y matar proceso
lsof -ti:8000,8001,8002,8003 | xargs kill -9

# O individualmente
lsof -i :8000  # Ver proceso
kill -9 <PID>  # Matar proceso
```

### Pokemon no encontrado

Solo Pokemon de Gen 1 (números 1-151) están en el catálogo local.

### Tool no disponible en Copilot

```bash
# Reinicia GitHub Copilot
# Ctrl+Shift+P → "GitHub Copilot: Restart Chat"

# Verifica que el MCP server esté compilado
cd mcp-server && npm run build
```

### Errores de importación Python

```bash
# Reinstala dependencias con uv
cd ap2-integration
uv pip install -e .

# O con pip
pip install pyjwt cryptography fastapi uvicorn pydantic
```

## 🚀 Próximos Pasos

Posibles extensiones:

1. **Validación de JWT**: Verificar firmas con claves públicas
2. **Multiple Payment Methods**: Soporte para más formas de pago
3. **Database Integration**: PostgreSQL para persistir transacciones
4. **User Authentication**: Login real con OAuth2
5. **Real Payment Gateway**: Integración con Stripe/PayPal
6. **More Pokemon Generations**: Expandir catálogo
7. **A2A Discovery**: Implementar discovery protocol completo
8. **Agent Reputation**: Sistema de reputación entre agentes

## 👤 Autor

- **CERVIII**
- GitHub: [@CERVIII](https://github.com/CERVIII)
- Repositorio: [mcp-adk-ap2-agent-pokemon](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon)

## 📝 Licencia

Este proyecto es para fines educativos y de demostración del protocolo AP2.

---

**Versión**: 3.0 - JWT RS256 + Web UI  
**Última actualización**: 20 de Octubre de 2025  
**Stack**: TypeScript, Python, MCP, Google ADK, AP2, JWT, FastAPI

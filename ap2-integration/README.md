# Pokemon AP2 Integration

Integración del protocolo **AP2 (Agent Payments Protocol)** para un marketplace de Pokemon. Implementa los roles principales de AP2 para demostrar transacciones seguras entre agentes de IA.

## 🎯 ¿Qué es AP2?

AP2 (Agent Payments Protocol) es un protocolo abierto para la economía de agentes emergente. Diseñado para habilitar comercio seguro, confiable e interoperable entre agentes de IA, desarrolladores, comerciantes y la industria de pagos.

### Conceptos Clave de AP2

1. **CartMandate**: Representa la autorización explícita del usuario para un carrito específico con items y precios exactos
2. **PaymentMandate**: Contiene la autorización final del usuario incluyendo el método de pago
3. **IntentMandate**: Captura las condiciones bajo las cuales un agente puede hacer compras en nombre del usuario
4. **Verifiable Credentials**: Credenciales digitales firmadas criptográficamente que sirven como base de confianza

## 🏗️ Arquitectura

```
┌─────────────────────┐         ┌─────────────────────┐
│  Shopping Agent     │ ◄─────► │  Merchant Agent     │
│  (Puerto 8000)      │   AP2   │  (Puerto 8001)      │
│                     │ Protocol│                     │
│  - Buscar Pokemon   │         │  - Gestión catálogo │
│  - Crear carrito    │         │  - Crear CartMandate│
│  - Procesar pago    │         │  - Procesar pagos   │
└─────────────────────┘         └─────────────────────┘
         │                               │
         │                               │
         ▼                               ▼
     Gemini 2.5                    pokemon-gen1.json
   (Google ADK)                  (Catálogo local)
```

### Flujo de Transacción AP2

1. **Usuario** → Shopping Agent: "Quiero comprar un Pikachu"
2. **Shopping Agent** → Merchant Agent: Buscar Pokemon
3. **Merchant Agent** → Shopping Agent: Resultados del catálogo
4. **Shopping Agent** → Usuario: Mostrar opciones
5. **Usuario** → Shopping Agent: Confirmar selección
6. **Shopping Agent** → Merchant Agent: Crear CartMandate
7. **Merchant Agent** → Shopping Agent: CartMandate firmado
8. **Usuario** → Shopping Agent: Confirmar compra
9. **Shopping Agent**: Crear PaymentMandate
10. **Shopping Agent** → Merchant Agent: Procesar pago
11. **Merchant Agent** → Shopping Agent: Recibo de transacción
12. **Shopping Agent** → Usuario: Confirmación de compra

## 📦 Componentes

### Merchant Agent (`merchant_agent.py`)

- **Puerto**: 8001
- **Responsabilidades**:
  - Gestionar catálogo de Pokemon
  - Crear CartMandates
  - Procesar pagos
  - Generar recibos de transacciones
- **Endpoints**:
  - `GET /catalog` - Obtener catálogo completo
  - `POST /catalog/search` - Buscar Pokemon
  - `POST /cart/create` - Crear carrito
  - `POST /payment/process` - Procesar pago
  - `GET /.well-known/agent-card.json` - A2A Agent Card

### Shopping Agent (`shopping_agent.py`)

- **Puerto**: 8000
- **Responsabilidades**:
  - Asistir al usuario en compras
  - Buscar Pokemon
  - Gestionar carrito de compras
  - Crear PaymentMandates
  - Completar transacciones
- **Herramientas**:
  - `search_pokemon` - Buscar en catálogo
  - `create_shopping_cart` - Crear carrito
  - `list_payment_methods` - Listar métodos de pago
  - `checkout` - Completar compra

### Common Utilities

- `pokemon_utils.py` - Utilidades para gestión de catálogo
- `ap2_types.py` - Tipos de datos del protocolo AP2
- `mcp_client.py` - Cliente para comunicación con MCP Server

## 🚀 Instalación y Configuración

### 1. Instalar dependencias

```bash
cd ap2-integration
uv pip install fastapi uvicorn pydantic python-dotenv google-adk requests
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y añade tu Google API Key:

```env
GOOGLE_API_KEY=tu_api_key_aqui
MERCHANT_AGENT_PORT=8001
SHOPPING_AGENT_PORT=8000
```

## 🎮 Ejecución

### Opción 1: Terminales Separadas

#### Terminal 1: Merchant Agent
```bash
cd ap2-integration
python -m src.roles.merchant_agent
```

#### Terminal 2: Shopping Agent
```bash
cd ap2-integration
python -m src.roles.shopping_agent
```

### Opción 2: Script de inicio
```bash
./start_ap2_demo.sh
```

## 💬 Uso

Una vez ambos agentes estén corriendo, interactúa con el Shopping Agent:

```
You: I want to buy a Pikachu

🤖 Assistant: I found Pikachu in the catalog! It costs $250 USD 
and we have 10 units in stock. Would you like me to add it to 
your cart?

You: Yes, add it to my cart

🤖 Assistant: 🛒 Shopping Cart Created!
Cart ID: cart_a1b2c3d4
Items:
  • Pikachu x1 - $250 each = $250 total

Total: $250 USD
Ready for checkout!

You: Proceed to checkout

🤖 Assistant: ✅ Payment Successful!
Transaction ID: txn_x9y8z7w6
Status: SUCCESS
Message: Successfully purchased 1 Pokemon for $250.00 USD
Total Paid: $250 USD
```

## 🧪 Testing con curl

### Buscar Pokemon
```bash
curl -X POST http://localhost:8001/catalog/search \
  -H "Content-Type: application/json" \
  -d '{"query": "pikachu"}'
```

### Crear Carrito
```bash
curl -X POST http://localhost:8001/cart/create \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"pokemon": "pikachu", "quantity": 1}
    ]
  }'
```

### Ver Agent Card
```bash
curl http://localhost:8001/.well-known/agent-card.json
```

## 📊 Estado del Proyecto

- [x] Tipos AP2 (CartMandate, PaymentMandate, etc.)
- [x] Merchant Agent con API REST
- [x] Shopping Agent con Google ADK
- [x] Integración con catálogo Pokemon
- [x] Flujo de compra básico
- [ ] Credentials Provider Agent
- [ ] Soporte completo A2A protocol
- [ ] Firmas digitales reales
- [ ] Integración con payment processors reales
- [ ] Manejo de desafíos 3DS
- [ ] IntentMandate para compras autónomas

## 🔐 Seguridad

**⚠️ IMPORTANTE**: Esta es una implementación de demostración.

Para producción, se requiere:
- Firmas digitales criptográficas reales
- Validación de PaymentMandates
- Integración con procesadores de pago reales
- Manejo seguro de credenciales
- Auditoría completa de transacciones
- Cumplimiento de PCI DSS

## 📁 Estructura

```
ap2-integration/
├── src/
│   ├── common/
│   │   ├── pokemon_utils.py    # Utilidades de catálogo
│   │   ├── ap2_types.py         # Tipos del protocolo AP2
│   │   └── mcp_client.py        # Cliente MCP
│   └── roles/
│       ├── merchant_agent.py    # Merchant Agent (FastAPI)
│       └── shopping_agent.py    # Shopping Agent (ADK)
├── pyproject.toml
├── .env.example
└── README.md                    # Este archivo
```

## 🐛 Troubleshooting

### "Connection refused" al conectar con Merchant Agent
- Asegúrate de que el Merchant Agent esté corriendo en el puerto 8001
- Verifica con: `curl http://localhost:8001/`

### "GOOGLE_API_KEY not configured"
- Verifica que existe el archivo `.env`
- Asegúrate de que contiene tu API key de Google

### Pokemon no encontrado
- Solo Pokemon de Gen 1 (1-151) están disponibles
- Verifica el nombre en `pokemon-gen1.json`

### Error de importación "No module named 'src'"
```bash
# Usar PYTHONPATH
cd ap2-integration
PYTHONPATH=. python -m src.roles.merchant_agent
```

## 🤝 Relación con otros componentes

Este módulo se integra con:
- **MCP Server** (`../mcp-server/`) - Catálogo unificado con AP2
- **ADK Agent** (`../adk-agent/`) - Agente base con Gemini
- **pokemon-gen1.json** - Catálogo de precios compartido

## 📚 Referencias

- [AP2 Protocol Specification](https://google-agentic-commerce.github.io/AP2/)
- [AP2 GitHub Repository](https://github.com/google-agentic-commerce/AP2)
- [A2A Protocol](https://a2a-protocol.org/)
- [Google ADK Documentation](https://google.github.io/adk-docs/)

---

**AP2 Integration - Pokemon Marketplace**  
**Versión**: 1.0  
**Última actualización**: 20 de Octubre de 2025

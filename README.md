# 🎮 Pokemon MCP + ADK + AP2 Integration

Proyecto completo que integra tres tecnologías clave para agentes de IA:
- **MCP (Model Context Protocol)**: Servidor con herramientas de Pokemon
- **Google ADK (Agent Development Kit)**: Agente con Gemini 2.5
- **AP2 (Agent Payments Protocol)**: Sistema de pagos seguro entre agentes

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                         Usuario                                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Shopping Agent (AP2)                          │
│                  Puerto 8000 - Google ADK                        │
│  - Asistente de compras                                          │
│  - Usa Gemini 2.5 Flash                                          │
│  - Protocolo AP2 para pagos                                      │
└────────────┬──────────────────────────────────┬─────────────────┘
             │                                   │
             │ Tools MCP                         │ AP2 Protocol
             ▼                                   ▼
┌──────────────────────┐           ┌──────────────────────────────┐
│   MCP Pokemon Server │           │     Merchant Agent (AP2)     │
│   Node.js/TypeScript │           │      Puerto 8001             │
│                      │           │   - Gestión de catálogo      │
│  Tools:              │           │   - Procesamiento de pagos   │
│  • get_pokemon_info  │           │   - CartMandates             │
│  • get_pokemon_price │           │   - PaymentMandates          │
│  • search_pokemon    │           └──────────────┬───────────────┘
│  • list_types        │                          │
└──────┬───────────────┘                          │
       │                                          │
       │ APIs                                     │ Data
       ▼                                          ▼
┌────────────────┐                    ┌─────────────────────────┐
│    PokeAPI     │                    │  pokemon-gen1.json      │
│ pokeapi.co/api │                    │  (Catálogo de precios)  │
└────────────────┘                    └─────────────────────────┘
```

## 📦 Componentes del Proyecto

### 1. MCP Server (`mcp-server/`)
Servidor del Model Context Protocol que expone herramientas para trabajar con Pokemon.

**Tecnologías**: TypeScript, Node.js, @modelcontextprotocol/sdk

**Herramientas disponibles**:
- `get_pokemon_info`: Información desde PokeAPI
- `get_pokemon_price`: Precios del catálogo local
- `search_pokemon`: Búsqueda combinada
- `list_pokemon_types`: Lista de tipos disponibles

### 2. ADK Agent (`adk-agent/`)
Agente básico usando Google ADK con integración de herramientas MCP.

**Tecnologías**: Python, Google ADK, Gemini 2.5

**Funcionalidades**:
- Conversación natural sobre Pokemon
- Acceso a información de PokeAPI
- Consulta de precios e inventario

### 3. AP2 Integration (`ap2-integration/`)
Implementación completa del protocolo AP2 para comercio entre agentes.

**Tecnologías**: Python, FastAPI, Google ADK, AP2 Protocol

**Agentes**:
- **Shopping Agent**: Asistente personal de compras
- **Merchant Agent**: Gestión del marketplace

## 🚀 Instalación Rápida

### Requisitos Previos

- **Node.js** 18+ y npm
- **Python** 3.10+
- **uv** package manager
- **Google API Key** de [AI Studio](https://aistudio.google.com/apikey)

### Instalación

```bash
# 1. Clonar/navegar al proyecto
cd prueba-mcp-a2a-ap2

# 2. Instalar MCP Server
cd mcp-server
npm install
npm run build
cd ..

# 3. Instalar ADK Agent
cd adk-agent
uv pip install google-adk python-dotenv
cd ..

# 4. Instalar AP2 Integration
cd ap2-integration
uv pip install fastapi uvicorn pydantic python-dotenv google-adk requests
cd ..

# 5. Configurar API Key
# Crea archivos .env en adk-agent/ y ap2-integration/
# con tu GOOGLE_API_KEY
```

## 🎮 Guías de Uso

### Escenario 1: Agente Simple con MCP

**Objetivo**: Usar el agente ADK básico para consultar información de Pokemon.

```bash
# Terminal 1: Asegúrate de que el MCP server esté compilado
cd mcp-server
npm run build

# Terminal 2: Ejecutar agente ADK
cd adk-agent
# Asegúrate de tener .env con GOOGLE_API_KEY
python pokemon_agent.py
```

**Ejemplo de interacción**:
```
Tú: ¿Qué información tienes sobre Pikachu?
🤖: Pikachu es un Pokemon de tipo eléctrico...

Tú: ¿Cuánto cuesta Charizard?
🤖: Charizard tiene un precio de $180 USD...
```

### Escenario 2: Marketplace con AP2

**Objetivo**: Demostrar el protocolo AP2 con compra completa de Pokemon.

```bash
# Terminal 1: Merchant Agent
cd ap2-integration
python -m src.roles.merchant_agent

# Terminal 2: Shopping Agent
cd ap2-integration
python -m src.roles.shopping_agent
```

**Flujo de compra completo**:
```
You: I want to buy a Pikachu

🤖 Assistant: I found Pikachu! It costs $250 USD...

You: Add it to my cart

🤖 Assistant: 🛒 Cart created with Pikachu...

You: Checkout

🤖 Assistant: ✅ Payment successful! Transaction ID: txn_...
```

## 📖 Documentación Detallada

Cada componente tiene su propio README con documentación completa:

- **MCP Server**: [`mcp-server/README.md`](mcp-server/README.md)
- **ADK Agent**: [`adk-agent/README.md`](adk-agent/README.md)
- **AP2 Integration**: [`ap2-integration/README.md`](ap2-integration/README.md)

## 🔑 Configuración de API Keys

### Google API Key

1. Visita [Google AI Studio](https://aistudio.google.com/apikey)
2. Crea una nueva API Key
3. Copia la clave

### Configurar en el proyecto

**Para adk-agent**:
```bash
cd adk-agent
cp .env.example .env
# Edita .env y pega tu API key
```

**Para ap2-integration**:
```bash
cd ap2-integration
cp .env.example .env
# Edita .env y pega tu API key
```

## 🧪 Testing

### Test MCP Server
```bash
cd mcp-server
npm start
# El servidor debe iniciar en modo stdio
```

### Test Merchant Agent API
```bash
# Con el merchant agent corriendo:
curl http://localhost:8001/catalog
curl http://localhost:8001/.well-known/agent-card.json
```

### Test Shopping Flow
```bash
# Buscar Pokemon
curl -X POST http://localhost:8001/catalog/search \
  -H "Content-Type: application/json" \
  -d '{"query": "pikachu"}'

# Crear carrito
curl -X POST http://localhost:8001/cart/create \
  -H "Content-Type: application/json" \
  -d '{"items": [{"pokemon": "pikachu", "quantity": 1}]}'
```

## 📊 Estructura del Proyecto

```
prueba-mcp-a2a-ap2/
├── mcp-server/              # Servidor MCP con tools de Pokemon
│   ├── src/
│   │   └── index.ts         # Implementación del servidor
│   ├── build/               # Código compilado
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── adk-agent/               # Agente básico con Google ADK
│   ├── pokemon_agent.py     # Agente principal
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md
│
├── ap2-integration/         # Integración completa de AP2
│   ├── src/
│   │   ├── common/          # Utilidades compartidas
│   │   │   ├── pokemon_utils.py
│   │   │   └── ap2_types.py
│   │   └── roles/           # Agentes AP2
│   │       ├── merchant_agent.py
│   │       └── shopping_agent.py
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md
│
├── pokemon-gen1.json        # Catálogo de Pokemon con precios
├── main.ts                  # (archivo original)
├── package.json             # (archivo original)
└── README.md                # Este archivo
```

## 🎯 Casos de Uso

### 1. Información de Pokemon
- Consultar stats, tipos, habilidades desde PokeAPI
- Ver precios e inventario del catálogo local
- Buscar Pokemon por tipo y precio

### 2. Compras Simples
- Buscar Pokemon disponibles
- Crear carrito de compras
- Completar transacción

### 3. Demostración AP2
- CartMandates: Autorización de carrito
- PaymentMandates: Autorización de pago
- Flujo completo con verificación

## 🔐 Seguridad

**⚠️ IMPORTANTE**: Este es un proyecto de demostración educativa.

Para producción se requiere:
- ✅ Firmas digitales reales (no simuladas)
- ✅ Integración con payment processors reales
- ✅ Validación completa de mandates
- ✅ Manejo seguro de credenciales
- ✅ Cumplimiento PCI DSS
- ✅ Auditoría de transacciones

## 📚 Referencias y Recursos

### Protocolos y Frameworks
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [AP2 Protocol Specification](https://ap2-protocol.net/)
- [A2A Protocol](https://a2a-protocol.org/)

### APIs
- [PokeAPI Documentation](https://pokeapi.co/docs/v2)

### Repositorios
- [AP2 GitHub](https://github.com/google-agentic-commerce/AP2)
- [MCP Specification](https://github.com/modelcontextprotocol)

## 🐛 Troubleshooting

### MCP Server no compila
```bash
cd mcp-server
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Error: GOOGLE_API_KEY no configurada
Asegúrate de tener archivos `.env` con la clave en:
- `adk-agent/.env`
- `ap2-integration/.env`

### Puerto 8000/8001 ya en uso
```bash
# Encontrar proceso usando el puerto
lsof -i :8000
lsof -i :8001

# Matar proceso
kill -9 <PID>
```

### Pokemon no encontrado
Solo Pokemon de Gen 1 (números 1-151) están en el catálogo.

## 🚀 Próximos Pasos

Posibles extensiones del proyecto:

1. **Credentials Provider Agent**: Gestión de métodos de pago
2. **IntentMandates**: Compras autónomas del agente
3. **A2A Protocol completo**: Comunicación entre agentes
4. **Web UI**: Interfaz gráfica para shopping
5. **Database**: PostgreSQL para persistencia
6. **Authentication**: OAuth2 para usuarios
7. **Payment Integration**: Stripe/PayPal real
8. **More Pokemon**: Expandir a todas las generaciones

## 📝 Licencia

Este proyecto es para fines educativos y de demostración.

## 🤝 Contribuciones

Este es un proyecto de aprendizaje. Siéntete libre de:
- Experimentar con el código
- Añadir nuevas funcionalidades
- Mejorar la documentación
- Reportar issues

## 📧 Contacto

Para preguntas sobre este proyecto, consulta la documentación de cada componente o las referencias oficiales de los protocolos utilizados.

---

**Fecha de creación**: 17 de octubre de 2025  
**Versión**: 1.0.0  
**Stack**: TypeScript, Python, MCP, Google ADK, AP2

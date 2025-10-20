# 🎮 Pokemon MCP Server

Servidor MCP (Model Context Protocol) para gestión de catálogo de Pokemon. Proporciona herramientas para consultar información, precios e inventario de Pokemon de la primera generación.

## 🎯 Descripción

Este proyecto implementa un servidor MCP que expone herramientas para trabajar con Pokemon:

- **MCP (Model Context Protocol)**: Servidor TypeScript con herramientas de Pokemon
- **PokeAPI Integration**: Consulta de información detallada de Pokemon
- **Catálogo Local**: Gestión de precios e inventario (pokemon-gen1.json)



## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│       Cliente MCP                       │
│  (Claude Desktop, GitHub Copilot, etc)  │
└────────────────┬────────────────────────┘
                 │
                 │ MCP Protocol (stdio)
                 │
                 ▼
┌─────────────────────────────────────────┐
│       MCP Pokemon Server                │
│       Node.js/TypeScript                │
│                                         │
│  Tools:                                 │
│  • get_pokemon_info                     │
│  • get_pokemon_price                    │
│  • search_pokemon                       │
│  • list_pokemon_types                   │
└────────────┬────────────────────────────┘
             │
             │ APIs
             ▼
┌────────────────────┬────────────────────┐
│    PokeAPI         │  pokemon-gen1.json │
│  pokeapi.co/api    │  (Precios locales) │
└────────────────────┴────────────────────┘
```


## ✨ Características Principales

### � Consulta de Pokemon
- Información detallada desde PokeAPI (stats, tipos, habilidades)
- Precios e inventario desde catálogo local
- Búsqueda avanzada con filtros

### �️ Herramientas MCP
- **get_pokemon_info**: Información completa de un Pokemon
- **get_pokemon_price**: Precio e inventario
- **search_pokemon**: Búsqueda con filtros (tipo, precio, disponibilidad)
- **list_pokemon_types**: Lista de todos los tipos disponibles

### 🚀 Integración
- Compatible con Claude Desktop
- Compatible con GitHub Copilot
- Protocolo MCP estándar (stdio)
- Respuestas estructuradas en JSON

## 📦 Componentes

### MCP Server (`mcp-server/`)

Servidor TypeScript que expone herramientas de Pokemon.

**Tecnologías**: TypeScript, Node.js, @modelcontextprotocol/sdk

**Tools disponibles**:
- `get_pokemon_info` - Info detallada desde PokeAPI
- `get_pokemon_price` - Precios del catálogo local
- `search_pokemon` - Búsqueda con filtros avanzados
- `list_pokemon_types` - Tipos disponibles

📖 **[Ver documentación completa →](mcp-server/README.md)**



## 🚀 Instalación Rápida### 💳 Protocolo AP2 Completo│  📚 Gestión de Catálogo  │   │  💳 Transacciones            ││                      │           │   - Gestión de catálogo      │



### Requisitos Previos- **CartMandates**: Autorización explícita de carritos



- **Node.js** 18+ y npm- **PaymentMandates**: Autorización de pagos con método│  • get_pokemon_info      │   │  • POST /cart/create         ││  Tools:              │           │   - Procesamiento de pagos   │

- **Python** 3.10+

- **uv** package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)- **Merchant Signatures**: Firmas digitales automáticas

- **Google API Key** de [AI Studio](https://aistudio.google.com/apikey)

- **Payment Requests**: Estructuras completas de pago│  • get_pokemon_price     │   │    └─► Usa MCP Client        ││  • get_pokemon_info  │           │   - CartMandates             │

### Pasos de Instalación

- Compatible con shopping agents AP2

```bash

# 1. Clonar o navegar al proyecto│  • search_pokemon        │   │  • POST /payment/process     ││  • get_pokemon_price │           │   - PaymentMandates          │

cd prueba-mcp-a2a-ap2

### 🤖 Agentes Inteligentes

# 2. Instalar MCP Server

cd mcp-server- **Shopping Agent**: Asistente conversacional con Gemini│  • list_pokemon_types    │   │  • GET /.well-known/...      ││  • search_pokemon    │           └──────────────┬───────────────┘

npm install

npm run build- **Merchant Agent**: Gestión de catálogo y transacciones

cd ..

- Coordinación automática entre agentes└──────────────────────────┘   └──────────────────────────────┘│  • list_types        │                          │

# 3. Instalar ADK Agent

cd adk-agent- Flujo de compra natural en lenguaje humano

uv pip install google-adk python-dotenv

cd ..           │                              │└──────┬───────────────┘                          │



# 4. Instalar AP2 Integration## 📦 Componentes

cd ap2-integration

uv pip install fastapi uvicorn pydantic python-dotenv google-adk requests           └──────────────┬───────────────┘       │                                          │

cd ..

### 1. MCP Server Unificado (`mcp-server/`)

# 5. Configurar API Keys

echo "GOOGLE_API_KEY=tu_api_key_aqui" > adk-agent/.env                          ▼       │ APIs                                     │ Data

echo "GOOGLE_API_KEY=tu_api_key_aqui" > ap2-integration/.env

```Servidor TypeScript que combina catálogo + merchant AP2.



## 🎮 Uso                  ┌────────────────┐       ▼                                          ▼



### Escenario 1: Agente Simple con MCP**Tecnologías**: TypeScript, Node.js, @modelcontextprotocol/sdk



Usar el agente ADK básico para consultar información de Pokemon.                  │  Pokemon Data  │┌────────────────┐                    ┌─────────────────────────┐



```bash**Tools disponibles**:

# Terminal 1: Asegúrate de que el MCP server esté compilado

cd mcp-server- `get_pokemon_info` - Info detallada desde PokeAPI                  │pokemon-gen1.json││    PokeAPI     │                    │  pokemon-gen1.json      │

npm run build

- `get_pokemon_price` - Precios del catálogo local

# Terminal 2: Ejecutar agente ADK

cd adk-agent- `search_pokemon` - Búsqueda con filtros avanzados                  │  (151 Pokemon) ││ pokeapi.co/api │                    │  (Catálogo de precios)  │

python pokemon_agent.py

```- `list_pokemon_types` - Tipos disponibles



**Ejemplo de interacción**:- `create_pokemon_cart` - ⭐ Crear CartMandates AP2                  └────────────────┘└────────────────┘                    └─────────────────────────┘

```

Tú: ¿Qué información tienes sobre Pikachu?- `get_pokemon_product` - ⭐ Info completa de producto

🤖: Pikachu es un Pokemon de tipo eléctrico...

``````

Tú: ¿Cuánto cuesta Charizard?

🤖: Charizard tiene un precio de $51 USD y hay 5 disponibles...📖 **[Ver documentación completa →](mcp-server/README.md)**

```



### Escenario 2: Marketplace Completo con AP2

### 2. Shopping Agent (`adk-agent/`)

Demostración del protocolo AP2 con compra completa.

## 📦 Componentes## 📦 Componentes del Proyecto

```bash

# Terminal 1: Merchant AgentAgente conversacional básico con Google ADK.

cd ap2-integration

python -m src.roles.merchant_agent



# Terminal 2: Shopping Agent**Tecnologías**: Python, Google ADK, Gemini 2.5 Flash

cd ap2-integration

python -m src.roles.shopping_agent### 1. MCP Server### 1. MCP Server (`mcp-server/`)

```

**Funcionalidades**:

**Flujo de compra**:

```- Conversación natural sobre Pokemon**Ubicación**: `mcp-server/`  Servidor del Model Context Protocol que expone herramientas para trabajar con Pokemon.

You: I want to buy a Pikachu

🤖: I found Pikachu! It costs $250 USD...- Acceso a información de PokeAPI



You: Add it to my cart- Consulta de precios e inventario**Tecnología**: TypeScript + Node.js  

🤖: 🛒 Cart created with Pikachu...



You: Checkout

🤖: ✅ Payment successful! Transaction ID: txn_...📖 **[Ver documentación completa →](adk-agent/README.md)****Puerto**: stdio (proceso subordinado)**Tecnologías**: TypeScript, Node.js, @modelcontextprotocol/sdk

```



### Escenario 3: GitHub Copilot / Claude Desktop

### 3. AP2 Integration (`ap2-integration/`)

Usar el servidor MCP desde tu editor o Claude Desktop.



1. El archivo `.vscode/mcp.json` ya está configurado

2. Reinicia GitHub Copilot: `Ctrl+Shift+P` → "GitHub Copilot: Restart Chat"Implementación completa del protocolo AP2.Servidor MCP que expone herramientas para consultar el catálogo de Pokemon.**Herramientas disponibles**:

3. Pregunta en lenguaje natural:



```

"Busca pokemon de tipo fire por menos de 100 USD"**Tecnologías**: Python, FastAPI, Google ADK, AP2- `get_pokemon_info`: Información desde PokeAPI

"Añade 2 Charizard y 1 Gyarados al carrito"

"Muéstrame el carrito con el CartMandate completo"

```

**Agentes**:🔗 **[Ver documentación completa →](mcp-server/README.md)**- `get_pokemon_price`: Precios del catálogo local

## 🧪 Testing

- **Shopping Agent**: Asistente personal de compras (Puerto 8000)

Ver documentación completa de tests en [`tests/README.md`](tests/README.md)

- **Merchant Agent**: Gestión del marketplace (Puerto 8001)- `search_pokemon`: Búsqueda combinada

### Ejecutar Tests



```bash

# Test completo MCP📖 **[Ver documentación completa →](ap2-integration/README.md)****Herramientas**:- `list_pokemon_types`: Lista de tipos disponibles

python tests/test_mcp.py



# Test simple MCP

python tests/test_mcp_simple.py## 🚀 Instalación Rápida- `get_pokemon_info` - Información detallada de un Pokemon



# Test del servidor unificado

./tests/test_unified_mcp.sh

```### Requisitos Previos- `get_pokemon_price` - Precio e inventario### 2. ADK Agent (`adk-agent/`)



## 💳 Protocolo AP2



### CartMandate- **Node.js** 18+ y npm- `search_pokemon` - Búsqueda con filtrosAgente básico usando Google ADK con integración de herramientas MCP.



El servidor genera automáticamente CartMandates siguiendo la especificación AP2:- **Python** 3.10+



```json- **uv** package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)- `list_pokemon_types` - Lista de tipos disponibles

{

  "contents": {- **Google API Key** de [AI Studio](https://aistudio.google.com/apikey)

    "id": "cart_pokemon_a1b2c3d4",

    "user_signature_required": false,**Tecnologías**: Python, Google ADK, Gemini 2.5

    "payment_request": {

      "method_data": [{### Pasos de Instalación

        "supported_methods": "CARD",

        "data": {### 2. AP2 Merchant Agent

          "payment_processor_url": "http://localhost:8003/a2a/processor"

        }```bash

      }],

      "details": {# 1. Clonar o navegar al proyecto**Ubicación**: `ap2-integration/`  **Funcionalidades**:

        "id": "order_pokemon_x1y2z3w4",

        "displayItems": [cd prueba-mcp-a2a-ap2

          {

            "label": "Charizard (x2)",**Tecnología**: Python + FastAPI  - Conversación natural sobre Pokemon

            "amount": { "currency": "USD", "value": 102 }

          }# 2. Instalar MCP Server

        ],

        "total": {cd mcp-server**Puerto**: 8001- Acceso a información de PokeAPI

          "label": "Total",

          "amount": { "currency": "USD", "value": 102 }npm install

        }

      }npm run build- Consulta de precios e inventario

    }

  },cd ..

  "merchant_signature": "sig_merchant_pokemon_...",

  "timestamp": "2025-10-20T12:00:00.000Z",Agente merchant que implementa el protocolo AP2 para gestión de carritos y pagos.

  "merchantName": "PokeMart - Primera Generación"

}# 3. Instalar ADK Agent

```

cd adk-agent### 3. AP2 Integration (`ap2-integration/`)

## 📖 Documentación Detallada

uv pip install google-adk python-dotenv

Cada componente tiene su propio README con documentación completa:

cd ..🔗 **[Ver documentación completa →](ap2-integration/README.md)**Implementación completa del protocolo AP2 para comercio entre agentes.

- **MCP Server**: [`mcp-server/README.md`](mcp-server/README.md)

- **ADK Agent**: [`adk-agent/README.md`](adk-agent/README.md)

- **AP2 Integration**: [`ap2-integration/README.md`](ap2-integration/README.md)

- **Tests**: [`tests/README.md`](tests/README.md)# 4. Instalar AP2 Integration



## 🗂️ Estructura del Proyectocd ap2-integration



```uv pip install fastapi uvicorn pydantic python-dotenv google-adk requests**Endpoints**:**Tecnologías**: Python, FastAPI, Google ADK, AP2 Protocol

prueba-mcp-a2a-ap2/

├── README.md                          # Este archivocd ..

├── pokemon-gen1.json                  # Catálogo (151 Pokemon)

├── .gitignore                         # Archivos ignorados- `POST /cart/create` - Crear CartMandate

├── .vscode/

│   └── mcp.json                       # Configuración MCP# 5. Configurar API Keys

│

├── tests/                             # Scripts de prueba# Crea archivos .env en adk-agent/ y ap2-integration/- `POST /payment/process` - Procesar PaymentMandate**Agentes**:

│   ├── README.md                      # Documentación de tests

│   ├── test_mcp.py                    # Test completo MCPecho "GOOGLE_API_KEY=tu_api_key_aqui" > adk-agent/.env

│   ├── test_mcp_simple.py             # Test simple MCP

│   └── test_unified_mcp.sh            # Script de test bashecho "GOOGLE_API_KEY=tu_api_key_aqui" > ap2-integration/.env- `GET /.well-known/agent-card.json` - Agent Card (A2A)- **Shopping Agent**: Asistente personal de compras

│

├── mcp-server/                        # Servidor MCP Unificado```

│   ├── README.md

│   ├── src/- **Merchant Agent**: Gestión del marketplace

│   │   └── index.ts                   # Servidor + AP2

│   ├── build/                         # Compilado## 🎮 Uso

│   ├── package.json

│   └── tsconfig.json### 3. Shopping Agent (ADK)

│

├── adk-agent/                         # Agente ADK básico### Escenario 1: Agente Simple con MCP

│   ├── README.md

│   ├── pokemon_agent.py**Ubicación**: `ap2-integration/src/roles/`  ## 🚀 Instalación Rápida

│   ├── pyproject.toml

│   └── .env.exampleUsar el agente ADK básico para consultar información de Pokemon.

│

└── ap2-integration/                   # Integración AP2**Tecnología**: Python + Google Generative AI (Gemini)  

    ├── README.md

    ├── .env.example```bash

    ├── src/

    │   ├── common/                    # Utilidades# Terminal 1: Asegúrate de que el MCP server esté compilado**Puerto**: Terminal interactiva### Requisitos Previos

    │   │   ├── pokemon_utils.py

    │   │   ├── ap2_types.pycd mcp-server

    │   │   └── mcp_client.py

    │   └── roles/                     # Agentesnpm run build

    │       ├── merchant_agent.py

    │       └── shopping_agent.py

    └── pyproject.toml

```# Terminal 2: Ejecutar agente ADKAsistente conversacional que coordina búsquedas y compras.- **Node.js** 18+ y npm



## 🔑 Configuración de API Keyscd adk-agent



### Obtener Google API Keypython pokemon_agent.py- **Python** 3.10+



1. Visita [Google AI Studio](https://aistudio.google.com/apikey)```

2. Crea una nueva API Key

3. Copia la clave🔗 **[Ver documentación completa →](adk-agent/README.md)**- **uv** package manager



### Configurar en el Proyecto**Ejemplo de interacción**:



**Para adk-agent**:```- **Google API Key** de [AI Studio](https://aistudio.google.com/apikey)

```bash

cd adk-agentTú: ¿Qué información tienes sobre Pikachu?

cp .env.example .env

# Edita .env y añade: GOOGLE_API_KEY=tu_key🤖: Pikachu es un Pokemon de tipo eléctrico...**Capacidades**:

```



**Para ap2-integration**:

```bashTú: ¿Cuánto cuesta Charizard?- Búsqueda de Pokemon por nombre/tipo### Instalación

cd ap2-integration

cp .env.example .env🤖: Charizard tiene un precio de $51 USD y hay 5 disponibles...

# Edita .env y añade: GOOGLE_API_KEY=tu_key

``````- Creación de carritos



## 📊 Mejoras vs Arquitectura Anterior



| Métrica | Antes | Ahora | Mejora |### Escenario 2: Marketplace Completo con AP2- Procesamiento de pagos```bash

|---------|-------|-------|--------|

| Servidores MCP | 2 (TS + Python) | 1 (TS) | 50% menos |

| Lenguajes | TypeScript + Python | Solo TypeScript | Unificado |

| Memoria | ~150MB | ~80MB | 47% menos |Demostración del protocolo AP2 con compra completa.- Vista de carrito actual# 1. Clonar/navegar al proyecto

| Velocidad inicio | ~5s | ~2s | 60% más rápido |

| Configuración | Compleja | Simple | 67% menos código |

| Mantenimiento | Difícil | Fácil | Mucho más simple |

```bashcd prueba-mcp-a2a-ap2

## 📚 Referencias

# Terminal 1: Merchant Agent

### Protocolos

- [Model Context Protocol](https://modelcontextprotocol.io/)cd ap2-integration## 🚀 Inicio Rápido

- [AP2 Protocol Specification](https://google-agentic-commerce.github.io/AP2/)

- [Google ADK Documentation](https://google.github.io/adk-docs/)python -m src.roles.merchant_agent



### APIs# 2. Instalar MCP Server

- [PokeAPI Documentation](https://pokeapi.co/docs/v2)

- [Google AI Studio](https://aistudio.google.com/)# Terminal 2: Shopping Agent



## 🐛 Troubleshootingcd ap2-integration### Prerequisitoscd mcp-server



### MCP Server no compilapython -m src.roles.shopping_agent

```bash

cd mcp-server```npm install

rm -rf node_modules package-lock.json

npm install

npm run build

```**Flujo de compra**:```bashnpm run build



### Error: GOOGLE_API_KEY no configurada```

Asegúrate de tener archivos `.env` con la clave en:

- `adk-agent/.env`You: I want to buy a Pikachu# Node.js 20+ para MCP Servercd ..

- `ap2-integration/.env`

🤖: I found Pikachu! It costs $250 USD...

### Puerto 8000/8001 ya en uso

```bashnode --version

# Encontrar proceso

lsof -i :8000You: Add it to my cart

lsof -i :8001

🤖: 🛒 Cart created with Pikachu...# 3. Instalar ADK Agent

# Matar proceso

kill -9 <PID>

```

You: Checkout# Python 3.10+ para AP2 y Shopping Agentcd adk-agent

### Pokemon no encontrado

Solo Pokemon de Gen 1 (números 1-151) están disponibles en el catálogo.🤖: ✅ Payment successful! Transaction ID: txn_...



### Tool create_pokemon_cart no encontrada```python3 --versionuv pip install google-adk python-dotenv

Reinicia GitHub Copilot: `Ctrl+Shift+P` → "GitHub Copilot: Restart Chat"



## 🔐 Seguridad

### Escenario 3: GitHub Copilot / Claude Desktopcd ..

**⚠️ IMPORTANTE**: Este es un proyecto de demostración educativa.



Para producción se requiere:

- ✅ Firmas digitales reales (no simuladas)Usar el servidor MCP desde tu editor o Claude Desktop.# Dependencias de Python

- ✅ Integración con payment processors reales

- ✅ Validación completa de mandates

- ✅ Manejo seguro de credenciales

- ✅ Cumplimiento PCI DSS1. El archivo `.vscode/mcp.json` ya está configuradopip install --user google-generativeai fastapi uvicorn pydantic python-dotenv requests# 4. Instalar AP2 Integration

- ✅ Auditoría de transacciones

2. Reinicia GitHub Copilot: `Ctrl+Shift+P` → "GitHub Copilot: Restart Chat"

## 🚀 Próximos Pasos

3. Pregunta en lenguaje natural:```cd ap2-integration

Posibles extensiones del proyecto:



1. **Credentials Provider Agent**: Gestión de métodos de pago

2. **IntentMandates**: Compras autónomas del agente```uv pip install fastapi uvicorn pydantic python-dotenv google-adk requests

3. **A2A Protocol completo**: Comunicación entre agentes

4. **Web UI**: Interfaz gráfica para shopping"Busca pokemon de tipo fire por menos de 100 USD"

5. **Database**: PostgreSQL para persistencia

6. **Authentication**: OAuth2 para usuarios"Añade 2 Charizard y 1 Gyarados al carrito"### Configuracióncd ..

7. **Payment Integration**: Stripe/PayPal real

8. **More Pokemon**: Expandar a todas las generaciones"Muéstrame el carrito con el CartMandate completo"



## 👤 Autor```



- **CERVIII**

- Repositorio: [mcp-adk-ap2-agent-pokemon](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon)

## 💳 Protocolo AP21. **Configurar API Key de Google**:# 5. Configurar API Key

---



**Versión**: 2.0 - Servidor MCP Unificado con AP2  

**Última actualización**: 20 de Octubre de 2025  ### CartMandate```bash# Crea archivos .env en adk-agent/ y ap2-integration/

**Stack**: TypeScript, Python, MCP, Google ADK, AP2



El servidor genera automáticamente CartMandates siguiendo la especificación AP2:# Crear archivo .env en ap2-integration/# con tu GOOGLE_API_KEY



```jsonecho "GOOGLE_API_KEY=tu_api_key_aqui" > ap2-integration/.env```

{

  "contents": {```

    "id": "cart_pokemon_a1b2c3d4",

    "user_signature_required": false,## 🎮 Guías de Uso

    "payment_request": {

      "method_data": [{2. **Compilar MCP Server**:

        "supported_methods": "CARD",

        "data": {```bash### Escenario 1: Agente Simple con MCP

          "payment_processor_url": "http://localhost:8003/a2a/processor"

        }cd mcp-server

      }],

      "details": {npm install**Objetivo**: Usar el agente ADK básico para consultar información de Pokemon.

        "id": "order_pokemon_x1y2z3w4",

        "displayItems": [npm run build

          {

            "label": "Charizard (x2)",``````bash

            "amount": { "currency": "USD", "value": 102 }

          }# Terminal 1: Asegúrate de que el MCP server esté compilado

        ],

        "total": {### Ejecucióncd mcp-server

          "label": "Total",

          "amount": { "currency": "USD", "value": 102 }npm run build

        }

      }**Terminal 1: Merchant Agent (AP2)**

    }

  },```bash# Terminal 2: Ejecutar agente ADK

  "merchant_signature": "sig_merchant_pokemon_...",

  "timestamp": "2025-10-20T12:00:00.000Z",cd ap2-integrationcd adk-agent

  "merchantName": "PokeMart - Primera Generación"

}PYTHONPATH=. python3 src/roles/merchant_agent.py# Asegúrate de tener .env con GOOGLE_API_KEY

```

```python pokemon_agent.py

## 📖 Documentación Detallada

```

Cada componente tiene su propio README con documentación completa:

**Terminal 2: Shopping Agent**

- **MCP Server**: [`mcp-server/README.md`](mcp-server/README.md)

- **ADK Agent**: [`adk-agent/README.md`](adk-agent/README.md)```bash**Ejemplo de interacción**:

- **AP2 Integration**: [`ap2-integration/README.md`](ap2-integration/README.md)

cd ap2-integration```

## 🗂️ Estructura del Proyecto

PYTHONPATH=. python3 src/roles/shopping_agent.pyTú: ¿Qué información tienes sobre Pikachu?

```

prueba-mcp-a2a-ap2/```🤖: Pikachu es un Pokemon de tipo eléctrico...

├── README.md                          # Este archivo

├── pokemon-gen1.json                  # Catálogo (151 Pokemon)

├── .gitignore                         # Archivos ignorados

├── .vscode/## 💬 Ejemplo de UsoTú: ¿Cuánto cuesta Charizard?

│   └── mcp.json                       # Configuración MCP

│🤖: Charizard tiene un precio de $180 USD...

├── mcp-server/                        # Servidor MCP Unificado

│   ├── README.md``````

│   ├── src/

│   │   └── index.ts                   # Servidor + AP2You: muéstrame pokemon de tipo Fire

│   ├── build/                         # Compilado

│   ├── package.json### Escenario 2: Marketplace con AP2

│   └── tsconfig.json

│🤖 Assistant: Found 10 Pokemon:

├── adk-agent/                         # Agente ADK básico

│   ├── README.md  • Charmander (#4) - $221.00 - Stock: 45 ✅**Objetivo**: Demostrar el protocolo AP2 con compra completa de Pokemon.

│   ├── pokemon_agent.py

│   ├── pyproject.toml  • Charmeleon (#5) - $132.00 - Stock: 38 ✅

│   └── .env.example

│  • Charizard (#6) - $51.00 - Stock: 25 ✅```bash

└── ap2-integration/                   # Integración AP2

    ├── README.md  ...# Terminal 1: Merchant Agent

    ├── .env.example

    ├── src/cd ap2-integration

    │   ├── common/                    # Utilidades

    │   │   ├── pokemon_utils.pyYou: quiero comprar un Charizardpython -m src.roles.merchant_agent

    │   │   ├── ap2_types.py

    │   │   └── mcp_client.py

    │   └── roles/                     # Agentes

    │       ├── merchant_agent.py🤖 Assistant: [Calling create_shopping_cart...]# Terminal 2: Shopping Agent

    │       └── shopping_agent.py

    └── pyproject.toml¡Listo! Charizard ha sido añadido a tu carrito. cd ap2-integration

```

El total es de $51.00.python -m src.roles.shopping_agent

## 🔑 Configuración de API Keys

¿Te gustaría pagar ahora o añadir algo más?```

### Obtener Google API Key



1. Visita [Google AI Studio](https://aistudio.google.com/apikey)

2. Crea una nueva API KeyYou: ver mi carrito**Flujo de compra completo**:

3. Copia la clave

```

### Configurar en el Proyecto

🤖 Assistant: [Calling view_cart...]You: I want to buy a Pikachu

**Para adk-agent**:

```bash🛒 Your Shopping Cart:

cd adk-agent

cp .env.example .envCart ID: cart_abc123🤖 Assistant: I found Pikachu! It costs $250 USD...

# Edita .env y añade: GOOGLE_API_KEY=tu_key

```  • Charizard x1 - $51.00 each = $51.00



**Para ap2-integration**:💰 Total: $51.00 USDYou: Add it to my cart

```bash

cd ap2-integration✅ Ready to checkout?

cp .env.example .env

# Edita .env y añade: GOOGLE_API_KEY=tu_key🤖 Assistant: 🛒 Cart created with Pikachu...

```

You: pagar con tarjeta

## 🧪 Testing

You: Checkout

### Test MCP Server

```bash🤖 Assistant: [Calling checkout...]

cd mcp-server

npm run build✅ Payment Successful!🤖 Assistant: ✅ Payment successful! Transaction ID: txn_...

npm start  # El servidor debe iniciar en modo stdio

```Transaction ID: txn_xyz789```



### Test Merchant Agent APIAmount: $51.00

```bash

# Con el merchant agent corriendo:Method: credit_card## 📖 Documentación Detallada

curl http://localhost:8001/

curl http://localhost:8001/.well-known/agent-card.json```

```

Cada componente tiene su propio README con documentación completa:

### Test Shopping Flow Completo

Ejecuta ambos agentes (merchant + shopping) y sigue el flujo de compra interactivo.## 🗂️ Estructura del Proyecto



## 📊 Mejoras vs Arquitectura Anterior- **MCP Server**: [`mcp-server/README.md`](mcp-server/README.md)



| Métrica | Antes | Ahora | Mejora |```- **ADK Agent**: [`adk-agent/README.md`](adk-agent/README.md)

|---------|-------|-------|--------|

| Servidores MCP | 2 (TS + Python) | 1 (TS) | 50% menos |prueba-mcp-a2a-ap2/- **AP2 Integration**: [`ap2-integration/README.md`](ap2-integration/README.md)

| Lenguajes | TypeScript + Python | Solo TypeScript | Unificado |

| Memoria | ~150MB | ~80MB | 47% menos |├── README.md                          # Este archivo

| Velocidad inicio | ~5s | ~2s | 60% más rápido |

| Configuración | Compleja | Simple | 67% menos código |├── pokemon-gen1.json                  # Catálogo (151 Pokemon)## 🔑 Configuración de API Keys

| Mantenimiento | Difícil | Fácil | Mucho más simple |

│

## 📚 Referencias

├── mcp-server/                        # Servidor MCP### Google API Key

### Protocolos

- [Model Context Protocol](https://modelcontextprotocol.io/)│   ├── README.md                      # Documentación MCP

- [AP2 Protocol Specification](https://google-agentic-commerce.github.io/AP2/)

- [Google ADK Documentation](https://google.github.io/adk-docs/)│   ├── src/index.ts                   # Implementación1. Visita [Google AI Studio](https://aistudio.google.com/apikey)



### APIs│   ├── build/                         # Compilado2. Crea una nueva API Key

- [PokeAPI Documentation](https://pokeapi.co/docs/v2)

- [Google AI Studio](https://aistudio.google.com/)│   └── package.json3. Copia la clave



## 🐛 Troubleshooting│



### MCP Server no compila├── ap2-integration/                   # AP2 + Shopping Agent### Configurar en el proyecto

```bash

cd mcp-server│   ├── README.md                      # Documentación AP2

rm -rf node_modules package-lock.json

npm install│   ├── .env                           # API Keys**Para adk-agent**:

npm run build

```│   ├── src/```bash



### Error: GOOGLE_API_KEY no configurada│   │   ├── roles/cd adk-agent

Asegúrate de tener archivos `.env` con la clave en:

- `adk-agent/.env`│   │   │   ├── merchant_agent.py     # Merchant (AP2)cp .env.example .env

- `ap2-integration/.env`

│   │   │   └── shopping_agent.py     # Shopping (Gemini)# Edita .env y pega tu API key

### Puerto 8000/8001 ya en uso

```bash│   │   └── common/```

# Encontrar proceso

lsof -i :8000│   │       ├── ap2_types.py          # Tipos AP2

lsof -i :8001

│   │       ├── pokemon_utils.py      # Utilidades**Para ap2-integration**:

# Matar proceso

kill -9 <PID>│   │       └── mcp_client.py         # Cliente MCP```bash

```

│   └── requirements.txtcd ap2-integration

### Pokemon no encontrado

Solo Pokemon de Gen 1 (números 1-151) están disponibles en el catálogo.│cp .env.example .env



### Tool create_pokemon_cart no encontrada└── adk-agent/                         # Documentación ADK# Edita .env y pega tu API key

Reinicia GitHub Copilot: `Ctrl+Shift+P` → "GitHub Copilot: Restart Chat"

    └── README.md```

## 🔐 Seguridad

```

**⚠️ IMPORTANTE**: Este es un proyecto de demostración educativa.

## 🧪 Testing

Para producción se requiere:

- ✅ Firmas digitales reales (no simuladas)## 📚 Referencias

- ✅ Integración con payment processors reales

- ✅ Validación completa de mandates### Test MCP Server

- ✅ Manejo seguro de credenciales

- ✅ Cumplimiento PCI DSS- **MCP Protocol**: https://modelcontextprotocol.io/```bash

- ✅ Auditoría de transacciones

- **AP2 Specification**: https://google-agentic-commerce.github.io/AP2/cd mcp-server

## 🚀 Próximos Pasos

- **PokeAPI**: https://pokeapi.co/docs/v2npm start

Posibles extensiones del proyecto:

- **Google Generative AI**: https://ai.google.dev/# El servidor debe iniciar en modo stdio

1. **Credentials Provider Agent**: Gestión de métodos de pago

2. **IntentMandates**: Compras autónomas del agente```

3. **A2A Protocol completo**: Comunicación entre agentes

4. **Web UI**: Interfaz gráfica para shopping## 👤 Autor

5. **Database**: PostgreSQL para persistencia

6. **Authentication**: OAuth2 para usuarios### Test Merchant Agent API

7. **Payment Integration**: Stripe/PayPal real

8. **More Pokemon**: Expandir a todas las generaciones- CERVIII```bash



## 👤 Autor- Repositorio: [mcp-adk-ap2-agent-pokemon](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon)# Con el merchant agent corriendo:



- **CERVIII**curl http://localhost:8001/catalog

- Repositorio: [mcp-adk-ap2-agent-pokemon](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon)

---curl http://localhost:8001/.well-known/agent-card.json

---

```

**Versión**: 2.0 - Servidor MCP Unificado con AP2  

**Última actualización**: 20 de Octubre de 2025  **Versión**: 3.0  

**Stack**: TypeScript, Python, MCP, Google ADK, AP2

**Última actualización**: 17 de Octubre de 2025### Test Shopping Flow

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

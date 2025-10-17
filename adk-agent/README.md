# Pokemon Agent con Google ADK

Agente de IA construido con Google Agent Development Kit (ADK) que usa Gemini 2.5 Flash y se conecta con el MCP Server de Pokemon para acceder a información y precios de Pokemon.

## 🎯 Características

- **Modelo**: Gemini 2.5 Flash (Google)
- **Framework**: Google ADK (Agent Development Kit)
- **Herramientas**: Integración con MCP Server de Pokemon
- **Interacción**: CLI interactiva

### Capacidades del Agente

El agente puede:
- 🔍 Buscar información detallada sobre cualquier Pokemon
- 💰 Consultar precios e inventario de Pokemon Gen 1
- 🎯 Buscar Pokemon por tipo, precio y disponibilidad
- 💡 Recomendar Pokemon según preferencias del usuario

## 📋 Requisitos Previos

1. Python 3.10 o superior
2. `uv` package manager instalado
3. MCP Server compilado y funcionando
4. Google API Key de AI Studio

## 🔧 Configuración

### 1. Instalar dependencias

```bash
cd adk-agent
uv sync
```

### 2. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita el archivo `.env` y añade tu Google API Key:

```env
GOOGLE_API_KEY=tu_api_key_aqui
```

**Obtener API Key:**
- Visita: https://aistudio.google.com/apikey
- Crea una nueva API key
- Cópiala al archivo `.env`

### 3. Verificar MCP Server

Asegúrate de que el MCP Server esté compilado:

```bash
cd ../mcp-server
npm run build
```

## 🚀 Ejecución

```bash
# Desde el directorio adk-agent
uv run python pokemon_agent.py
```

O si prefieres usar el entorno virtual:

```bash
# Activar entorno
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Ejecutar
python pokemon_agent.py
```

## 💬 Ejemplos de Uso

Una vez iniciado el agente, puedes hacer preguntas como:

```
Tú: ¿Qué información tienes sobre Pikachu?
🤖 Pokemon Agent: Pikachu es un Pokemon de tipo eléctrico...

Tú: ¿Cuál es el precio de Charizard?
🤖 Pokemon Agent: Charizard tiene un precio de $180 USD...

Tú: Muéstrame Pokemon de tipo fuego con precio menor a $150
🤖 Pokemon Agent: Aquí están los Pokemon de tipo fuego disponibles...

Tú: ¿Qué Pokemon están en stock ahora?
🤖 Pokemon Agent: Los siguientes Pokemon están disponibles...
```

## 🏗️ Arquitectura

```
Usuario
   ↓
Pokemon Agent (ADK + Gemini 2.5)
   ↓
MCP Tools (4 herramientas)
   ↓
┌─────────────────────┬──────────────────────┐
│   PokeAPI           │  pokemon-gen1.json   │
│   (API externa)     │  (datos locales)     │
└─────────────────────┴──────────────────────┘
```

### Flujo de Datos

1. **Usuario** hace una pregunta al agente
2. **Agente ADK** procesa la pregunta con Gemini 2.5
3. **Gemini** decide qué herramientas MCP usar
4. **MCP Server** ejecuta las herramientas necesarias:
   - Consulta PokeAPI para información del Pokemon
   - Lee pokemon-gen1.json para precios
5. **Agente** recibe los datos y genera respuesta
6. **Usuario** recibe la respuesta formateada

## 🔌 Integración con MCP

El agente se conecta al MCP Server usando `MCPTool.from_server()`:

```python
mcp_tools = MCPTool.from_server(
    command="node",
    args=[mcp_server_path],
    env={}
)
```

Esto le da acceso a las 4 herramientas del MCP Server:
1. `get_pokemon_info` - Información de PokeAPI
2. `get_pokemon_price` - Precios e inventario
3. `search_pokemon` - Búsqueda avanzada
4. `list_pokemon_types` - Lista de tipos

## 📁 Estructura

```
adk-agent/
├── pokemon_agent.py      # Agente principal
├── pyproject.toml        # Dependencias Python
├── .env.example          # Template de variables
├── .env                  # Tu configuración (no en git)
└── README.md            # Esta documentación
```

## 🐛 Troubleshooting

### Error: "GOOGLE_API_KEY no está configurada"
- Verifica que existe el archivo `.env`
- Asegúrate de que contiene `GOOGLE_API_KEY=tu_clave`

### Error: "No se encuentra el MCP Server"
- Compila el MCP Server: `cd ../mcp-server && npm run build`
- Verifica que existe `../mcp-server/build/index.js`

### Error al conectar con PokeAPI
- Verifica tu conexión a internet
- PokeAPI puede estar temporalmente no disponible

## 🔗 Referencias

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [PokeAPI](https://pokeapi.co/)
- [Gemini API](https://ai.google.dev/)

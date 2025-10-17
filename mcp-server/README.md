# MCP Pokemon Server

Servidor MCP (Model Context Protocol) que proporciona herramientas para interactuar con la API de Pokémon y gestionar precios e inventario de Pokémon de la primera generación.

## 🚀 Características

Este servidor MCP expone 4 herramientas (tools):

### 1. `get_pokemon_info`
Obtiene información detallada de un Pokémon desde PokeAPI incluyendo:
- Habilidades
- Tipos
- Estadísticas
- Sprites (imágenes)

**Parámetros:**
- `pokemon` (string): Nombre o número del Pokémon (ej: "pikachu" o "25")

### 2. `get_pokemon_price`
Obtiene información de precio e inventario de un Pokémon desde el catálogo local Gen 1.

**Parámetros:**
- `pokemon` (string): Nombre o número del Pokémon (1-151)

**Retorna:**
- Precio en USD
- Estado de disponibilidad
- Inventario (total, disponibles, vendidos)

### 3. `search_pokemon`
Busca Pokémon combinando datos de PokeAPI y precios locales.

**Parámetros:**
- `type` (string, opcional): Filtrar por tipo (ej: "fire", "water", "grass")
- `maxPrice` (number, opcional): Precio máximo en USD
- `minPrice` (number, opcional): Precio mínimo en USD
- `onlyAvailable` (boolean, opcional): Solo mostrar Pokémon en stock
- `limit` (number, opcional): Número máximo de resultados (default: 10)

### 4. `list_pokemon_types`
Lista todos los tipos de Pokémon disponibles en PokeAPI.

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# Compilar TypeScript
npm run build
```

## 🏃 Ejecución

```bash
# Modo producción
npm start

# Modo desarrollo (con watch)
npm run dev
```

## 🔧 Configuración en Claude Desktop

Para usar este servidor MCP con Claude Desktop, añade la siguiente configuración a tu archivo de configuración de Claude:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pokemon": {
      "command": "node",
      "args": ["/ruta/absoluta/a/mcp-server/build/index.js"]
    }
  }
}
```

## 🧪 Ejemplos de Uso

Una vez configurado en Claude Desktop, puedes hacer preguntas como:

- "¿Cuál es el precio de Pikachu?"
- "Muéstrame todos los Pokémon de tipo fuego con precio menor a $150"
- "¿Qué información tienes sobre Charizard?"
- "¿Qué Pokémon están disponibles y cuestan entre $100 y $200?"

## 📁 Estructura

```
mcp-server/
├── src/
│   └── index.ts          # Servidor MCP principal
├── build/                # Archivos compilados
├── package.json
├── tsconfig.json
└── README.md
```

## 🔗 Dependencias

- `@modelcontextprotocol/sdk`: SDK oficial de MCP
- `zod`: Validación de esquemas
- PokeAPI: https://pokeapi.co/
- `pokemon-gen1.json`: Catálogo local de precios

## 📝 Notas

- Solo soporta Pokémon de la primera generación (números 1-151)
- Los datos de PokeAPI se obtienen en tiempo real
- Los precios e inventario se cargan desde `pokemon-gen1.json` en la raíz del proyecto

# MCP Server - Pokemon Marketplace

Model Context Protocol server para el marketplace de Pokemon.

## Estructura

```
src/mcp/
├── server/
│   ├── index.ts           # Entry point del servidor
│   ├── tools/             # Implementación de herramientas MCP
│   │   ├── pokemon-info.ts
│   │   ├── pokemon-price.ts
│   │   ├── search-pokemon.ts
│   │   ├── list-types.ts
│   │   ├── cart-management.ts
│   │   ├── product-info.ts
│   │   └── index.ts
│   └── types/             # TypeScript types e interfaces
│       ├── pokemon.ts
│       ├── cart.ts
│       └── index.ts
├── client/                # Cliente MCP en Python
│   └── mcp_client.py
├── keys/                  # Claves RSA para JWT
│   ├── merchant_private.pem
│   └── merchant_public.pem
└── build/                 # Salida compilada de TypeScript

```

## Desarrollo

```bash
# Compilar
npm run build

# Modo watch
npm run watch

# Ejecutar
node build/index.js
```

## Tools Expuestas

1. **get_pokemon_info** - Información detallada de PokeAPI
2. **get_pokemon_price** - Precio e inventario local
3. **search_pokemon** - Búsqueda con filtros
4. **list_pokemon_types** - Listado de tipos Pokemon
5. **create_pokemon_cart** - Crear carrito AP2
6. **get_current_cart** - Obtener carrito actual
7. **get_pokemon_product** - Info completa (API + precio)

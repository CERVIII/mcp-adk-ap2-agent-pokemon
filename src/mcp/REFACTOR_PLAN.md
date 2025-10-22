# Plan de Refactorización de MCP Server index.ts

## Análisis del Archivo Actual (892 líneas)

### Estructura Detectada:

1. **Imports** (líneas 1-16)
   - SDK MCP, Zod, fs, path, jwt, crypto

2. **RSA Key Management** (líneas 21-86)
   - `loadOrGenerateRSAKeys()` - Función para cargar/generar claves RSA
   - Carga de claves al inicio
   - MERCHANT_PRIVATE_KEY, MERCHANT_PUBLIC_KEY

3. **TypeScript Types** (líneas 88-167)
   - `PokemonPrice` - Datos locales de Pokemon
   - AP2 Protocol Types (líneas 102-167):
     - `PaymentRequest`
     - `CartItem`
     - `MerchantInfo`
     - `CartMandate`
     - `Cart`

4. **Estado Global** (líneas 169-174)
   - `pricesCache` - Caché de precios
   - `currentCart` - Carrito actual

5. **Helper Functions** (líneas 175-238)
   - `loadPokemonPrices()` - Cargar datos de pokemon-gen1.json
   - `fetchPokeAPI()` - Peticiones a PokeAPI

6. **AP2 Helpers** (líneas 239-419)
   - `createCartMandate()` - Crear CartMandate con firma JWT
   - `formatCartMandateDisplay()` - Formatear output para agentes

7. **Tools Definitions** (líneas 421-549)
   - Array `TOOLS` con metadata de las 7 tools

8. **Server Setup** (líneas 550-881)
   - Crear servidor MCP
   - Handler `ListToolsRequestSchema`
   - Handler `CallToolRequestSchema` con switch-case para cada tool:
     - get_pokemon_info
     - get_pokemon_price
     - search_pokemon
     - list_pokemon_types
     - create_pokemon_cart
     - get_current_cart
     - get_pokemon_product

9. **Server Start** (líneas 882-892)
   - Iniciar transporte y servidor

## Plan de Extracción

### Archivos a Crear:

```
src/mcp/server/
├── types/
│   ├── pokemon.ts          # PokemonPrice
│   ├── cart.ts             # AP2 types: CartMandate, Cart, etc.
│   └── index.ts            # Re-exports
├── utils/
│   ├── rsa-keys.ts         # loadOrGenerateRSAKeys()
│   ├── pokemon-data.ts     # loadPokemonPrices(), state
│   ├── pokeapi.ts          # fetchPokeAPI()
│   └── index.ts            # Re-exports
├── ap2/
│   ├── cart-mandate.ts     # createCartMandate()
│   ├── formatting.ts       # formatCartMandateDisplay()
│   └── index.ts            # Re-exports
├── tools/
│   ├── pokemon-info.ts     # get_pokemon_info
│   ├── pokemon-price.ts    # get_pokemon_price
│   ├── search-pokemon.ts   # search_pokemon
│   ├── list-types.ts       # list_pokemon_types
│   ├── cart-create.ts      # create_pokemon_cart
│   ├── cart-get.ts         # get_current_cart
│   ├── product-info.ts     # get_pokemon_product
│   ├── registry.ts         # TOOLS array
│   └── index.ts            # Re-exports
└── index.ts                # Entry point (~100 líneas)
```

### Orden de Extracción:

1. ✅ **Types primero** (sin dependencias)
   - `types/pokemon.ts`
   - `types/cart.ts`
   - `types/index.ts`

2. ✅ **Utils después** (usan types)
   - `utils/rsa-keys.ts`
   - `utils/pokemon-data.ts`
   - `utils/pokeapi.ts`
   - `utils/index.ts`

3. ✅ **AP2 helpers** (usan types y utils)
   - `ap2/cart-mandate.ts`
   - `ap2/formatting.ts`
   - `ap2/index.ts`

4. ✅ **Tools** (usan todo lo anterior)
   - Cada tool en su archivo
   - `tools/registry.ts`
   - `tools/index.ts`

5. ✅ **Entry point final** (usa tools)
   - `index.ts` simplificado

## Compatibilidad

### Paths que deben mantenerse:
- Claves RSA en `keys/` (relativo a build/)
- `pokemon-gen1.json` en `../../pokemon-gen1.json` (relativo a build/)

### Exports que deben preservarse:
- El servidor debe seguir exportando lo mismo
- Los tools deben tener las mismas firmas

### Build output:
- Todo debe compilarse a `build/index.js`
- `package.json` ya configurado correctamente

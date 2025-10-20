# MCP Pokemon Server - Unified with AP2 Support

Servidor MCP (Model Context Protocol) unificado que combina:
- **Catálogo de Pokémon** (PokeAPI + precios locales)
- **Funcionalidades de Merchant AP2** (CartMandates, Payment Requests)
- **Gestión de Carritos** de compra

Este servidor implementa completamente el protocolo **AP2 (Agent Payments Protocol)** permitiendo la creación de carritos de compra y flujos de pago seguros para agentes de IA.

## 🚀 Características

### Catálogo de Pokémon
- ✅ Información detallada de PokeAPI
- ✅ Precios e inventario local (Gen 1)
- ✅ Búsqueda y filtrado avanzado
- ✅ Listado de tipos disponibles

### AP2 Protocol Support
- ✅ **CartMandate Creation**: Creación de carritos con autorización de compra
- ✅ **Payment Requests**: Estructura completa de solicitudes de pago
- ✅ **Merchant Signatures**: Firmas digitales del comerciante
- ✅ **Display Items**: Desglose detallado de items
- ✅ Compatibilidad con agentes de compra AP2

## 🛠️ Tools Disponibles

### 1. `get_pokemon_info`
Obtiene información detallada de un Pokémon desde PokeAPI.

**Parámetros:**
```json
{
  "pokemon": "charizard"  // Nombre o número (1-151)
}
```

**Respuesta:**
- ID, nombre, altura, peso
- Tipos (fire, water, etc.)
- Habilidades
- Estadísticas base
- Sprites (imágenes)

### 2. `get_pokemon_price`
Obtiene precio e inventario de un Pokémon del catálogo local.

**Parámetros:**
```json
{
  "pokemon": "pikachu"  // Nombre o número (1-151)
}
```

**Respuesta:**
- Precio en USD
- Estado de disponibilidad
- Inventario (total, disponibles, vendidos)

### 3. `search_pokemon`
Busca Pokémon con filtros personalizados.

**Parámetros:**
```json
{
  "type": "fire",         // Tipo de Pokemon (opcional)
  "maxPrice": 100,        // Precio máximo en USD (opcional)
  "minPrice": 50,         // Precio mínimo en USD (opcional)
  "onlyAvailable": true,  // Solo en stock (opcional)
  "limit": 10             // Máximo de resultados (opcional)
}
```

**Respuesta:**
- Lista de Pokemon que cumplen los filtros
- Número total de resultados
- Información completa de cada Pokemon

### 4. `list_pokemon_types`
Lista todos los tipos de Pokémon disponibles.

**Parámetros:**
```json
{}
```

**Respuesta:**
- Lista completa de tipos (fire, water, grass, electric, etc.)

### 5. `create_pokemon_cart` 🆕 (AP2)
Crea un CartMandate siguiendo el protocolo AP2.

**Parámetros:**
```json
{
  "items": [
    {
      "product_id": "6",    // Número de Pokemon (1-151)
      "quantity": 2         // Cantidad a comprar
    },
    {
      "product_id": "130",
      "quantity": 1
    }
  ]
}
```

**Respuesta:**
```
🛒 CARRITO DE COMPRA CREADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Items:
  • Charizard (x2): $102
  • Gyarados (x1): $64

💰 TOTAL: $166.0

🆔 Cart ID: cart_pokemon_a1b2c3d4
📅 Timestamp: 2025-10-20T12:00:00.000Z

✅ CartMandate listo para el proceso de pago AP2

📄 CartMandate completo (JSON): ...
```

### 6. `get_pokemon_product` 🆕
Obtiene información completa de un producto Pokemon (precio + PokeAPI).

**Parámetros:**
```json
{
  "product_id": "25"  // Número de Pokemon (1-151)
}
```

**Respuesta:**
- Toda la información del Pokemon (tipos, stats, habilidades)
- Precio e inventario
- Disponibilidad en stock

## 📦 Estructura del CartMandate (AP2)

El servidor genera CartMandates siguiendo la especificación AP2:

```typescript
interface CartMandate {
  contents: {
    id: string;                        // Identificador único del carrito
    user_signature_required: boolean;   // Si requiere firma del usuario
    payment_request: {
      method_data: [{
        supported_methods: "CARD",
        data: {
          payment_processor_url: string  // URL del procesador de pagos
        }
      }];
      details: {
        id: string;                      // Order ID
        displayItems: Array<{
          label: string;
          amount: {
            currency: "USD";
            value: number;
          }
        }>;
        total: {
          label: "Total";
          amount: {
            currency: "USD";
            value: number;
          }
        }
      };
      options: {
        requestPayerName: boolean;
        requestPayerEmail: boolean;
        requestPayerPhone: boolean;
        requestShipping: boolean;
      }
    }
  };
  merchant_signature: string;  // Firma digital del merchant
  timestamp: string;           // ISO 8601 timestamp
  merchantName: string;        // Nombre del comerciante
}
```

## 🔧 Instalación y Uso

### 1. Instalar dependencias

```bash
cd mcp-server
npm install
```

### 2. Compilar el servidor

```bash
npm run build
```

### 3. Configurar en VS Code / Claude Desktop

El archivo `.vscode/mcp.json` en la raíz del proyecto ya está configurado:

```json
{
  "servers": {
    "mcp-pokemon": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "tsx", "mcp-server/src/index.ts"]
    }
  }
}
```

### 4. Reiniciar GitHub Copilot / Claude

**GitHub Copilot:**
1. Abre la paleta de comandos: `Ctrl+Shift+P`
2. Escribe: `GitHub Copilot: Restart Chat`
3. El servidor estará disponible con todas las funcionalidades

**Claude Desktop:**
Agrega la configuración a `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) o `%APPDATA%\Claude\claude_desktop_config.json` (Windows).

## 🔄 Flujo de Compra AP2

```
┌─────────────────────────────────────────────────────────────────┐
│                    Usuario / Agente de IA                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  1. Buscar Pokémon            │
              │     (search_pokemon)          │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  2. Ver detalles y precio     │
              │     (get_pokemon_info/price)  │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  3. Crear carrito             │
              │     (create_pokemon_cart)     │
              │     → CartMandate generado    │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  4. Procesar pago AP2         │
              │     (Shopping Agent)          │
              │     → PaymentMandate          │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  5. Confirmar transacción     │
              │     → TransactionReceipt      │
              └───────────────────────────────┘
```

## 🧪 Ejemplo de Uso Completo

```typescript
// 1. Buscar Pokémon de tipo fuego baratos
const results = await search_pokemon({
  type: "fire",
  maxPrice: 100
});

// 2. Ver detalles de Charizard
const info = await get_pokemon_info({ pokemon: "charizard" });
const price = await get_pokemon_price({ pokemon: "charizard" });

// 3. Crear carrito con 2 Charizard y 1 Gyarados
const cart = await create_pokemon_cart({
  items: [
    { product_id: "6", quantity: 2 },   // Charizard
    { product_id: "130", quantity: 1 }  // Gyarados
  ]
});

// 4. El CartMandate está listo para ser procesado por un Shopping Agent AP2
```

## 🌟 Ventajas de la Unificación

### Antes (2 servidores):
- ❌ Servidor MCP Python (Merchant)
- ❌ Servidor MCP TypeScript (Catálogo)
- ❌ Comunicación entre servidores
- ❌ Configuración compleja

### Ahora (1 servidor unificado):
- ✅ Todo en TypeScript
- ✅ Un solo proceso
- ✅ Mejor rendimiento
- ✅ Configuración simple
- ✅ Más fácil de mantener
- ✅ Completamente compatible con AP2

## 📁 Estructura

```
mcp-server/
├── src/
│   └── index.ts          # Servidor MCP + AP2
├── build/                # Archivos compilados
├── package.json
├── tsconfig.json
└── README.md             # Este archivo
```

## 🔗 Dependencias

- `@modelcontextprotocol/sdk` - SDK oficial de MCP
- `zod` - Validación de esquemas
- PokeAPI - https://pokeapi.co/
- `pokemon-gen1.json` - Catálogo local de precios (raíz del proyecto)

## 🤝 Integración con Shopping Agents

El CartMandate generado puede ser procesado por:

1. **Shopping Agent Simple**: `ap2-integration/src/roles/shopping_agent_simple.py`
2. **Shopping Agent Completo**: `ap2-integration/src/roles/shopping_agent.py`
3. **Cualquier agente compatible con AP2**

## 📝 Notas

- Todos los precios están en USD
- Solo Pokémon de Generación 1 (1-151) están disponibles
- El inventario se actualiza en tiempo real desde `pokemon-gen1.json`
- Las firmas del merchant son generadas automáticamente
- El payment processor URL apunta a `http://localhost:8003/a2a/processor`

## 🐛 Troubleshooting

### Error: "Pokemon not found"
- Verifica que el número o nombre sea correcto (Gen 1 solamente: 1-151)

### Error: "Not available for sale"
- El Pokémon no está marcado como `enVenta: true` en el catálogo

### Error: "Only X available"
- El inventario disponible es menor que la cantidad solicitada

### El servidor no inicia
```bash
# Verificar dependencias
npm install

# Recompilar
npm run build

# Ver logs de errores
npx tsx src/index.ts
```

### Tool create_pokemon_cart no aparece
Reinicia GitHub Copilot: `Ctrl+Shift+P` → "GitHub Copilot: Restart Chat"

## 📚 Referencias

- [AP2 Protocol Specification](https://google-agentic-commerce.github.io/AP2/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [PokeAPI](https://pokeapi.co/)

---

**Servidor MCP Unificado con AP2 Support**  
**Versión**: 2.0  
**Última actualización**: 20 de Octubre de 2025

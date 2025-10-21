---
title: "[Phase 3.2] Product Categories & Variants"
labels: enhancement, mcp-server, data, phase-3
assignees: CERVIII
---

## 📋 Descripción

Expandir catálogo con categorías de productos: Shiny variants, Items (potions, berries), Mega Evolutions, Regional Forms (Alolan, Galarian).

## 🎯 Tipo de Issue

- [x] ✨ Nueva feature
- [x] 🗄️ Database
- [x] 🤖 MCP Server

## 📦 Fase del Roadmap

**Fase 3.2: Categorías de Productos**

## ✅ Tareas

### Data Model Extensions
```typescript
// pokemon-gen1.json → pokemon-catalog.json
{
  "numero": 25,
  "nombre": "Pikachu",
  "precio": 51,
  "categoria": "pokemon",  // NEW
  "variant": null,         // NEW: 'shiny' | 'alolan' | 'galarian' | 'mega'
  "shiny_available": true, // NEW
  "enVenta": true,
  "inventario": {
    "total": 100,
    "disponibles": 87,
    "vendidos": 13
  }
}

// Nueva estructura para variants
{
  "numero": "25-shiny",
  "nombre": "Pikachu (Shiny)",
  "precio": 150,  // 3x precio base
  "categoria": "pokemon",
  "variant": "shiny",
  "base_numero": 25,
  "enVenta": true,
  "inventario": {...}
}

// Items
{
  "numero": "item-001",
  "nombre": "Potion",
  "precio": 10,
  "categoria": "item",
  "tipo": "healing",
  "enVenta": true,
  "inventario": {...}
}
```

### Database Schema
```sql
CREATE TABLE product_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) UNIQUE,  -- 'pokemon' | 'item' | 'evolution' | 'mega'
    description TEXT,
    display_order INTEGER
);

CREATE TABLE product_variants (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(50),  -- e.g., "25-shiny", "item-001"
    base_product_id INTEGER,  -- e.g., 25 (base Pikachu)
    variant_type VARCHAR(50),  -- 'shiny' | 'alolan' | 'galarian' | 'mega' | null
    name VARCHAR(100),
    price INTEGER,
    price_multiplier DECIMAL(3,2),  -- 3.0 for shiny, 1.5 for regional
    category_id INTEGER REFERENCES product_categories(id),
    metadata JSON,  -- extra data specific to variant
    inventario JSON,
    created_at TIMESTAMP
);
```

### MCP Server Changes

#### New Tool: `list_product_categories`
```typescript
{
  name: "list_product_categories",
  description: "Get all available product categories",
  inputSchema: {
    type: "object",
    properties: {
      include_items: { type: "boolean", default: true }
    }
  }
}
```

#### Update Tool: `search_pokemon`
```typescript
// Add new filters
{
  category?: "pokemon" | "item" | "mega" | "all",
  variant?: "shiny" | "alolan" | "galarian" | "mega",
  include_variants?: boolean  // default false
}
```

#### New Tool: `get_product_variants`
```typescript
{
  name: "get_product_variants",
  description: "Get all variants of a product (shiny, regional forms)",
  inputSchema: {
    type: "object",
    properties: {
      base_product_id: { type: "number" },
      variant_type: { type: "string", enum: ["shiny", "alolan", "galarian", "mega", "all"] }
    },
    required: ["base_product_id"]
  }
}
```

### Product Categories Implementation

#### Pokemon (existing)
- 151-1025 base Pokemon
- Variantes: shiny, regional forms, mega evolutions

#### Items
- [ ] **Healing Items**: Potion ($10), Super Potion ($25), Hyper Potion ($50), Max Potion ($100)
- [ ] **Berries**: Oran Berry ($5), Sitrus Berry ($15), Lum Berry ($20)
- [ ] **Pokéballs**: Poké Ball ($5), Great Ball ($15), Ultra Ball ($30), Master Ball ($500)
- [ ] **Evolution Stones**: Fire Stone ($50), Water Stone ($50), Thunder Stone ($50), Moon Stone ($75)
- [ ] **Held Items**: Leftovers ($100), Choice Band ($150), Life Orb ($200)

#### Mega Evolutions (Gen 6+)
- [ ] Mega Stones: Charizardite X ($300), Mewtwonite Y ($500)
- [ ] Solo para Pokemon con mega evolution

### Pricing Strategy
```typescript
const VARIANT_MULTIPLIERS = {
  shiny: 3.0,      // Shiny Pikachu = $51 × 3 = $153
  alolan: 1.5,     // Alolan Raichu = $60 × 1.5 = $90
  galarian: 1.5,
  mega: 2.5,       // Mega Charizard = $120 × 2.5 = $300
  gmax: 2.0        // Gigantamax forms
};
```

### Frontend UI Changes

#### Category Filters
```html
<div class="category-tabs">
  <button class="active">All</button>
  <button>Pokemon</button>
  <button>Items</button>
  <button>Mega Evolutions</button>
  <button>Shiny ✨</button>
</div>
```

#### Product Card Badge
```html
<div class="product-card">
  <span class="badge badge-shiny">✨ Shiny</span>
  <span class="badge badge-mega">⚡ Mega</span>
  <span class="badge badge-alolan">🌺 Alolan</span>
</div>
```

#### Variant Selector
```html
<!-- On product detail page -->
<div class="variant-selector">
  <button class="variant" data-variant="base">
    Base - $51
  </button>
  <button class="variant" data-variant="shiny">
    ✨ Shiny - $153
  </button>
</div>
```

### Data Generation Script
```python
# scripts/generate_variants.py
def generate_shiny_variants():
    """Create shiny variants for all Pokemon"""
    for pokemon in pokemon_catalog:
        if pokemon["shiny_available"]:
            shiny = {
                "numero": f"{pokemon['numero']}-shiny",
                "nombre": f"{pokemon['nombre']} (Shiny)",
                "precio": pokemon["precio"] * 3,
                "categoria": "pokemon",
                "variant": "shiny",
                "base_numero": pokemon["numero"],
                "inventario": {
                    "total": 10,  # Shiny rarer
                    "disponibles": 10,
                    "vendidos": 0
                }
            }
            catalog.append(shiny)

def generate_items():
    """Create item catalog"""
    items = [
        {"id": "item-001", "name": "Potion", "price": 10, "type": "healing"},
        {"id": "item-002", "name": "Super Potion", "price": 25, "type": "healing"},
        # ... etc
    ]
    return items
```

## 📝 Criterios de Aceptación

- [ ] MCP server expone categorías
- [ ] Shiny variants disponibles para todos Pokemon
- [ ] Items catalog con 20+ items
- [ ] Frontend muestra category tabs
- [ ] Variant selector funciona
- [ ] Cart soporta mixed categories (Pokemon + Items)
- [ ] Search filtra por category

## 🎨 UI/UX

**Shiny Pokemon Visual:**
- Icono ✨ en card
- Efecto sparkle en hover
- Precio en gold color

**Item Cards:**
- Diseño diferente a Pokemon
- Icon de item (sprite de juego)
- Quantity selector (can buy multiple)

## ⏱️ Estimación

**Tiempo:** 1.5-2 semanas
**Prioridad:** Medium
**Complejidad:** Medium (data modeling + UI)

## 🔗 Issues Relacionados

Relacionado con: #phase-3-1-all-generations (expand catalog)
Prerequisito para: #phase-3-3-promotions (bundle discounts)

## 📚 Recursos

- [PokeAPI Varieties](https://pokeapi.co/docs/v2#pokemon-varieties)
- [Shiny Pokemon Data](https://pokemondb.net/shiny)
- [Item List](https://bulbapedia.bulbagarden.net/wiki/List_of_items)
- [Mega Evolution](https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution)

## 🧪 Testing

```python
def test_shiny_variant_pricing():
    pikachu = get_product("25")
    shiny_pikachu = get_product("25-shiny")
    assert shiny_pikachu.price == pikachu.price * 3

def test_category_filter():
    items = search_products(category="item")
    assert all(p.category == "item" for p in items)

def test_variant_inventory():
    # Shiny should have lower inventory
    base = get_product("25")
    shiny = get_product("25-shiny")
    assert shiny.inventario["total"] < base.inventario["total"]
```

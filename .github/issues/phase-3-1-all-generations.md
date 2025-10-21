---
title: "[Phase 3.1] Expand to All Pokemon Generations (Gen 2-9)"
labels: enhancement, data, mcp-server, phase-3
assignees: CERVIII
---

## 📋 Descripción

Expandir el catálogo de 151 Pokemon (Gen 1) a las 1025 especies de todas las generaciones, actualizando el MCP server y la base de datos.

## 🎯 Tipo de Issue

- [x] ✨ Nueva feature
- [x] 🗄️ Database
- [x] 🔧 Backend

## 📦 Fase del Roadmap

**Fase 3.1: Generaciones 2-9**

## ✅ Tareas

### Data Generation
- [ ] Script para generar `pokemon-all-gens.json` (1-1025)
- [ ] Fetch desde PokeAPI para cada Pokemon
- [ ] Generar precios aleatorios por generación:
  - Gen 1: $50-$590 (actual)
  - Gen 2: $40-$500
  - Gen 3-5: $30-$450
  - Gen 6-9: $50-$600 (más recientes)
- [ ] Generar inventario aleatorio (5-15 disponibles)

### MCP Server Updates
- [ ] Actualizar límite en `mcp-server/src/index.ts` (1-1025)
- [ ] Validación de rango en tools
- [ ] Actualizar tests para Gen 2+ Pokemon

### Database Migration
- [ ] Script `migrate_all_generations.py`
- [ ] Batch insert (100 a la vez)
- [ ] Progress bar
- [ ] Rollback en caso de error

### Búsqueda y Filtros
- [ ] Añadir campo `generation` a modelo Pokemon
- [ ] Filtro por generación en frontend
- [ ] Selector de generación (1-9)
- [ ] "Show All Generations" checkbox

### Performance
- [ ] Índice en `pokemon.generation`
- [ ] Lazy loading de imágenes
- [ ] Paginación obligatoria (20 por página)
- [ ] Cache de PokeAPI responses (1 día)

## 🔧 Detalles Técnicos

**Script de Generación:**
```python
# scripts/generate_all_gens.py
import requests
import json
import random

GENERATIONS = {
    1: (1, 151),
    2: (152, 251),
    3: (252, 386),
    # ... hasta gen 9
}

for gen, (start, end) in GENERATIONS.items():
    for numero in range(start, end + 1):
        # Fetch PokeAPI
        # Generate price
        # Generate inventory
```

**Tamaño estimado:**
- JSON: ~15-20 MB
- Database: ~50-60 MB

## 📝 Criterios de Aceptación

- [ ] JSON con 1025 Pokemon generado
- [ ] Database migrada correctamente
- [ ] MCP tools aceptan Pokemon 1-1025
- [ ] Filtro de generación funciona
- [ ] Performance aceptable (búsqueda < 1s)
- [ ] Tests pasan con Pokemon de todas las gens

## 🎨 Frontend Changes

- [ ] Generation filter dropdown
- [ ] Badge mostrando generación en card
- [ ] Colores por generación (opcional)

## ⏱️ Estimación

**Tiempo:** 1 semana
**Prioridad:** Media-Alta

## 🔗 Issues Relacionados

Impacto: #phase-2-3-detail-view (más Pokemon para mostrar)

## 📚 Recursos

- [PokeAPI Pagination](https://pokeapi.co/docs/v2#resource-listspagination-section)
- [Pokemon Generations List](https://bulbapedia.bulbagarden.net/wiki/Generation)
- [National Pokédex](https://www.serebii.net/pokemon/nationalpokedex.shtml)

## 🚨 Consideraciones

**PokeAPI Rate Limits:**
- Máximo ~100 requests/minuto
- Script debe incluir delays: `time.sleep(0.6)`
- Considerar cache local para desarrollo

**Backward Compatibility:**
- Mantener `pokemon-gen1.json` para tests
- Endpoints deben funcionar sin especificar generación

**Storage:**
- Imágenes sprite: ~50KB por Pokemon
- Total sprites: ~50MB
- Considerar CDN para producción

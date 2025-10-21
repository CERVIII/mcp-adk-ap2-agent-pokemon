---
title: "[Phase 2.2] UI/UX Improvements"
labels: enhancement, ui, frontend, phase-2
assignees: CERVIII
---

## 📋 Descripción

Mejorar la experiencia de usuario del Shopping Agent Web UI con estados de carga, paginación, ordenamiento y filtros avanzados.

## 🎯 Tipo de Issue

- [x] ✨ Nueva feature
- [x] 🎨 UI/UX improvement

## 📦 Fase del Roadmap

**Fase 2.2: Mejoras de UI/UX**

## ✅ Tareas

### Loading States
- [ ] Spinners cuando carga Pokemon desde PokeAPI
- [ ] Skeleton screens para lista de productos
- [ ] Loading state en botón "Add to Cart"
- [ ] Progress indicator en checkout

### Paginación
- [ ] Implementar paginación para resultados de búsqueda
- [ ] Mostrar "Página X de Y"
- [ ] Navegación anterior/siguiente
- [ ] Selector de items por página (10, 20, 50)

### Ordenamiento
- [ ] Ordenar por precio (asc/desc)
- [ ] Ordenar por nombre (A-Z, Z-A)
- [ ] Ordenar por número de Pokédex
- [ ] Ordenar por popularidad (más vendidos)
- [ ] Dropdown selector visible

### Filtros Avanzados
- [ ] Combinar múltiples filtros (tipo + precio)
- [ ] Filtro por disponibilidad
- [ ] Clear all filters button
- [ ] Mostrar filtros activos como chips

### Confirmaciones
- [ ] Modal de confirmación antes de checkout
- [ ] Confirmación al limpiar carrito
- [ ] Confirmación al remover items

### Animaciones
- [ ] Transitions CSS suaves en hover
- [ ] Fade in/out para modals
- [ ] Slide animation para carrito
- [ ] Bounce effect en "Add to Cart"

### Theme Switcher
- [ ] Modo oscuro/claro toggle
- [ ] Persistir preferencia en localStorage
- [ ] Transición suave entre temas
- [ ] Iconos moon/sun

## 🔧 Detalles Técnicos

**Stack:**
- FastAPI (backend)
- Vanilla JavaScript (frontend)
- CSS3 animations

**Endpoints a actualizar:**
- `GET /api/search` → Añadir parámetros `page`, `limit`, `sort_by`, `order`
- Mantener compatibilidad con filtros existentes

## 📝 Criterios de Aceptación

- [ ] Loading states visibles en todas las operaciones async
- [ ] Paginación funcional con máximo 20 items por página
- [ ] Al menos 4 opciones de ordenamiento
- [ ] Filtros combinables sin bugs
- [ ] Animaciones smooth (no janky)
- [ ] Theme switcher persistente
- [ ] Mobile responsive

## 🎨 Referencias de Diseño

- Inspiración: Amazon, eBay, Pokémon Center oficial
- Loading: Skeleton screens (como Facebook, LinkedIn)
- Theme: Material Design dark mode guidelines

## ⏱️ Estimación

**Tiempo:** 1 semana
**Prioridad:** Alta

## 🔗 Issues Relacionados

Prerequisito: #PR-cart-persistence (completado)

## 📚 Recursos

- [CSS Loading Spinners](https://loading.io/css/)
- [Material Design Motion](https://material.io/design/motion)
- [Dark Mode Best Practices](https://web.dev/prefers-color-scheme/)

---
title: "[Phase 2.4] Purchase History Page"
labels: enhancement, frontend, database, phase-2
assignees: CERVIII
---

## 📋 Descripción

Crear página de "Mis Compras" donde los usuarios puedan ver su historial de transacciones, descargar recibos en PDF y re-comprar items anteriores.

## 🎯 Tipo de Issue

- [x] ✨ Nueva feature
- [x] 🗄️ Database

## 📦 Fase del Roadmap

**Fase 2.4: Historial de Compras**

## ✅ Tareas

### Página de Historial
- [ ] Nueva ruta `/my-purchases`
- [ ] Lista de transacciones del usuario
- [ ] Filtrar por fecha (última semana, mes, año, todo)
- [ ] Ordenar por fecha (más reciente primero)
- [ ] Paginación (10 por página)

### Vista de Transacción
- [ ] Card por transacción con:
  - Transaction ID
  - Fecha y hora
  - Status (completed, pending, failed)
  - Total pagado
  - Items comprados (nombre + cantidad)
  - Imágenes de Pokemon

### Recibos en PDF
- [ ] Botón "Download Receipt" por transacción
- [ ] Generar PDF con:
  - Logo PokeMart
  - Transaction ID
  - Fecha
  - Lista de items con precios
  - Subtotal + impuestos (mock) + total
  - Payment method
- [ ] Usar librería `reportlab` o `pdfkit`

### Re-comprar
- [ ] Botón "Buy Again" en cada transacción
- [ ] Añade todos los items al carrito actual
- [ ] Confirmación: "X items added to cart"
- [ ] Navega al carrito

### Filtros y Búsqueda
- [ ] Buscar por Pokemon name
- [ ] Filtrar por rango de precio
- [ ] Filtrar por status
- [ ] Clear filters button

## 🔧 Detalles Técnicos

**Nuevos Endpoints:**
```python
GET /api/transactions?user_id={id}&page={n}&limit={m}
GET /api/transactions/{transaction_id}
GET /api/transactions/{transaction_id}/receipt (PDF)
POST /api/cart/reorder  # Body: {transaction_id}
```

**Database:**
- Usar tabla `transactions` existente
- Añadir índice en `user_id` (si no existe)
- Query optimizado con JOIN a `transaction_items`

**PDF Generation:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
```

## 📝 Criterios de Aceptación

- [ ] Lista de transacciones carga < 2 segundos
- [ ] PDF descarga correctamente
- [ ] "Buy Again" añade items al carrito
- [ ] Filtros funcionan correctamente
- [ ] Paginación fluida
- [ ] Mobile responsive
- [ ] Sin transacciones muestra mensaje amigable

## 🎨 Referencias de Diseño

- Amazon Order History
- eBay Purchase History
- Stripe Receipts

## ⏱️ Estimación

**Tiempo:** 3-4 días
**Prioridad:** Media

## 🔗 Issues Relacionados

Prerequisito: Database de transacciones (ya existe desde Fase 1.4)

## 📚 Recursos

- [ReportLab Tutorial](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Python PDF Libraries Comparison](https://realpython.com/creating-modifying-pdf/)
- [Invoice Design Best Practices](https://www.invoice-generator.com/)

## 🚨 Consideraciones

**Privacidad:**
- Solo mostrar transacciones del usuario autenticado
- En Phase 2.4 usar `session_id` temporal
- En Phase 4 migrar a `user_id` real con auth

**Performance:**
- Lazy load imágenes de Pokemon
- Cache de PDF generado (30 días)
- Index en `transactions.created_at`

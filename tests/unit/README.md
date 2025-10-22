# Unit Tests

## Descripción

Tests unitarios para validar la funcionalidad de actualización de inventario en el flujo de compra AP2.

## Estructura

```
UT/
├── __init__.py
├── conftest.py              # Configuración de pytest
├── test_inventory_update.py # Tests de actualización de inventario
└── README.md               # Este archivo
```

## Tests Implementados

### 1. TestInventoryUpdate
Tests de la funcionalidad core de actualización de inventario:

- ✅ `test_pokemon_decrease_stock`: Verifica que `decrease_stock()` reduce disponible y aumenta vendido
- ✅ `test_pokemon_decrease_stock_insufficient`: Verifica que falla cuando no hay stock suficiente
- ✅ `test_repository_decrease_stock`: Verifica el método del repositorio
- ✅ `test_repository_decrease_stock_not_found`: Manejo de Pokemon inexistente
- ✅ `test_cart_item_model`: Validación del modelo `CartItem`
- ✅ `test_cart_item_default_quantity`: Verifica que quantity por defecto es 1
- ✅ `test_cart_contents_with_items`: Verifica que `CartContents` acepta campo `items`
- ✅ `test_multiple_purchases_update_inventory`: Verifica acumulación de múltiples compras

### 2. TestPaymentProcessorIntegration
Tests de integración con el payment processor:

- ✅ `test_cart_mandate_items_extraction`: Extracción de items del CartMandate
- ✅ `test_fallback_to_display_items`: Fallback cuando items no está presente

### 3. TestEdgeCases
Tests de casos límite:

- ✅ `test_purchase_exact_remaining_stock`: Compra del stock restante exacto
- ✅ `test_purchase_zero_quantity`: Manejo de cantidad cero
- ✅ `test_negative_quantity_handled`: Rechazo de cantidades negativas

## Ejecución

### Método Recomendado (usa script)

```bash
cd tests/unit
./run_tests.sh
```

El script `run_tests.sh` configura automáticamente el `PYTHONPATH` y ejecuta los tests.

### Ejecución Manual (si necesitas opciones específicas)

```bash
cd tests/unit
PYTHONPATH=../../ap2-integration:$PYTHONPATH pytest -v
```

### Con Coverage

```bash
cd tests/unit
PYTHONPATH=../../ap2-integration:$PYTHONPATH pytest --cov=../../ap2-integration/src/database/models --cov-report=term-missing
```

### Instalar dependencias de testing

```bash
cd ap2-integration
uv pip install pytest pytest-asyncio pytest-cov
```

### Ejecutar todos los tests

```bash
cd UT
pytest -v
```

### Ejecutar un test específico

```bash
pytest test_inventory_update.py::TestInventoryUpdate::test_pokemon_decrease_stock -v
```

### Ejecutar con coverage

```bash
pytest --cov=src --cov-report=html
```

### Ejecutar tests en modo verbose

```bash
pytest -vv --tb=short
```

## Cobertura

Los tests cubren:

1. **Modelo de datos**: 
   - `Pokemon.decrease_stock()`
   - `Pokemon.increase_stock()`
   
2. **Repositorio**:
   - `PokemonRepository.decrease_stock()`
   - `PokemonRepository.increase_stock()`
   
3. **Modelos Pydantic**:
   - `CartItem`
   - `CartContents` con campo `items`
   
4. **Integración**:
   - Extracción de items del CartMandate
   - Fallback a displayItems
   
5. **Casos límite**:
   - Stock insuficiente
   - Stock exacto
   - Cantidades inválidas
   - Pokemon inexistente

## Fixtures

- `db_session`: Sesión de base de datos SQLite en memoria con datos de prueba
- `pokemon_repo`: Repositorio configurado con la sesión de test

## Notas

- Los tests usan SQLite en memoria (`:memory:`) para aislamiento
- Cada test tiene su propia sesión de DB independiente
- Los datos de prueba incluyen Bulbasaur (#1), Pikachu (#25), y Mewtwo (#150)
- No se requiere base de datos real para ejecutar los tests

## Ejemplo de Salida

```
UT/test_inventory_update.py::TestInventoryUpdate::test_pokemon_decrease_stock PASSED
UT/test_inventory_update.py::TestInventoryUpdate::test_pokemon_decrease_stock_insufficient PASSED
UT/test_inventory_update.py::TestInventoryUpdate::test_repository_decrease_stock PASSED
...

======================== 15 passed in 0.45s ========================
```

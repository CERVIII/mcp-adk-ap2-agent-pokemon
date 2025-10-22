# 🧪 Suite de Tests Unitarios - Pokemon MCP + AP2 Agent

## 📊 Estado Actual

```
✅ 15 tests pasados
❌ 0 tests fallidos
📈 80% cobertura en models.py
📈 35% cobertura total módulo database
```

## 📁 Estructura

```
UT/
├── __init__.py                    # Módulo Python
├── conftest.py                    # Configuración pytest
├── test_inventory_update.py       # Tests principales (13 tests)
├── test_e2e_flow.py              # Tests E2E (2 tests)
├── requirements-test.txt          # Dependencias
├── run_tests.sh                   # Script de ejecución
└── README.md                      # Esta documentación
```

## 🎯 Cobertura de Tests

### Tests de Inventario (13 tests)

#### TestInventoryUpdate
- ✅ Reducción de stock en modelo Pokemon
- ✅ Validación de stock insuficiente
- ✅ Métodos del repositorio
- ✅ Validación de modelos Pydantic (CartItem, CartContents)
- ✅ Múltiples compras acumuladas

#### TestPaymentProcessorIntegration
- ✅ Extracción de items del CartMandate
- ✅ Fallback a displayItems (compatibilidad legacy)

#### TestEdgeCases
- ✅ Compra de stock exacto restante
- ✅ Cantidad cero
- ✅ Cantidades negativas (comportamiento actual)

### Tests End-to-End (2 tests)
- ✅ Flujo completo: MCP → Merchant → Payment Processor
- ✅ Compatibilidad retroactiva sin campo items

## 🚀 Ejecución Rápida

### Instalar dependencias
```bash
cd ap2-integration
source .venv/bin/activate
uv pip install -r ../UT/requirements-test.txt
```

### Ejecutar todos los tests
```bash
cd UT
./run_tests.sh
```

O directamente con pytest:
```bash
cd UT
python -m pytest -v
```

### Modos específicos

**Tests rápidos (para en primer error)**
```bash
./run_tests.sh --quick
```

**Con cobertura**
```bash
./run_tests.sh --coverage
```

**Modo verbose**
```bash
./run_tests.sh --verbose
```

**Test específico**
```bash
python -m pytest test_inventory_update.py::TestInventoryUpdate::test_pokemon_decrease_stock -v
```

## 📈 Cobertura Detallada

| Archivo | Cobertura | Funciones Testeadas |
|---------|-----------|---------------------|
| `models.py` | 80% | `decrease_stock()`, `increase_stock()` |
| `repository.py` | 24% | `decrease_stock()`, `increase_stock()`, `get_by_numero()` |
| `ap2_types.py` | - | `CartItem`, `CartContents` con campo `items` |

## 🧩 Componentes Testeados

### 1. Modelo de Datos
```python
pokemon.decrease_stock(quantity)  # ✅ Testeado
pokemon.increase_stock(quantity)  # ✅ Testeado
```

### 2. Repositorio
```python
repo.decrease_stock(numero, quantity)  # ✅ Testeado
repo.get_by_numero(numero)             # ✅ Testeado
```

### 3. Modelos Pydantic
```python
CartItem(product_id="25", quantity=3)  # ✅ Testeado
CartContents(..., items=[...])         # ✅ Testeado
```

### 4. Flujo E2E
```
MCP Server (items) → Merchant Agent (Pydantic) → Payment Processor (DB update)
✅ Testeado completamente
```

## 🔍 Ejemplo de Salida

```bash
$ ./run_tests.sh

🧪 Unit Tests - Pokemon MCP + AP2 Agent
==========================================

🏃 Ejecutando tests...

test_e2e_flow.py::test_end_to_end_cart_mandate_to_inventory PASSED   [  6%]
test_e2e_flow.py::test_backward_compatibility_without_items PASSED   [ 13%]
test_inventory_update.py::TestInventoryUpdate::test_pokemon_decrease_stock PASSED [ 20%]
...
======================== 15 passed in 0.57s ========================

✅ Tests completados
```

## 📝 Notas Importantes

1. **Base de datos en memoria**: Los tests usan SQLite `:memory:` para aislamiento
2. **No requiere servicios corriendo**: Tests completamente independientes
3. **Fixtures reutilizables**: Sesiones de DB y repositorios pre-configurados
4. **Datos de prueba**: Bulbasaur (#1), Pikachu (#25), Mewtwo (#150)

## 🐛 Issues Detectados

- ⚠️ **Cantidades negativas**: Actualmente aceptadas (debería validarse)
- ℹ️ **Pydantic deprecation warning**: `Config` class debería migrar a `ConfigDict`

## 🔄 Integración Continua

Para agregar a CI/CD:

```yaml
# .github/workflows/tests.yml
- name: Run Unit Tests
  run: |
    cd ap2-integration
    source .venv/bin/activate
    cd ../UT
    pytest -v --cov=../ap2-integration/src --cov-report=xml
```

## 📚 Referencias

- [Pytest Documentation](https://docs.pytest.org/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

---

**Última actualización**: 22 de octubre de 2025
**Tests**: 15 pasados ✅
**Autor**: Sistema de testing automatizado

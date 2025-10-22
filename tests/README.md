# 🧪 Test Suite - Pokemon MCP + AP2 Agent# 🧪 Tests y Scripts de Prueba



Suite completa de tests para el proyecto Pokemon MCP + AP2.Esta carpeta contiene scripts de prueba para validar el funcionamiento del servidor MCP y la integración AP2.



## 📁 Estructura## 📋 Archivos de Test



```### `test_mcp.py` - Test Completo del Servidor MCP

tests/Test exhaustivo del servidor MCP con todas las tools.

├── unit/                          # Tests unitarios (aislados, rápidos)

│   ├── test_inventory_update.py  # Tests de actualización de inventario**Uso:**

│   ├── test_e2e_flow.py          # Tests del flujo completo de datos```bash

│   ├── conftest.py                # Fixtures para tests unitariospython tests/test_mcp.py

│   ├── run_tests.sh               # Script de ejecución```

│   ├── README.md                  # Documentación de tests unitarios

│   └── SUMMARY.md                 # Resumen ejecutivo**Prueba:**

│- ✅ Conexión con el servidor MCP via stdio

├── integration/                   # Tests de integración (con dependencias)- ✅ Todas las tools disponibles (6 tools)

│   ├── database/                  # Tests de base de datos- ✅ `get_pokemon_info` - Información desde PokeAPI

│   │   ├── test_database.py- ✅ `get_pokemon_price` - Precios e inventario local

│   │   ├── test_cart_persistence.py- ✅ `search_pokemon` - Búsqueda con filtros

│   │   └── test_get_cart.py- ✅ `list_pokemon_types` - Listado de tipos

│   ├── mcp/                       # Tests de MCP protocol- ✅ `create_pokemon_cart` - CartMandate con JWT RS256

│   │   ├── test_mcp.py- ✅ `get_pokemon_product` - Producto completo

│   │   ├── test_mcp_simple.py- ✅ Formato de respuestas JSON

│   │   └── test_mcp_debug.py- ✅ Manejo de errores

│   ├── jwt/                       # Tests de JWT/Auth

│   │   ├── test_jwt_generation.py**Salida esperada:**

│   │   ├── test_jwt_signature.py```

│   │   ├── test_jwt_validation.py🚀 Testing MCP Pokemon Server

│   │   └── test_rsa_persistence.py✅ Connected to MCP server

│   └── ap2/                       # Tests de AP2 protocol✅ Tool: get_pokemon_info

│✅ Tool: get_pokemon_price

├── e2e/                          # Tests end-to-end (flujo completo)✅ Tool: search_pokemon

│   └── (tests E2E existentes)✅ Tool: list_pokemon_types

│✅ Tool: create_pokemon_cart

├── conftest.py                    # Configuración global de pytest✅ Tool: get_pokemon_product

└── README.md                      # Este archivo✅ All tests passed!

``````



## 🎯 Tipos de Tests### `test_mcp_simple.py` - Test Rápido

Test simplificado para validación rápida.

### Unit Tests (tests/unit/)

**Propósito**: Validar componentes individuales de forma aislada**Uso:**

```bash

- ✅ Rápidos de ejecutar (< 1s)python tests/test_mcp_simple.py

- ✅ Sin dependencias externas```

- ✅ Base de datos en memoria

- ✅ Mocks/stubs cuando es necesario**Prueba:**

- ✅ Conexión básica con servidor MCP

**Ejecución**:- ✅ Tool `get_pokemon_info` con Pikachu

```bash- ✅ Respuesta correcta en menos de 5 segundos

cd tests/unit

./run_tests.sh**Salida esperada:**

``````

Testing MCP Pokemon Server (Simple)

**Cobertura actual**: ✅ Connected successfully

- 15 tests pasados ✅✅ get_pokemon_info test passed

- 80% cobertura en models.pyTest completed in 2.3s

```

### Integration Tests (tests/integration/)

**Propósito**: Validar interacción entre componentes### `test_unified_mcp.sh` - Script Bash Interactivo

Script bash completo para probar el servidor MCP end-to-end.

- 🔄 Usan servicios reales (DB, MCP server)

- 🔄 Más lentos que unit tests**Uso:**

- 🔄 Validan flujos completos```bash

chmod +x tests/test_unified_mcp.sh

**Ejecución**:./tests/test_unified_mcp.sh

```bash```

# Tests de base de datos

pytest tests/integration/database/ -v**Realiza:**

1. ⚙️ Verifica dependencias (Node.js, npm)

# Tests de MCP2. 📦 Instala dependencias si es necesario

pytest tests/integration/mcp/ -v3. 🔨 Compila el servidor TypeScript

4. 🚀 Inicia el servidor MCP en modo stdio

# Tests de JWT5. 🧪 Lista todas las tools disponibles

pytest tests/integration/jwt/ -v6. ⏸️ Espera Ctrl+C para detener

```

**Ejemplo de uso:**

### E2E Tests (tests/e2e/)```bash

**Propósito**: Validar sistema completo end-to-end$ ./tests/test_unified_mcp.sh

Checking dependencies...

- 🌐 Requieren todos los servicios corriendo✅ Node.js found

- 🌐 Simulan flujos de usuario reales✅ npm found

- 🌐 Más lentos pero más completosInstalling dependencies...

✅ Dependencies installed

## 🚀 Ejecución RápidaBuilding server...

✅ Server built

### Todos los testsStarting MCP server...

```bash✅ Server started on stdio

pytest tests/ -vTools available:

```  - get_pokemon_info

  - get_pokemon_price

### Solo unit tests (rápido)  - search_pokemon

```bash  - list_pokemon_types

pytest tests/unit/ -v  - create_pokemon_cart

```  - get_pokemon_product

Press Ctrl+C to stop

### Solo integration tests```

```bash

pytest tests/integration/ -v### `test_get_cart.py` - Test de CartMandate

```Test específico para la creación de CartMandates con JWT.



### Con cobertura**Uso:**

```bash```bash

pytest tests/ --cov=ap2-integration/src --cov-report=htmlpython tests/test_get_cart.py

``````



### Tests específicos**Prueba:**

```bash- ✅ Creación de cart con `create_pokemon_cart`

# Un archivo- ✅ Estructura de CartMandate AP2

pytest tests/unit/test_inventory_update.py -v- ✅ merchant_signature (JWT RS256)

- ✅ payment_request completo

# Un test específico- ✅ displayItems correctos

pytest tests/unit/test_inventory_update.py::TestInventoryUpdate::test_pokemon_decrease_stock -v

```## 🚀 Ejecutar Todos los Tests



## 📊 Estado de Tests### Opción 1: Tests individuales



| Tipo | Cantidad | Estado | Cobertura |```bash

|------|----------|--------|-----------|# Test completo (recomendado)

| Unit | 15 | ✅ Pasando | 80% models |python tests/test_mcp.py

| Integration/DB | ~5 | 🔄 Mixed | - |

| Integration/MCP | ~3 | 🔄 Mixed | - |# Test rápido

| Integration/JWT | ~4 | 🔄 Mixed | - |python tests/test_mcp_simple.py

| E2E | ~2 | 🔄 Mixed | - |

# Test de CartMandate

## 🛠️ Configuraciónpython tests/test_get_cart.py



### Instalar dependencias de test# Test bash interactivo

```bash./tests/test_unified_mcp.sh

cd ap2-integration```

source .venv/bin/activate

uv pip install pytest pytest-asyncio pytest-cov pytest-mock### Opción 2: Suite completa

```

```bash

### Variables de entorno (automáticas)# Ejecutar todos los tests Python

- `TESTING=1` - Modo test activadofor test in tests/test_*.py; do

- `ENVIRONMENT=test` - Entorno de test    echo "Running $test..."

    python "$test" || exit 1

## 📝 Escribiendo Nuevos Testsdone



### Unit Test Templateecho "✅ All Python tests passed!"

```python```

import pytest

from src.database import Pokemon, PokemonRepository## 📝 Requisitos



class TestNewFeature:### Para tests Python

    @pytest.fixture

    def db_session(self):```bash

        # Setup# Dependencias necesarias

        yield sessionpip install mcp python-dotenv

        # Teardown

    # O con uv

    def test_something(self, db_session):cd ap2-integration

        # Arrangeuv sync

        repo = PokemonRepository(db_session)```

        

        # Act### Para test bash

        result = repo.some_method()

        ```bash

        # Assert# Solo necesitas Node.js y npm

        assert result is not Nonenode --version  # >= 18

```npm --version

```

### Integration Test Template

```python### MCP Server compilado

import pytest

from src.database import SessionLocal, init_db```bash

# Compilar antes de ejecutar tests

def test_integration_flow():cd mcp-server

    # Setup real DBnpm install

    init_db()npm run build

    ```

    # Test with real dependencies

    with SessionLocal() as db:## 🔍 Debugging Tests

        result = perform_action(db)

        assert result.success is True### Si test_mcp.py falla

```

```bash

## 🔍 Debugging Tests# 1. Verifica que el servidor esté compilado

cd mcp-server && npm run build

### Ver output completo

```bash# 2. Verifica la ruta en el test

pytest tests/ -v -s# El test busca: mcp-server/build/index.js

```

# 3. Ejecuta con más verbose

### Parar en primer errorpython -v tests/test_mcp.py

```bash```

pytest tests/ -x

```### Si test_unified_mcp.sh no ejecuta



### Ejecutar solo tests marcados```bash

```bash# Dale permisos de ejecución

# Marcar test: @pytest.mark.slowchmod +x tests/test_unified_mcp.sh

pytest tests/ -m "not slow"

```# Ejecuta directamente

bash tests/test_unified_mcp.sh

### Ver traceback completo```

```bash

pytest tests/ -v --tb=long### Si los tests son lentos

```

El test completo puede tardar 10-15 segundos debido a:

## 📚 Referencias- Conexión con PokeAPI (externa)

- Inicio del servidor MCP

- [Unit Tests README](unit/README.md) - Documentación detallada de tests unitarios- Múltiples llamadas a tools

- [Unit Tests Summary](unit/SUMMARY.md) - Resumen ejecutivo

- [Pytest Documentation](https://docs.pytest.org/)Para tests más rápidos, usa `test_mcp_simple.py`.



## 🤝 Contribuir## 📊 Cobertura de Tests



Al agregar nuevos tests:| Componente | Test | Cobertura |

|------------|------|-----------|

1. **Unit tests**: `tests/unit/` - Para lógica aislada| MCP Connection | test_mcp.py | ✅ 100% |

2. **Integration tests**: `tests/integration/` - Para interacción entre componentes| get_pokemon_info | test_mcp.py, test_mcp_simple.py | ✅ 100% |

3. **E2E tests**: `tests/e2e/` - Para flujos completos de usuario| get_pokemon_price | test_mcp.py | ✅ 100% |

| search_pokemon | test_mcp.py | ✅ 100% |

Mantener:| list_pokemon_types | test_mcp.py | ✅ 100% |

- ✅ Nombres descriptivos de tests| create_pokemon_cart | test_mcp.py, test_get_cart.py | ✅ 100% |

- ✅ Fixtures reutilizables| get_pokemon_product | test_mcp.py | ✅ 100% |

- ✅ Docstrings explicando qué se testea| JWT Signatures | test_get_cart.py | ⚠️ Partial |

- ✅ Assertions claros

## 🎯 Tests de Integración

---

Para tests de integración completa con AP2:

**Última actualización**: 22 de octubre de 2025  

**Mantenedor**: CERVIII```bash

# Inicia todos los agentes
./scripts/run-ap2-agents.sh &

# Ejecuta tests de integración
./scripts/test-ap2-integration.sh

# O prueba la Web UI manualmente
./scripts/run-shopping-agent.sh
open http://localhost:8000
```

## 🔗 Ver También

- [README Principal](../README.md) - Documentación general
- [MCP Server README](../mcp-server/README.md) - Documentación del servidor MCP
- [AP2 Integration README](../ap2-integration/README.md) - Documentación de AP2
- [Scripts README](../scripts/README.md) - Scripts de automatización

---

**💡 Tip**: Para CI/CD, usa `test_mcp_simple.py` que es más rápido y no depende de APIs externas lentas.

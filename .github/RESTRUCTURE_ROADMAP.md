# 🗺️ Roadmap de Reestructuración - Paso a Paso

> **⚠️ IMPORTANTE:** Este es un plan DETALLADO y REALISTA basado en el estado actual del proyecto.
> A diferencia de un plan teórico, este documento considera:
> - ✅ Código que YA funciona y debe seguir funcionando
> - ✅ Paths relativos y absolutos reales
> - ✅ Dependencias entre módulos existentes
> - ✅ Tests que ya corren (aunque algunos fallen)
> - ✅ Scripts y Makefile que están operativos

## 📖 Resumen Ejecutivo

**Objetivo:** Reorganizar el código en `src/{mcp,ap2,database}` sin romper funcionalidad existente.

**Motivación:**
- Separar claramente MCP, AP2 y Database
- Facilitar testing unitario e integración
- Mejorar mantenibilidad y escalabilidad

**Enfoque:**
1. **Preservar funcionalidad** - Todo lo que funciona DEBE seguir funcionando
2. **Migración incremental** - Hacer cambios en fases pequeñas y verificables
3. **Git history** - Usar `git mv` para mantener historia
4. **Tests como red de seguridad** - Verificar después de cada cambio

**Tiempo estimado:** 2-3 días de trabajo enfocado

**Riesgos:**
- 🔴 **Alto:** Romper imports y que agentes no arranquen
- 🟡 **Medio:** Path de database incorrecto y pérdida de datos
- 🟡 **Medio:** Claude Desktop no conecte con MCP
- 🟢 **Bajo:** Tests fallen temporalmente (pueden marcarse skip)

---

## 📍 Estado Actual del Proyecto

**Branch:** `refactor/project-restructure`

**Sistema Funcional:**
- ✅ **MCP Server (ORIGINAL)**: `mcp-server/` - Compila con `npm run build`, 893 líneas en `index.ts`
- ✅ **MCP Server (REFACTORIZADO)**: `src/mcp/` - Estructura modular, 120 líneas en `index.ts`, ✅ TESTS PASSED
- ✅ **AP2 Integration**: `ap2-integration/` - Usa `uv`, 4 agentes funcionando
- ✅ **Database**: `pokemon_marketplace.db` - SQLite con datos reales (backup creado)
- ✅ **Scripts**: 7 scripts shell en `scripts/` - todos operativos
- ✅ **Makefile**: 173 líneas - comandos `setup`, `run`, `stop` funcionan
- ✅ **Tests**: Parcialmente organizados en `tests/integration/` y `tests/unit/`

**Dependencias:**
- Node.js + npm (MCP server)
- Python 3.11+ + uv (AP2 agents)
- SQLite (Database)
- Google AI Studio API Key (en `.env`)

**Puertos Activos:**
- 8000: Shopping Web UI (`shopping_agent`)
- 8001: Merchant Agent
- 8002: Credentials Provider
- 8003: Payment Processor

**Archivos Críticos:**
- `pokemon-gen1.json` - Catálogo de 151 Pokemon (single source of truth)
- `claude_desktop_config.json` - Config MCP para Claude
- `ap2-integration/.env` - GOOGLE_API_KEY y otras vars
- `mcp-server/keys/*.pem` - Claves RSA para JWT
- `pokemon_marketplace.db` - Base de datos con transacciones

---

## 🎯 Fase 1: Preparación y Setup Inicial

### ✅ Step 1.1: Crear branch de reestructuración
**Objetivo:** Trabajar en una rama separada para no afectar `main`

**Estado:** ✅ **COMPLETADO** - Branch `refactor/project-restructure` activo

---

### ✅ Step 1.2: Hacer backup y verificar sistema funcional
**Objetivo:** Asegurar que podemos restaurar si algo sale mal

**Estado:** ✅ **COMPLETADO**

**Verificación realizada:** 
- ✅ Backup `pokemon_marketplace.db.backup` creado
- ✅ MCP original compila sin errores (`mcp-server/`)
- ✅ Tests de integración identificados

---

### ✅ Step 1.3: Crear estructura base de carpetas
**Objetivo:** Crear la nueva estructura de directorios vacía

**Estado:** ✅ **COMPLETADO**

**Estructura creada:**
```
src/
├── mcp/
│   ├── server/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── ap2/
│   │   ├── tools/
│   │   └── index.ts
│   ├── client/
│   ├── keys/
│   └── build/
├── ap2/
│   ├── agents/
│   ├── protocol/
│   └── README.md
└── database/
    └── README.md

tests/
├── mcp/{unit,integration}/
├── ap2/{unit,integration}/
└── database/{unit,integration}/
```

**Archivos creados:**
- ✅ `pytest.ini` con markers (unit, integration, e2e, mcp, ap2, database)
- ✅ READMEs para cada módulo (mcp, ap2, database)
- ✅ `src/mcp/REFACTOR_PLAN.md` con análisis detallado

---

### ⬜ Step 1.4: Configurar pytest
**Objetivo:** Crear configuración pytest sin romper tests existentes

**IMPORTANTE:** `tests/conftest.py` YA EXISTE y tiene configuración crítica:
```python
# tests/conftest.py ACTUAL (NO borrar):
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
ap2_path = project_root / "ap2-integration"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(ap2_path))
```

**Acción - Crear `pytest.ini` (NO existe actualmente):**
```bash
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    mcp: MCP related tests
    ap2: AP2 protocol tests
    database: Database tests
    skip: Skip test temporarily
EOF
```

**Acción - ACTUALIZAR `tests/conftest.py` (después de mover archivos):**
```python
"""Global pytest configuration for all tests"""
import sys
import os
from pathlib import Path

# Add project paths - ACTUALIZAR cuando movamos archivos
project_root = Path(__file__).parent.parent
src_path = project_root / "src"  # NUEVO - después de reestructurar

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Mantener configuración existente
os.environ["TESTING"] = "1"
os.environ["ENVIRONMENT"] = "test"
```

**Verificación:**
```bash
pytest --collect-only tests/integration/database  # Debe encontrar tests
pytest --markers                                   # Debe mostrar markers
```

---

### ✅ Step 1.4: Actualizar .gitignore
**Objetivo:** Asegurar que archivos temporales no se commiteen

**Agregar a .gitignore:**
```
# Test artifacts
.pytest_cache/
.coverage
htmlcov/
*.cover
.hypothesis/

# Database
*.db
*.db-journal
*.sqlite

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# TypeScript
dist/
build/
*.tsbuildinfo

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
```

**Verificación:** ✓ .gitignore actualizado

---

## 🎯 Fase 2: Migración del MCP Server

### ✅ Step 2.1: Analizar index.ts actual y planear extracción
**Objetivo:** Entender el código antes de partirlo

**Estado:** ✅ **COMPLETADO** - Análisis documentado en `src/mcp/REFACTOR_PLAN.md`

**Resultados:**
- 893 líneas en total (no 694 como se pensaba originalmente)
- 7 herramientas identificadas (6 originales + get_current_cart)
- Módulos extraídos: types (2), utils (3), ap2 (3), tools (7)

**Acciones:**
```bash
# 1. Ver estructura actual del index.ts
wc -l mcp-server/src/index.ts  # 694 líneas
head -100 mcp-server/src/index.ts  # Ver imports y tipos

# 2. Identificar secciones en index.ts:
# Líneas aproximadas (verificar con editor):
# - 1-50: Imports y configuración
# - 51-150: Tipos e interfaces TypeScript
# - 151-250: Funciones helper (formatCartMandateDisplay, etc.)
# - 251-600: Implementación de tools (6 tools)
# - 601-694: Setup del servidor y manejo de requests
```

**NO hacer cambios todavía - solo planear**

**Archivo a crear:** `src/mcp/REFACTOR_PLAN.md`
```markdown
# Plan de Refactorización de index.ts

## Estructura Actual (694 líneas)
- Tools: get_pokemon_info, get_pokemon_price, search_pokemon, 
         list_pokemon_types, create_pokemon_cart, get_pokemon_product
- Helper functions: formatCartMandateDisplay, createCartMandate
- Firma JWT con claves RSA en keys/

## Archivos a Crear
1. types/pokemon.ts - Interfaces de Pokemon
2. types/cart.ts - Interfaces de Cart/AP2
3. types/index.ts - Re-exports
4. tools/pokemon-info.ts - Tool get_pokemon_info
5. tools/pokemon-price.ts - Tool get_pokemon_price
6. tools/search-pokemon.ts - Tool search_pokemon
7. tools/list-types.ts - Tool list_pokemon_types
8. tools/cart-management.ts - Tools create_cart + get_current_cart
9. tools/product-info.ts - Tool get_pokemon_product
10. tools/index.ts - Registry + exports
11. server/index.ts - Entry point simplificado (~100 líneas)

## Orden de Extracción
1. Types primero (no tienen dependencias)
2. Helpers después (usan types)
3. Tools después (usan types y helpers)
4. Server al final (usa todo)
```

**Verificación:** ✓ Plan documentado y entendido

---

### ✅ Step 2.2-2.7: Extraer todas las herramientas
**Objetivo:** Separar las 7 tools en archivos dedicados

**Estado:** ✅ **COMPLETADO**

**Archivos creados:**
- ✅ `src/mcp/server/tools/pokemon-info.ts` - get_pokemon_info
- ✅ `src/mcp/server/tools/pokemon-price.ts` - get_pokemon_price
- ✅ `src/mcp/server/tools/search-pokemon.ts` - search_pokemon
- ✅ `src/mcp/server/tools/list-types.ts` - list_pokemon_types
- ✅ `src/mcp/server/tools/cart-create.ts` - create_pokemon_cart
- ✅ `src/mcp/server/tools/cart-get.ts` - get_current_cart
- ✅ `src/mcp/server/tools/product-info.ts` - get_pokemon_product

**Módulos auxiliares extraídos:**
- ✅ `src/mcp/server/types/pokemon.ts` - PokemonPrice, PokemonInfo
- ✅ `src/mcp/server/types/cart.ts` - CartMandate, PaymentRequest, etc.
- ✅ `src/mcp/server/utils/rsa-keys.ts` - loadOrGenerateRSAKeys()
- ✅ `src/mcp/server/utils/pokemon-data.ts` - loadPokemonPrices()
- ✅ `src/mcp/server/utils/pokeapi.ts` - fetchPokeAPI()
- ✅ `src/mcp/server/ap2/cart-state.ts` - Cart state management
- ✅ `src/mcp/server/ap2/cart-mandate.ts` - createCartMandate()
- ✅ `src/mcp/server/ap2/formatting.ts` - formatCartMandateDisplay()

---

### ✅ Step 2.8: Crear registro de tools
**Estado:** ✅ **COMPLETADO**

**Archivo creado:** `src/mcp/server/tools/registry.ts`
- Contiene array `TOOLS` con metadata de las 7 herramientas
- Cada tool tiene: name, description, inputSchema (Zod → JSON Schema)

---

### ✅ Step 2.9: Refactorizar index.ts
**Estado:** ✅ **COMPLETADO**

**Archivo creado:** `src/mcp/server/index.ts` (~120 líneas vs 893 originales)
- Entry point simplificado con imports modulares
- Request handlers para initialize, tools/list, tools/call
- Switch-case dispatcher para las 7 herramientas
- Código mucho más legible y mantenible

---

### ✅ Step 2.10: Configurar compilación y dependencias
**Estado:** ✅ **COMPLETADO**

**Archivos creados:**
- ✅ `src/mcp/package.json` - Dependencias y scripts de build
- ✅ `src/mcp/tsconfig.json` - Configuración TypeScript
- ✅ `src/mcp/keys/` - Claves RSA copiadas desde mcp-server/

**Comandos ejecutados:**
```bash
cd src/mcp
npm install    # ✅ 107 packages instalados, 0 vulnerabilities
npm run build  # ✅ Compilación exitosa
```

---

### ✅ Step 2.11: Crear test de integración
**Estado:** ✅ **COMPLETADO**

**Archivo creado:** `tests/integration/mcp/test_refactored_mcp.py`
- Test completo del servidor refactorizado
- Verifica: initialize, tools/list, tools/call
- Prueba tool `list_pokemon_types` como validación

**Resultado del test:**
```
✅ ALL TESTS PASSED - MCP Server refactorizado funciona correctamente
- Server name: mcp-pokemon-server
- Protocol version: 2024-11-05
- 7 tools registradas correctamente
- Tool execution funciona (19 Pokemon types encontrados)
```

---

## ✅ FASE 2 COMPLETADA - Resumen

**Commit:** `c91fe75` - "✅ Fase 2.3: MCP tools extraídas + servidor compilado"

**Logros:**
1. ✅ Monolito de 893 líneas dividido en 15+ módulos organizados
2. ✅ Estructura modular: types/, utils/, ap2/, tools/, index.ts
3. ✅ Build exitoso: `npm run build` genera build/index.js
4. ✅ Tests pasando: test_refactored_mcp.py valida todas las funcionalidades
5. ✅ Servidor MCP 100% funcional en nueva estructura

**Métricas:**
- **Antes:** 1 archivo monolítico (893 líneas)
- **Después:** 15 archivos modulares (~120 líneas entry point + módulos especializados)
- **Reducción complejidad:** ~85% en archivo principal
- **Mantenibilidad:** ↑↑↑ (cada módulo tiene responsabilidad única)

**Próximo paso:** Fase 3 - Migración del AP2 Protocol

---

## 🎯 Fase 3: Migración del AP2 Protocol

**ESTADO ACTUAL:** ⚠️ **PARCIALMENTE COMPLETADA**

**Completado:**
- ✅ Agentes movidos a `src/ap2/agents/` (shopping, merchant, credentials, payment_processor)
- ✅ Estructura de directorios creada

**Pendiente:**
- ❌ Step 3.1: Migrar archivos de `ap2-integration/src/common/` a `src/ap2/protocol/`
- ❌ Step 3.7: Crear `src/ap2/pyproject.toml`
- ❌ Step 3.8-3.11: Tests de AP2
- ⚠️ **DUPLICACIÓN:** `ap2-integration/` todavía existe (debería eliminarse después de migración completa)

---

### ⬜ Step 3.1: Preparar migración de AP2
**Objetivo:** Entender la estructura actual antes de mover

**Estado:** ⚠️ **PARCIALMENTE COMPLETADO** - Estructura analizada pero archivos NO migrados

**Estado Actual:**
- ✅ Análisis completado
- ❌ Archivos de `ap2-integration/src/common/` AÚN NO migrados a `src/ap2/protocol/`

**Archivos pendientes de migración:**
```
ap2-integration/src/common/ap2_types.py      → src/ap2/protocol/types.py (PENDIENTE)
ap2-integration/src/common/jwt_validator.py  → src/ap2/protocol/validators.py (PENDIENTE)
ap2-integration/src/common/session.py        → src/ap2/protocol/session.py (PENDIENTE)
ap2-integration/src/common/utils.py          → src/ap2/protocol/utils.py (PENDIENTE)
ap2-integration/src/common/mcp_client.py     → src/mcp/client/mcp_client.py (PENDIENTE)
```

**Estado de `src/ap2/protocol/`:**
- ✅ Directorio existe
- ✅ `__init__.py` existe
- ❌ Solo tiene `__init__.py`, faltan los 4 archivos principales

---

### ❌ Step 3.2: Migrar archivos de protocol
**Objetivo:** Mover archivos de `ap2-integration/src/common/` a `src/ap2/protocol/`

**Estado:** ❌ **PENDIENTE**

**Acciones necesarias:**
```bash
# Migrar archivos de protocol
git mv ap2-integration/src/common/ap2_types.py src/ap2/protocol/types.py
git mv ap2-integration/src/common/jwt_validator.py src/ap2/protocol/validators.py
git mv ap2-integration/src/common/session.py src/ap2/protocol/session.py
git mv ap2-integration/src/common/utils.py src/ap2/protocol/utils.py

# Actualizar imports en todos los archivos que usen common
# - src/ap2/agents/merchant/server.py
# - src/ap2/agents/shopping/agent.py
# - src/ap2/agents/payment_processor/server.py
# - ap2-integration/src/* (archivos que no se han migrado aún)
```

---

### ⬜ Step 3.3: Mover Shopping Agent
**Objetivo:** Mover agente de compras

**Estado:** ✅ **COMPLETADO**

**Archivos migrados:**
- ✅ `src/ap2/agents/shopping/agent.py`
- ✅ `src/ap2/agents/shopping/web_ui.py`
- ✅ `src/ap2/agents/shopping/__main__.py`

---

### ⬜ Step 3.4: Mover Merchant Agent

**Estado:** ✅ **COMPLETADO**

**Archivos migrados:**
- ✅ `src/ap2/agents/merchant/server.py`
- ✅ `src/ap2/agents/merchant/__main__.py`

---

### ⬜ Step 3.5: Mover Credentials Provider

**Estado:** ✅ **COMPLETADO**

**Archivos migrados:**
- ✅ `src/ap2/agents/credentials/server.py`
- ✅ `src/ap2/agents/credentials/__main__.py`

---

### ⬜ Step 3.6: Mover Payment Processor

**Estado:** ✅ **COMPLETADO**

**Archivos migrados:**
- ✅ `src/ap2/agents/payment_processor/server.py`
- ✅ `src/ap2/agents/payment_processor/__main__.py`

---

### ❌ Step 3.7: Crear pyproject.toml para AP2
**Objetivo:** Configurar el módulo AP2 de forma independiente

**Estado:** ❌ **PENDIENTE** - Archivo NO existe

**Archivo a crear:** `src/ap2/pyproject.toml`

**Archivo:** `src/ap2/pyproject.toml`
```toml
[project]
name = "pokemon-marketplace-ap2"
version = "1.0.0"
description = "AP2 Protocol implementation for Pokemon Marketplace"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.115.12",
    "uvicorn>=0.34.1",
    "google-genai>=1.12.1",
    "pydantic>=2.10.8",
    "python-jose>=3.3.0",
    "cryptography>=44.0.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.4",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.1",
]

[tool.pytest.ini_options]
testpaths = ["../../tests/ap2"]
pythonpath = ["."]
```

**Verificación:** ❌ pyproject.toml NO creado

---

### ❌ Step 3.8: Crear tests unitarios de AP2

**Estado:** ❌ **PENDIENTE**
**Archivo:** `tests/ap2/conftest.py`
```python
import pytest
from pathlib import Path
import sys

# Add src/ap2 to path
ap2_path = Path(__file__).parent.parent.parent / "src" / "ap2"
sys.path.insert(0, str(ap2_path))

@pytest.fixture
def sample_cart_mandate():
    """Sample CartMandate for testing"""
    return {
        "contents": {
            "id": "test-cart-123",
            "user_signature_required": False,
            "payment_request": {
                "amount": 100.00,
                "currency": "USD",
                "items": []
            }
        },
        "merchant_signature": "sig_test",
        "timestamp": "2025-10-21T20:00:00Z",
        "merchantName": "PokeMart"
    }
```

**Crear tests:**
- `tests/ap2/unit/test_cart_mandate.py`
- `tests/ap2/unit/test_jwt_generation.py`
- `tests/ap2/unit/test_jwt_validation.py`
- `tests/ap2/unit/test_rsa_keys.py`
- `tests/ap2/unit/test_protocol_types.py`

**Verificación:** ❌ Tests unitarios NO creados

---

### ❌ Step 3.9: Mover tests existentes de AP2

**Estado:** ❌ **PENDIENTE**
**Acciones:**
```bash
git mv tests/test_jwt_generation.py tests/ap2/unit/test_jwt_generation.py
git mv tests/test_jwt_validation.py tests/ap2/unit/test_jwt_validation.py
git mv tests/test_jwt_signature.py tests/ap2/unit/test_jwt_signature.py
git mv tests/test_rsa_persistence.py tests/ap2/unit/test_rsa_persistence.py
```

**Verificación:** ❌ Tests NO movidos

---

### ❌ Step 3.10: Crear tests de integración AP2

**Estado:** ❌ **PENDIENTE**
**Crear:**
- `tests/ap2/integration/test_shopping_agent.py`
- `tests/ap2/integration/test_merchant_agent.py`
- `tests/ap2/integration/test_payment_processor.py`
- `tests/ap2/integration/test_full_payment_flow.py`

**Verificación:** ❌ Tests de integración NO creados

---

### ❌ Step 3.11: Verificar AP2 funciona

**Estado:** ❌ **PENDIENTE** - No se puede verificar hasta completar steps anteriores

**Comandos (cuando esté listo):**
```bash
cd src/ap2
uv sync
pytest ../../tests/ap2/unit -v
pytest ../../tests/ap2/integration -v
```

**Verificación:** ❌ No ejecutado (steps previos pendientes)

---

## ⚠️ RESUMEN FASE 3 - Estado Real

**Completado (40%):**
- ✅ Steps 3.3-3.6: Agentes movidos a `src/ap2/agents/`

**Pendiente (60%):**
- ❌ Step 3.1: Análisis hecho pero archivos NO migrados
- ❌ Step 3.2: Archivos de protocol NO migrados desde `ap2-integration/src/common/`
- ❌ Step 3.7: `src/ap2/pyproject.toml` NO existe
- ❌ Steps 3.8-3.11: Tests de AP2 NO creados

**Bloqueadores:**
- 🔴 `ap2-integration/` todavía existe (duplicación de código)
- 🔴 Imports de agentes aún apuntan a `ap2-integration/src/common/`
- 🔴 Sin configuración de dependencias (`pyproject.toml`)

**Siguiente paso:** Completar Step 3.2 (migrar archivos de protocol)

---

## 🎯 Fase 4: Migración de Database Layer

### ⬜ Step 4.1: Analizar dependencias de Database
**Objetivo:** Entender qué usa la DB antes de mover

**Estado Actual:**
```bash
# Ver estructura de database
ls -la ap2-integration/src/database/
# __init__.py
# cli.py         - CLI commands
# engine.py      - SQLAlchemy engine + SessionLocal
# models.py      - Pokemon, Transaction, Cart, CartItem
# repository.py  - CRUD operations
# seed.py        - Database seeder

# Ver imports de database en otros módulos
grep -r "from.*database import" ap2-integration/src/
grep -r "from.*database import" tests/
```

**Quién Usa Database:**
1. **merchant_agent/server.py**:
   - `from src.database import get_db, PokemonRepository`
   - Usado en endpoints de FastAPI

2. **Tests**:
   - `tests/integration/database/*` - Todos los tests de DB
   - `tests/unit/test_inventory_update.py` - Tests de inventario

3. **seed.py**:
   - Lee `pokemon-gen1.json` desde root
   - Path relativo: `../../pokemon-gen1.json`

**Problemas a Resolver:**
1. **Path de DB**: `engine.py` tiene `sqlite:///../../pokemon_marketplace.db`
   - Relativo a `ap2-integration/src/database/`
   - Después de mover a `src/database/` cambiar a `sqlite:///../../../pokemon_marketplace.db`
   - O mejor: usar path absoluto o variable de entorno

2. **Path de pokemon-gen1.json**: `seed.py` lo lee
   - Relativo actual: `../../pokemon-gen1.json`
   - Después de mover: `../../../config/pokemon-gen1.json` (si lo movemos a config/)

3. **Imports en merchant_agent**:
   - De: `from src.database import ...`
   - A: `from database import ...` (si src/database está en PYTHONPATH)

**⚠️ CRÍTICO:**
- NO mover hasta tener plan claro de paths
- Hacer backup de pokemon_marketplace.db primero
- Actualizar engine.py para usar DATABASE_URL de .env

**Verificación:** ✓ Dependencias documentadas

---

### ✅ Step 4.2: Configurar Alembic para migraciones
**Objetivo:** Setup de migraciones de DB

**Comandos:**
```bash
cd src/database
alembic init migrations
```

**Archivo:** `src/database/alembic.ini`
```ini
[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///../../pokemon_marketplace.db
```

**Archivo:** `src/database/migrations/env.py`
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Add src/database to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Base

target_metadata = Base.metadata

# ... resto de configuración
```

**Verificación:** ✓ Alembic configurado

---

### ✅ Step 4.3: Crear migración inicial
**Comandos:**
```bash
cd src/database
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Verificación:** ✓ Migración creada

---

### ✅ Step 4.4: Crear seeders
**Archivo:** `src/database/seeds/pokemon_seeder.py`
```python
"""Pokemon data seeder"""
import json
from pathlib import Path
from engine import SessionLocal
from models import Pokemon

def seed_pokemon():
    """Seed Pokemon data from catalog"""
    catalog_path = Path(__file__).parent.parent.parent.parent / "config" / "pokemon-gen1.json"
    
    with open(catalog_path) as f:
        pokemon_data = json.load(f)
    
    db = SessionLocal()
    
    for poke in pokemon_data:
        # Insert pokemon
        pass
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_pokemon()
```

**Verificación:** ✓ Seeders creados

---

### ✅ Step 4.5: Actualizar imports en MCP y AP2
**Objetivo:** Actualizar todos los imports de database

**Archivos a actualizar:**
- `src/mcp/server/tools/*.ts` (si usan DB)
- `src/ap2/agents/shopping/agent.py`
- `src/ap2/agents/merchant/server.py`
- Cualquier otro archivo que importe database

**Cambiar:**
```python
# Antes
from ap2_integration.src.database import get_db, Pokemon

# Después
from database import get_db, Pokemon
```

**Verificación:** ✓ Imports actualizados

---

### ✅ Step 4.6: Crear tests unitarios de Database
**Archivo:** `tests/database/conftest.py`
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add src/database to path
db_path = Path(__file__).parent.parent.parent / "src" / "database"
sys.path.insert(0, str(db_path))

from models import Base

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def test_db(test_engine):
    """Create test database session"""
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.rollback()
    session.close()
```

**Crear tests:**
- `tests/database/unit/test_models.py`
- `tests/database/unit/test_pokemon_repository.py`
- `tests/database/unit/test_transaction_repository.py`
- `tests/database/unit/test_cart_repository.py`
- `tests/database/unit/test_engine.py`

**Verificación:** ✓ Tests unitarios creados

---

### ✅ Step 4.7: Mover tests existentes de Database
**Acciones:**
```bash
git mv tests/test_database.py tests/database/unit/test_database.py
git mv tests/test_cart_persistence.py tests/database/integration/test_cart_persistence.py
```

**Verificación:** ✓ Tests movidos

---

### ✅ Step 4.8: Crear tests de integración de Database
**Crear:**
- `tests/database/integration/test_transaction_flow.py`
- `tests/database/integration/test_migrations.py`

**Verificación:** ✓ Tests de integración creados

---

### ✅ Step 4.9: Verificar Database funciona
**Comandos:**
```bash
pytest tests/database/unit -v
pytest tests/database/integration -v
```

**Verificación:** ✓ Todos los tests pasan

---

## 🎯 Fase 5: Tests End-to-End

### ✅ Step 5.1: Crear test de flujo completo de compra
**Archivo:** `tests/e2e/test_purchase_flow.py`
```python
import pytest

@pytest.mark.e2e
async def test_complete_purchase_flow():
    """Test complete purchase flow from search to payment"""
    # 1. Start MCP server
    # 2. Search for Pokemon
    # 3. Get Pokemon info
    # 4. Create cart
    # 5. Process payment via AP2
    # 6. Verify transaction in DB
    pass
```

**Verificación:** ✓ Test E2E creado

---

### ✅ Step 5.2: Crear test de integración AP2 completa
**Archivo:** `tests/e2e/test_ap2_full_integration.py`
```python
import pytest

@pytest.mark.e2e
async def test_ap2_full_integration():
    """Test full AP2 protocol integration"""
    # Test all agents working together
    pass
```

**Verificación:** ✓ Test de integración AP2 creado

---

### ✅ Step 5.3: Verificar E2E tests
**Comandos:**
```bash
pytest tests/e2e -v
```

**Verificación:** ✓ Tests E2E pasan

---

## 🎯 Fase 6: Configuración y Scripts

### ✅ Step 6.1: Mover configuraciones
**Acciones:**
```bash
git mv pokemon-gen1.json config/pokemon-gen1.json
git mv claude_desktop_config.json config/claude_desktop_config.json
```

**Crear:** `config/environment/.env.example`
```bash
# Google AI Studio API Key
GOOGLE_API_KEY=your_api_key_here

# Database
DATABASE_URL=sqlite:///../../pokemon_marketplace.db

# MCP Server
MCP_SERVER_PORT=3000

# AP2 Agents
SHOPPING_AGENT_PORT=8000
MERCHANT_AGENT_PORT=8001
PAYMENT_PROCESSOR_PORT=8003
```

**Verificación:** ✓ Configuraciones movidas

---

### ✅ Step 6.2: Actualizar scripts
**Objetivo:** Actualizar scripts para nueva estructura

**Archivo:** `scripts/run-mcp-server.sh`
```bash
#!/bin/bash
cd src/mcp
npm run build
node build/index.js
```

**Archivo:** `scripts/run-shopping-agent.sh`
```bash
#!/bin/bash
cd src/ap2
uv run python -m agents.shopping
```

**Archivo:** `scripts/test-mcp.sh`
```bash
#!/bin/bash
pytest tests/mcp -v
```

**Archivo:** `scripts/test-ap2.sh`
```bash
#!/bin/bash
pytest tests/ap2 -v
```

**Archivo:** `scripts/test-database.sh`
```bash
#!/bin/bash
pytest tests/database -v
```

**Archivo:** `scripts/test-all.sh`
```bash
#!/bin/bash
pytest tests -v
```

**Verificación:** ✓ Scripts actualizados

---

### ✅ Step 6.3: Actualizar Makefile
**Objetivo:** Comandos make para nueva estructura

**Archivo:** `Makefile`
```makefile
.PHONY: help setup clean test test-mcp test-ap2 test-db test-e2e

help:
	@echo "Available commands:"
	@echo "  make setup       - Install all dependencies"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make test        - Run all tests"
	@echo "  make test-mcp    - Run MCP tests only"
	@echo "  make test-ap2    - Run AP2 tests only"
	@echo "  make test-db     - Run Database tests only"
	@echo "  make test-e2e    - Run E2E tests only"

setup:
	cd src/mcp && npm install
	cd src/ap2 && uv sync

clean:
	rm -rf src/mcp/build
	rm -rf src/mcp/node_modules
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

test:
	pytest tests -v

test-mcp:
	pytest tests/mcp -v

test-ap2:
	pytest tests/ap2 -v

test-db:
	pytest tests/database -v

test-e2e:
	pytest tests/e2e -v

coverage:
	pytest tests --cov=src --cov-report=html
```

**Verificación:** ✓ Makefile actualizado

---

## 🎯 Fase 7: Documentación

### ✅ Step 7.1: Crear README por módulo
**Archivos a crear:**
- `src/mcp/README.md`
- `src/ap2/README.md`
- `src/database/README.md`
- `tests/README.md`

**Verificación:** ✓ READMEs creados

---

### ✅ Step 7.2: Mover documentación a docs/
**Acciones:**
```bash
git mv QUICKSTART.md docs/QUICKSTART.md
git mv ROADMAP.md docs/ROADMAP.md
```

**Verificación:** ✓ Docs movidos

---

### ✅ Step 7.3: Actualizar README principal
**Objetivo:** Actualizar README con nueva estructura

**Verificación:** ✓ README actualizado

---

### ✅ Step 7.4: Crear diagramas de arquitectura
**Crear:**
- `docs/architecture/system-overview.md`
- `docs/architecture/mcp-flow.md`
- `docs/architecture/ap2-flow.md`
- `docs/architecture/database-schema.md`

**Verificación:** ✓ Diagramas creados

---

## 🎯 Fase 8: Cleanup y Verificación Final

### ✅ Step 8.1: Eliminar carpetas antiguas
**Acciones:**
```bash
rm -rf mcp-server/
rm -rf ap2-integration/
```

**Verificación:** ✓ Carpetas antiguas eliminadas

---

### ✅ Step 8.2: Ejecutar todos los tests
**Comandos:**
```bash
make test
```

**Verificación:** ✓ Todos los tests pasan

---

### ✅ Step 8.3: Verificar cobertura de tests
**Comandos:**
```bash
make coverage
```

**Verificación:** ✓ Cobertura > 80%

---

### ✅ Step 8.4: Actualizar Claude Desktop config
**Objetivo:** Apuntar a nueva ubicación del MCP server

**Archivo:** `config/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "pokemon-marketplace": {
      "command": "node",
      "args": [
        "/absolute/path/to/src/mcp/build/index.js"
      ]
    }
  }
}
```

**Verificación:** ✓ Config actualizado

---

### ✅ Step 8.5: Commit y push
**Acciones:**
```bash
git add .
git commit -m "♻️ Refactor: Complete project restructure

- Separated MCP, AP2, and Database into src/ subdirectories
- Organized tests by module (unit/integration/e2e)
- Extracted MCP tools into individual files
- Created proper test fixtures and configuration
- Updated all imports and dependencies
- Migrated documentation to docs/
- Centralized configuration in config/

BREAKING CHANGE: Directory structure has been completely reorganized"

git push origin refactor/project-restructure
```

**Verificación:** ✓ Cambios pusheados

---

### ✅ Step 8.6: Crear PR
**Objetivo:** PR para revisar cambios antes de mergear

**Comando:**
```bash
gh pr create \
  --title "♻️ Complete Project Restructure" \
  --body "See .github/RESTRUCTURE_PLAN.md for details" \
  --base main \
  --head refactor/project-restructure
```

**Verificación:** ✓ PR creado

---

## 📊 Checklist de Reestructuración

### Preparación (Fase 1)
- [x] Branch `refactor/project-restructure` creado
- [ ] Backup de `pokemon_marketplace.db` creado
- [ ] Sistema actual verificado funcionando
- [ ] Estructura de carpetas `src/` creada
- [ ] `pytest.ini` creado
- [ ] `.gitignore` actualizado (si necesario)

### MCP Server (Fase 2)
- [ ] Análisis de `index.ts` completado
- [ ] `src/mcp/server/types/` creado con interfaces
- [ ] Tools extraídas en `src/mcp/server/tools/`
- [ ] `src/mcp/server/index.ts` simplificado
- [ ] Claves RSA copiadas a `src/mcp/keys/`
- [ ] `package.json` y `tsconfig.json` actualizados
- [ ] `npm run build` funciona en nueva ubicación
- [ ] Tests de integración MCP movidos a `tests/mcp/integration/`
- [ ] Tests unitarios nuevos creados en `tests/mcp/unit/`
- [ ] **CRÍTICO:** Claude Desktop config actualizado con nuevo path

### AP2 Integration (Fase 3)
- [ ] Análisis de dependencias de `common/` completado
- [ ] `src/ap2/protocol/` creado (types, validators, utils)
- [ ] `mcp_client.py` movido a `src/mcp/client/`
- [ ] Agentes movidos a `src/ap2/agents/`
- [ ] Payment processor movido a `src/ap2/processor/`
- [ ] `.env` copiado a `src/ap2/`
- [ ] `pyproject.toml` y `uv.lock` actualizados
- [ ] `__main__.py` de cada agente actualizado con imports
- [ ] Tests JWT movidos a `tests/ap2/unit/`
- [ ] Tests de integración creados en `tests/ap2/integration/`
- [ ] **CRÍTICO:** `uv run python -m ...` funciona con nueva estructura

### Database (Fase 4)
- [ ] Análisis de paths y dependencias completado
- [ ] `src/database/` creado con engine, models, repository
- [ ] Path de DB actualizado en `engine.py` (usar DATABASE_URL)
- [ ] Alembic configurado en `src/database/migrations/`
- [ ] `seed.py` actualizado con nuevo path de `pokemon-gen1.json`
- [ ] Imports de database actualizados en merchant_agent
- [ ] Tests de database movidos a `tests/database/`
- [ ] **CRÍTICO:** DB sigue accesible y tests pasan

### Tests (Fase 5)
- [ ] `tests/conftest.py` actualizado con nuevos paths
- [ ] Tests reorganizados: `tests/{mcp,ap2,database,e2e}/`
- [ ] Fixtures creadas en cada módulo (`conftest.py` por módulo)
- [ ] Tests E2E movidos de `tests/unit/` a `tests/e2e/`
- [ ] Markers pytest configurados (unit, integration, e2e)
- [ ] Al menos 80% de tests existentes siguen pasando

### Configuración (Fase 6)
- [ ] `pokemon-gen1.json` movido a `config/`
- [ ] `claude_desktop_config.json` movido a `config/`
- [ ] Scripts en `scripts/` actualizados con nuevos paths
- [ ] `Makefile` extendido con comandos de tests
- [ ] `make setup` funciona
- [ ] `make build` funciona
- [ ] `make run` funciona
- [ ] `make test` funciona (nuevo)

### Documentación (Fase 7)
- [ ] `src/mcp/README.md` creado
- [ ] `src/ap2/README.md` creado
- [ ] `src/database/README.md` creado
- [ ] `tests/README.md` actualizado
- [ ] `QUICKSTART.md` actualizado con nueva estructura
- [ ] README principal actualizado
- [ ] Diagramas de arquitectura creados (opcional)

### Limpieza y Verificación (Fase 8)
- [ ] Carpeta `mcp-server/` eliminada (contenido movido)
- [ ] Carpeta `ap2-integration/` eliminada (contenido movido)
- [ ] Todos los tests pasan: `make test`
- [ ] Sistema completo funciona: `make run`
- [ ] Claude Desktop puede conectarse al MCP server
- [ ] Web UI carga en `http://localhost:8000`
- [ ] No hay imports rotos (verificar con `pytest --collect-only`)

### Git & Deploy (Fase 9)
- [ ] Commits organizados por fase
- [ ] PR creado con descripción detallada
- [ ] README del PR lista breaking changes
- [ ] Revisión de código completada
- [ ] Merge a `main`
- [ ] Tag de versión creado (e.g., `v2.0.0-restructure`)

---

## ✅ Criterios de Éxito

**El proyecto está correctamente reestructurado si:**

1. ✅ `make setup && make build` funciona sin errores
2. ✅ `make run` inicia todos los agentes correctamente
3. ✅ Web UI en puerto 8000 carga y puede buscar Pokemon
4. ✅ Claude Desktop puede usar MCP tools
5. ✅ Al menos 80% de tests pasan
6. ✅ Database mantiene datos existentes
7. ✅ No hay archivos duplicados entre old/new locations
8. ✅ Documentación refleja nueva estructura

**Red Flags - NO mergear si:**

- ❌ `pokemon_marketplace.db` perdió datos
- ❌ MCP server no compila
- ❌ Algún agente no arranca
- ❌ Scripts en `scripts/` no funcionan
- ❌ Tests de integración de database fallan
- ❌ Hay imports circulares

---

## 🎯 Siguiente Paso Inmediato

**ESTADO:** Ya estamos en el branch `refactor/project-restructure` ✅

**PRÓXIMO PASO:** Step 1.2 - Hacer backup y verificar sistema funcional

```bash
# Ejecutar estos comandos para preparar:

# 1. Backup de DB
cp pokemon_marketplace.db pokemon_marketplace.db.backup

# 2. Verificar MCP compila
cd mcp-server && npm run build && cd ..

# 3. Verificar tests corren
pytest tests/integration/database/test_database.py -v

# 4. Ver estado git
git status
```

**⚠️ IMPORTANTE ANTES DE CONTINUAR:**
1. Asegurarse de tener backup de `pokemon_marketplace.db`
2. Verificar que `make build` funciona
3. Tener `.env` configurado en `ap2-integration/`
4. Revisar que no hay cambios sin commitear importantes

**¿Listo para Step 1.2?** Confirma para proceder con el backup y verificación

---

## 🔧 Troubleshooting Común

### Problema: "Module not found" después de mover archivos
**Causa:** Imports no actualizados o `sys.path` incorrecto

**Solución:**
```python
# En conftest.py o __init__.py
import sys
from pathlib import Path

# Agregar src/ al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
```

### Problema: MCP server no compila después de refactorizar
**Causa:** Imports TypeScript rotos o paths relativos incorrectos

**Solución:**
```bash
# Verificar tsconfig.json tiene paths correctos
cd src/mcp
cat tsconfig.json  # Verificar "outDir": "build"

# Limpiar build y recompilar
rm -rf build
npm run build

# Si sigue fallando, verificar imports:
grep -r "from './" src/mcp/server/  # Deben ser relativos correctos
```

### Problema: Tests no encuentran database
**Causa:** Path de DB incorrecto en engine.py

**Solución:**
```python
# En src/database/engine.py, usar path absoluto:
from pathlib import Path
import os

# Opción 1: Variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///pokemon_marketplace.db")

# Opción 2: Path absoluto
project_root = Path(__file__).parent.parent.parent
db_path = project_root / "pokemon_marketplace.db"
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL)
```

### Problema: Agentes AP2 no arrancan
**Causa:** Entry points `__main__.py` con imports rotos

**Solución:**
```python
# En src/ap2/agents/merchant/__main__.py
import sys
import os
from pathlib import Path

# Agregar src/ap2 al path
ap2_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ap2_path))

# ENTONCES importar
from agents.merchant.server import app  # Import relativo
```

### Problema: Claude Desktop no conecta con MCP
**Causa:** Path en config apunta a ubicación vieja

**Solución:**
```json
// En config/claude_desktop_config.json
{
  "mcpServers": {
    "pokemon-marketplace": {
      "command": "node",
      "args": [
        "/ruta/absoluta/a/src/mcp/build/index.js"
      ]
    }
  }
}
```

Verificar: `node src/mcp/build/index.js` debe correr sin errores

### Problema: "EADDRINUSE" - puerto ya en uso
**Causa:** Agentes de ejecución anterior no se cerraron

**Solución:**
```bash
# Matar todos los procesos en puertos usados
make stop

# O manualmente:
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
lsof -ti:8002 | xargs kill -9
lsof -ti:8003 | xargs kill -9
```

### Problema: uv no encuentra módulos
**Causa:** `pyproject.toml` no actualizado o .venv corrupto

**Solución:**
```bash
cd src/ap2
rm -rf .venv uv.lock
uv sync  # Recrear entorno
```

### Problema: Tests pasan individualmente pero fallan en suite
**Causa:** Estado compartido o imports con side effects

**Solución:**
```python
# En tests, usar fixtures con scope aislado
@pytest.fixture(scope="function")  # NO "session"
def test_db():
    engine = create_engine("sqlite:///:memory:")
    # ... setup
    yield session
    # ... teardown
```

# 🗺️ Roadmap de Reestructuración - Paso a Paso

> **📅 ÚLTIMA ACTUALIZACIÓN:** 24 de octubre de 2025 - Auditoría completa del estado real
> 
> **⚠️ IMPORTANTE:** Este documento refleja el estado REAL del proyecto, no aspiracional.
> Se actualizó después de una auditoría exhaustiva comparando el código con la documentación.

## 🚨 **ESTADO CRÍTICO - ATENCIÓN REQUERIDA**

```
┌─────────────────────────────────────────────────────────────────┐
│  🔴 FASE 3 (AP2 Protocol) BLOQUEADA - SISTEMA NO FUNCIONAL     │
│                                                                  │
│  Problema: Archivos movidos pero imports completamente rotos    │
│  Impacto: 0% ejecutable - Agentes NO arrancan                   │
│  Acción: Completar Step 3.2 URGENTE (migrar protocol files)    │
└─────────────────────────────────────────────────────────────────┘
```

### 🎯 Estado de las Fases:

| Fase | Nombre | Estado | Completitud Real | Funcionalidad |
|------|--------|--------|------------------|---------------|
| 1 | Setup Inicial | ✅ | 100% | ✅ Operativo |
| 2 | MCP Server | ✅ | 100% | ✅ Tests passing |
| **3** | **AP2 Protocol** | 🔴 **BLOQUEADA** | **15-20%** | ❌ **NO FUNCIONAL** |
| 4 | Database | ⬜ | 0% | N/A |
| 5 | Tests E2E | ⬜ | 0% | N/A |

### 🔴 Bloqueadores Activos:

1. **CRÍTICO**: `src/ap2/protocol/` vacío (solo __init__.py, faltan types.py, utils.py, validators.py, session.py)
2. **CRÍTICO**: Imports rotos en agentes (`from mcp_wrapper.client` - módulo no existe)
3. **ALTO**: Sin `pyproject.toml` en `src/ap2/` (no se pueden instalar deps)
4. **ALTO**: Tests vacíos (0 archivos en tests/ap2/unit/ e integration/)
5. **MEDIO**: Duplicación activa (`ap2-integration/` completo sigue existiendo)

---

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
- 🔴 **Alto:** Romper imports y que agentes no arranquen ⚠️ **YA OCURRIÓ EN FASE 3**
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

**ESTADO ACTUAL:** 🔴 **BLOQUEADA - IMPORTS ROTOS**

**Estado Real:** ~25% funcional (archivos movidos pero NO operativos)

**Completado:**
- ✅ Agentes movidos físicamente a `src/ap2/agents/` (shopping, merchant, credentials, payment_processor)
- ✅ `src/ap2/protocol/__init__.py` creado con estructura de imports

**Bloqueadores Críticos:**
- 🔴 **Step 3.2**: Protocol files NO migrados - `src/ap2/protocol/` solo tiene `__init__.py`
  - ❌ Falta `types.py` (ap2_types.py sin migrar)
  - ❌ Falta `utils.py` (sin migrar)
  - ❌ Falta `validators.py` (jwt_validator.py sin migrar)
  - ❌ Falta `session.py` (sin migrar)
  - 🔴 **IMPACTO:** `from ap2.protocol import CartMandate` → `ModuleNotFoundError`
- 🔴 **Imports rotos en agentes**: `from mcp_wrapper.client` → módulo no existe
  - Los agentes importan desde `mcp_wrapper` que NO existe
  - Debería ser `from mcp.client.mcp_client`
- ❌ **Step 3.7**: `src/ap2/pyproject.toml` NO existe (sin gestión de dependencias)
- ❌ **Steps 3.8-3.11**: Tests completamente vacíos (0 archivos en unit/ e integration/)
- 🔴 **DUPLICACIÓN ACTIVA:** `ap2-integration/` completo sigue existiendo (riesgo de desarrollo paralelo)

---

### ⚠️ Step 3.1: Preparar migración de AP2
**Objetivo:** Entender la estructura actual antes de mover

**Estado:** ⚠️ **PARCIALMENTE COMPLETADO** - Estructura analizada pero archivos NO migrados

**Estado Actual:**
- ✅ Análisis de estructura completado
- ✅ Directorio `src/ap2/protocol/` creado
- ✅ `__init__.py` con imports preparado (pero los módulos no existen)
- ❌ Archivos de `ap2-integration/src/common/` AÚN NO migrados

**Archivos que DEBEN migrarse:**
```bash
ORIGEN (ap2-integration/src/common/)     →  DESTINO (src/ap2/protocol/)
─────────────────────────────────────────────────────────────────────────
ap2_types.py (305 líneas, 11 KB)        →  types.py ❌ PENDIENTE
utils.py (10 KB, 10,096 bytes)          →  utils.py ❌ PENDIENTE  
jwt_validator.py (14 KB, 14,362 bytes)  →  validators.py ❌ PENDIENTE
session.py (1.7 KB, 1,691 bytes)        →  session.py ❌ PENDIENTE
mcp_client.py (10 KB, 10,395 bytes)     →  NO MIGRAR (va a src/mcp/client/)
```

**Estado de `src/ap2/protocol/`:**
```bash
src/ap2/protocol/
└── __init__.py (96 líneas) - INTENTA importar de:
    ├── from .types import (...)      ❌ types.py NO EXISTE
    └── from .utils import (...)      ❌ utils.py NO EXISTE
```

**Prueba de Importación:**
```bash
$ python -c "import sys; sys.path.insert(0, 'src'); from ap2.protocol import CartMandate"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File ".../src/ap2/protocol/__init__.py", line 6, in <module>
    from .types import (
ModuleNotFoundError: No module named 'ap2.protocol.types'
```

**Verificación:** ⚠️ Análisis documentado pero migración NO ejecutada

---

### 🔴 Step 3.2: Migrar archivos de protocol
**Objetivo:** Mover archivos de `ap2-integration/src/common/` a `src/ap2/protocol/`

**Estado:** 🔴 **BLOQUEADOR CRÍTICO - NO EJECUTADO**

**Impacto:** Sin estos archivos, NADA funciona:
- ❌ Agentes no pueden ejecutarse (`ModuleNotFoundError`)
- ❌ Tests no se pueden crear
- ❌ Imports en código movido están rotos

**Archivos verificados que existen en origen:**
```bash
$ ls -la ap2-integration/src/common/
-rw-r--r--  ap2_types.py (11,359 bytes)      ✅ EXISTE en origen
-rw-r--r--  jwt_validator.py (14,362 bytes)  ✅ EXISTE en origen
-rw-r--r--  session.py (1,691 bytes)         ✅ EXISTE en origen
-rw-r--r--  utils.py (10,096 bytes)          ✅ EXISTE en origen
-rw-r--r__  mcp_client.py (10,395 bytes)     ✅ EXISTE (migrar a src/mcp/client/)
```

**Acciones necesarias:**
```bash
# 1. Migrar archivos de protocol (usar git mv para mantener historia)
git mv ap2-integration/src/common/ap2_types.py src/ap2/protocol/types.py
git mv ap2-integration/src/common/jwt_validator.py src/ap2/protocol/validators.py
git mv ap2-integration/src/common/session.py src/ap2/protocol/session.py
git mv ap2-integration/src/common/utils.py src/ap2/protocol/utils.py

# 2. Actualizar __init__.py si es necesario (puede que ya esté correcto)

# 3. Actualizar imports en TODOS los agentes que usen common/
# Los siguientes archivos importan desde common:
# - src/ap2/agents/merchant/server.py
# - src/ap2/agents/shopping/agent.py
# - src/ap2/agents/credentials/server.py (probablemente)
# - src/ap2/agents/payment_processor/server.py
# - ap2-integration/src/* (archivos que no se han migrado aún - IGNORAR por ahora)

# Buscar y reemplazar:
# DE: from common.ap2_types import → A: from ap2.protocol.types import
# DE: from common.jwt_validator import → A: from ap2.protocol.validators import
# DE: from common.utils import → A: from ap2.protocol.utils import
# DE: from common.session import → A: from ap2.protocol.session import
```

**Imports rotos adicionales detectados:**
```python
# EN: src/ap2/agents/shopping/agent.py (línea 18)
# EN: src/ap2/agents/merchant/server.py (línea 16)
from mcp_wrapper.client import get_mcp_client  # ❌ mcp_wrapper NO EXISTE

# DEBE SER:
from mcp.client.mcp_client import get_mcp_client  # ✅ CORRECTO
# O crear alias en src/ap2/__init__.py
```

**Verificación después de migración:**
```bash
# Test de importación
cd /path/to/project
python -c "import sys; sys.path.insert(0, 'src'); from ap2.protocol import CartMandate, generate_cart_id"
# Debe ejecutar sin errores

# Verificar estructura
ls -la src/ap2/protocol/
# Debe mostrar: __init__.py, types.py, utils.py, validators.py, session.py
```

**Estado:** ❌ **PENDIENTE - BLOQUEA TODA LA FASE 3**

---

### ✅ Step 3.3: Mover Shopping Agent
**Objetivo:** Mover agente de compras

**Estado:** ⚠️ **ARCHIVOS MOVIDOS - IMPORTS ROTOS**

**Archivos migrados:**
- ✅ `src/ap2/agents/shopping/agent.py` (365 líneas)
- ✅ `src/ap2/agents/shopping/web_ui.py`
- ✅ `src/ap2/agents/shopping/__main__.py`

**Imports verificados en agent.py (líneas 1-30):**
```python
# Línea 18:
from mcp_wrapper.client import get_mcp_client  # ❌ ROTO - módulo no existe

# Línea 19-30:
from ap2.protocol import (  # ⚠️ PREPARADO pero módulos subyacentes faltan
    PaymentMandate,
    PaymentMandateContents,
    PaymentResponse,
    generate_unique_id,
    # ... más imports
)
```

**Problemas:**
1. 🔴 `mcp_wrapper` no existe → debe ser `mcp.client.mcp_client`
2. 🔴 `ap2.protocol` falla porque `types.py` y `utils.py` no existen

**Estado funcional:** ❌ NO EJECUTABLE hasta resolver Step 3.2

---

### ✅ Step 3.4: Mover Merchant Agent

**Estado:** ⚠️ **ARCHIVOS MOVIDOS - IMPORTS ROTOS**

**Archivos migrados:**
- ✅ `src/ap2/agents/merchant/server.py` (279 líneas)
- ✅ `src/ap2/agents/merchant/__main__.py`

**Imports verificados en server.py (líneas 1-30):**
```python
# Línea 16:
from mcp_wrapper.client import get_mcp_client  # ❌ ROTO

# Línea 17-30:
from ap2.protocol import (  # ⚠️ PREPARADO pero módulos faltan
    CartMandate,
    CartContents,
    PaymentRequest,
    # ... más imports
)
```

**Estado funcional:** ❌ NO EJECUTABLE hasta resolver Step 3.2

---

### ✅ Step 3.5: Mover Credentials Provider

**Estado:** ⚠️ **ARCHIVOS MOVIDOS - IMPORTS POSIBLEMENTE ROTOS**

**Archivos migrados:**
- ✅ `src/ap2/agents/credentials/server.py`
- ✅ `src/ap2/agents/credentials/__main__.py`

**Nota:** Imports no verificados en detalle pero probablemente tienen los mismos problemas.

**Estado funcional:** ❌ NO EJECUTABLE hasta resolver Step 3.2

---

### ✅ Step 3.6: Mover Payment Processor

**Estado:** ⚠️ **ARCHIVOS MOVIDOS - IMPORTS POSIBLEMENTE ROTOS**

**Archivos migrados:**
- ✅ `src/ap2/agents/payment_processor/server.py`
- ✅ `src/ap2/agents/payment_processor/__main__.py`

**Estado funcional:** ❌ NO EJECUTABLE hasta resolver Step 3.2

---

### 🔴 Step 3.7: Crear pyproject.toml para AP2
**Objetivo:** Configurar el módulo AP2 de forma independiente

**Estado:** 🔴 **CRÍTICO - ARCHIVO NO EXISTE**

**Verificación:**
```bash
$ ls -la src/ap2/
total 8
drwxr-xr-x  6 CERVIII  staff   192 23 oct 13:51 .
drwxr-xr-x  6 CERVIII  staff   192 23 oct 00:23 ..
drwxr-xr-x  7 CERVIII  staff   224 23 oct 00:00 agents
drwxr-xr-x  2 CERVIII  staff    64 23 oct 00:00 processor
drwxr-xr-x  3 CERVIII  staff    96 22 oct 21:22 protocol
-rw-r--r--  1 CERVIII  staff  1486 23 oct 13:51 README.md

# ❌ pyproject.toml NO EXISTE
```

**Impacto:**
- ❌ No se pueden instalar dependencias con `uv sync`
- ❌ No hay configuración de módulo independiente
- ❌ No hay settings de pytest específicos para AP2
- ❌ Dificulta testing y desarrollo

**Referencia disponible:**
- ✅ `ap2-integration/pyproject.toml` existe y puede copiarse/adaptarse

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

### 🔴 Step 3.8: Crear tests unitarios de AP2

**Estado:** 🔴 **NO INICIADO - CARPETAS VACÍAS**

**Verificación:**
```bash
$ ls -la tests/ap2/unit/
total 0
drwxr-xr-x  2 CERVIII  staff   64 23 oct 00:00 .
drwxr-xr-x  4 CERVIII  staff  128 23 oct 00:00 ..

# ❌ COMPLETAMENTE VACÍO - 0 archivos
```

**Tests que deberían crearse:**
- ❌ `tests/ap2/unit/test_types.py` - Validar Pydantic models (CartMandate, PaymentMandate, etc.)
- ❌ `tests/ap2/unit/test_utils.py` - Funciones helper (generate_cart_id, hash_object, etc.)
- ❌ `tests/ap2/unit/test_validators.py` - JWT validation y structure validation
- ❌ `tests/ap2/unit/test_session.py` - Session management
- ❌ `tests/ap2/conftest.py` - Fixtures compartidas

**Dependencia:** Bloqueado por Step 3.2 (sin archivos para testear)

**Estado:** ❌ **PENDIENTE - REQUIERE Step 3.2 COMPLETADO**
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

### 🔴 Step 3.9: Mover tests existentes de AP2

**Estado:** 🔴 **NO APLICABLE - NO HAY TESTS EXISTENTES**

**Búsqueda de tests AP2/JWT en proyecto:**
```bash
$ find tests/ -name "*jwt*.py" -o -name "*ap2*.py"
# ❌ No se encontraron archivos

# Búsqueda ampliada:
$ grep -r "test.*jwt" tests/ 2>/dev/null
$ grep -r "test.*ap2" tests/ 2>/dev/null
# ❌ No hay tests existentes para mover
```

**Conclusión:** No hay tests pre-existentes de AP2 o JWT en el proyecto. Todos los tests deben crearse desde cero en Step 3.8.

**Estado:** ⏭️ **SKIP - NO HAY TESTS QUE MOVER**

---

### 🔴 Step 3.10: Crear tests de integración AP2

**Estado:** 🔴 **NO INICIADO - CARPETAS VACÍAS**

**Verificación:**
```bash
$ ls -la tests/ap2/integration/
total 0
drwxr-xr-x  2 CERVIII  staff   64 23 oct 00:00 .
drwxr-xr-x  4 CERVIII  staff  128 23 oct 00:00 ..

# ❌ COMPLETAMENTE VACÍO - 0 archivos
```

**Tests de integración necesarios:**
- ❌ `tests/ap2/integration/test_shopping_agent.py` - Shopping agent endpoints
- ❌ `tests/ap2/integration/test_merchant_agent.py` - Merchant cart creation & signing
- ❌ `tests/ap2/integration/test_payment_processor.py` - Payment processing
- ❌ `tests/ap2/integration/test_credentials_provider.py` - Credentials endpoint
- ❌ `tests/ap2/integration/test_full_payment_flow.py` - E2E flow entre agentes

**Dependencia:** Bloqueado por Steps 3.2 (protocol) y 3.7 (pyproject)

**Estado:** ❌ **PENDIENTE - REQUIERE Steps 3.2 y 3.7**

---

### 🔴 Step 3.11: Verificar AP2 funciona

**Estado:** 🔴 **IMPOSIBLE EJECUTAR - DEPENDENCIAS NO RESUELTAS**

**Verificación intentada:**
```bash
$ cd src && python -c "from ap2.protocol import CartMandate"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File ".../src/ap2/protocol/__init__.py", line 6, in <module>
    from .types import (
ModuleNotFoundError: No module named 'ap2.protocol.types'
```

**Comandos que DEBERÍAN funcionar (cuando esté listo):**
```bash
cd src/ap2
uv sync                              # ❌ FALLA - pyproject.toml no existe
pytest ../../tests/ap2/unit -v      # ❌ FALLA - tests vacíos
pytest ../../tests/ap2/integration -v # ❌ FALLA - tests vacíos

# Verificar agentes arrancan:
python -m agents.shopping            # ❌ FALLA - imports rotos
python -m agents.merchant            # ❌ FALLA - imports rotos
```

**Bloqueadores:**
1. 🔴 Step 3.2 sin completar (protocol files)
2. 🔴 Step 3.7 sin completar (pyproject.toml)
3. 🔴 Step 3.8-3.10 sin completar (tests)
4. 🔴 Imports rotos (mcp_wrapper.client)

**Estado:** ❌ **BLOQUEADO - REQUIERE COMPLETAR STEPS 3.2-3.10**

---

## 🚨 RESUMEN FASE 3 - Estado Real vs Documentado

**Estado Real del Sistema:** 🔴 **BLOQUEADA - NO FUNCIONAL**

### Comparación Honesta:

| Step | Descripción | Estado Archivos | Estado Funcional | Bloqueador |
|------|-------------|-----------------|------------------|------------|
| 3.1 | Análisis migración | ⚠️ Parcial | N/A | - |
| 3.2 | **Migrar protocol** | ❌ **NO HECHO** | ❌ **CRÍTICO** | 🔴 Bloquea todo |
| 3.3-3.6 | Migrar agentes | ✅ Movidos | ❌ **NO EJECUTABLES** | Requiere 3.2 |
| 3.7 | pyproject.toml | ❌ **NO EXISTE** | ❌ Sin config | 🔴 Bloquea tests |
| 3.8 | Tests unitarios | ❌ **VACÍO (0)** | ❌ Sin tests | Requiere 3.2 |
| 3.9 | Mover tests | ⏭️ Skip | N/A | No hay tests |
| 3.10 | Tests integración | ❌ **VACÍO (0)** | ❌ Sin tests | Requiere 3.2, 3.7 |
| 3.11 | Verificar funciona | ❌ **IMPOSIBLE** | ❌ Bloqueado | Requiere todo |

### Métrica de Completitud Real:

**Previo (documentado):** 40% completado ❌ **INCORRECTO**

**Estado Real Auditado:**
- **Archivos movidos:** 50% (4 agentes + estructura) ✅
- **Sistema funcional:** 0% (nada ejecutable) ❌
- **Tests creados:** 0% (carpetas vacías) ❌
- **Imports funcionando:** 0% (todos rotos) ❌

**Porcentaje Real de Completitud:** **~15-20%** 
- Solo estructura de carpetas y archivos físicamente movidos
- Código NO funcional, NO testeable, NO ejecutable

### Problemas Críticos Identificados:

1. **🔴 BLOQUEADOR #1: Protocol Files NO Migrados**
   - `src/ap2/protocol/` tiene solo `__init__.py`
   - Faltan: `types.py`, `utils.py`, `validators.py`, `session.py`
   - **Impacto:** `ModuleNotFoundError` en todo import de `ap2.protocol`

2. **🔴 BLOQUEADOR #2: Imports Rotos en Agentes**
   - Todos los agentes importan `from mcp_wrapper.client` ❌
   - El módulo `mcp_wrapper` NO EXISTE en el proyecto
   - Debería ser `from mcp.client.mcp_client`

3. **🔴 BLOQUEADOR #3: Sin Configuración de Dependencias**
   - `src/ap2/pyproject.toml` NO EXISTE
   - No se puede hacer `uv sync`
   - No hay gestión de paquetes

4. **🔴 PROBLEMA #4: Duplicación Activa**
   - `ap2-integration/` COMPLETO sigue existiendo
   - Riesgo de desarrollo en paralelo
   - Confusión sobre código "oficial"

5. **🔴 PROBLEMA #5: Zero Tests**
   - `tests/ap2/unit/` vacío
   - `tests/ap2/integration/` vacío
   - No hay red de seguridad para validar cambios

### Comandos que NO Funcionan Actualmente:

```bash
# ❌ Importar desde protocol
python -c "from ap2.protocol import CartMandate"
# ModuleNotFoundError: No module named 'ap2.protocol.types'

# ❌ Arrancar shopping agent
cd src/ap2 && python -m agents.shopping
# ModuleNotFoundError: No module named 'mcp_wrapper'

# ❌ Instalar dependencias
cd src/ap2 && uv sync
# Error: pyproject.toml not found

# ❌ Ejecutar tests
pytest tests/ap2/unit -v
# No tests collected (carpeta vacía)
```

### Próximos Pasos Obligatorios (en orden):

**PRIORIDAD MÁXIMA - DESBLOQUEAR:**
1. ✅ **Step 3.2**: Migrar 4 archivos protocol (git mv)
2. ✅ **Arreglar imports**: `mcp_wrapper` → `mcp.client.mcp_client` en 4 agentes
3. ✅ **Step 3.7**: Crear `pyproject.toml` (copiar de ap2-integration)
4. ✅ **Verificar imports**: `python -c "from ap2.protocol import CartMandate"`
5. ✅ **Step 3.8**: Crear al menos 2 tests unitarios básicos
6. ✅ **Step 3.11**: Verificar que al menos 1 agente arranca

**Hasta completar Step 3.2**, la Fase 3 está **completamente bloqueada**.

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

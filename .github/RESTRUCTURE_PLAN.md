# 🏗️ Plan de Reestructuración del Repositorio

## 📋 Objetivos
1. Separar claramente MCP, AP2 Protocol y Database
2. Organizar tests por módulo con estructura clara
3. Mejorar mantenibilidad y escalabilidad
4. Facilitar testing unitario e integración

## 🎯 Estructura Propuesta

```
mcp-adk-ap2-agent-pokemon/
├── .github/
│   ├── workflows/           # CI/CD pipelines
│   ├── issues/              # Issue templates
│   └── RESTRUCTURE_PLAN.md  # Este documento
├── .vscode/                 # VS Code settings
├── docs/                    # 📚 Documentación centralizada
│   ├── api/                 # Documentación de APIs
│   ├── architecture/        # Diagramas de arquitectura
│   ├── QUICKSTART.md        
│   ├── ROADMAP.md
│   └── README.md
├── config/                  # ⚙️ Configuración centralizada
│   ├── claude_desktop_config.json
│   ├── pokemon-gen1.json
│   └── environment/
│       ├── .env.example
│       └── .env.test
├── src/                     # 💻 Código fuente principal
│   ├── mcp/                 # 🔌 Model Context Protocol Server
│   │   ├── server/
│   │   │   ├── index.ts     # MCP Server principal
│   │   │   ├── tools/       # Implementación de tools
│   │   │   │   ├── pokemon-info.ts
│   │   │   │   ├── pokemon-price.ts
│   │   │   │   ├── search-pokemon.ts
│   │   │   │   ├── cart-management.ts
│   │   │   │   └── index.ts
│   │   │   └── types/       # TypeScript types
│   │   │       ├── pokemon.ts
│   │   │       ├── cart.ts
│   │   │       └── index.ts
│   │   ├── client/          # MCP Client utilities
│   │   │   └── mcp_client.py
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   ├── ap2/                 # 💳 Agent Payments Protocol (AP2)
│   │   ├── agents/
│   │   │   ├── shopping/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── __main__.py
│   │   │   │   ├── agent.py
│   │   │   │   └── web_ui.py
│   │   │   ├── merchant/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── __main__.py
│   │   │   │   └── server.py
│   │   │   └── credentials_provider/
│   │   │       ├── __main__.py
│   │   │       └── server.py
│   │   ├── protocol/
│   │   │   ├── __init__.py
│   │   │   ├── types.py     # AP2 types (CartMandate, etc.)
│   │   │   ├── validators.py
│   │   │   └── utils.py
│   │   ├── processor/
│   │   │   ├── __init__.py
│   │   │   ├── __main__.py
│   │   │   └── server.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── database/            # 🗄️ Database Layer (SQLAlchemy)
│       ├── __init__.py
│       ├── engine.py        # Database engine & session
│       ├── models.py        # SQLAlchemy models
│       ├── repository.py    # Repository pattern
│       ├── migrations/      # Alembic migrations
│       │   ├── versions/
│       │   ├── env.py
│       │   └── alembic.ini
│       ├── seeds/           # Database seeders
│       │   ├── pokemon_seeder.py
│       │   └── test_data.py
│       └── README.md
│
├── tests/                   # 🧪 Tests organizados por módulo
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures globales
│   ├── mcp/                 # Tests del MCP Server
│   │   ├── __init__.py
│   │   ├── conftest.py      # Fixtures específicas de MCP
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_pokemon_info_tool.py
│   │   │   ├── test_pokemon_price_tool.py
│   │   │   ├── test_search_tool.py
│   │   │   ├── test_cart_tool.py
│   │   │   └── test_types.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_mcp_server.py
│   │   │   ├── test_mcp_client.py
│   │   │   └── test_tools_integration.py
│   │   └── README.md
│   │
│   ├── ap2/                 # Tests del AP2 Protocol
│   │   ├── __init__.py
│   │   ├── conftest.py      # Fixtures específicas de AP2
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_cart_mandate.py
│   │   │   ├── test_jwt_generation.py
│   │   │   ├── test_jwt_validation.py
│   │   │   ├── test_rsa_keys.py
│   │   │   └── test_protocol_types.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_shopping_agent.py
│   │   │   ├── test_merchant_agent.py
│   │   │   ├── test_payment_processor.py
│   │   │   └── test_full_payment_flow.py
│   │   └── README.md
│   │
│   ├── database/            # Tests de Database Layer
│   │   ├── __init__.py
│   │   ├── conftest.py      # Fixtures específicas de DB
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_pokemon_repository.py
│   │   │   ├── test_transaction_repository.py
│   │   │   ├── test_cart_repository.py
│   │   │   └── test_engine.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_cart_persistence.py
│   │   │   ├── test_transaction_flow.py
│   │   │   └── test_migrations.py
│   │   └── README.md
│   │
│   └── e2e/                 # Tests End-to-End
│       ├── __init__.py
│       ├── test_purchase_flow.py
│       ├── test_ap2_full_integration.py
│       └── README.md
│
├── scripts/                 # 🔧 Scripts de utilidad
│   ├── setup.sh
│   ├── clean.sh
│   ├── run-mcp-server.sh
│   ├── run-ap2-agents.sh
│   ├── run-shopping-agent.sh
│   ├── test-all.sh          # Ejecutar todos los tests
│   ├── test-mcp.sh          # Tests solo de MCP
│   ├── test-ap2.sh          # Tests solo de AP2
│   ├── test-database.sh     # Tests solo de Database
│   ├── create-issues.sh
│   ├── create-labels.sh
│   ├── apply-labels-to-issues.sh
│   └── README.md
│
├── .gitignore
├── Makefile                 # Comandos principales
├── README.md                # README principal
├── package.json             # Root package.json (workspaces)
└── pytest.ini               # Configuración de pytest

```

## 📦 Cambios Detallados

### 1. MCP Server (`src/mcp/`)
**Estado Actual (FUNCIONAL):**
```
mcp-server/
├── src/
│   └── index.ts (694 líneas - COMPILADO Y FUNCIONANDO)
├── build/               # Salida de TypeScript
│   ├── index.js
│   └── index.d.ts
├── keys/                # Claves RSA para JWT
│   ├── merchant_private.pem
│   └── merchant_public.pem
├── package.json         # Configurado con npm
├── tsconfig.json
└── README.md
```

**Después de Reestructuración:**
```
src/mcp/
├── server/
│   ├── index.ts           # Entry point (~100 líneas)
│   ├── tools/
│   │   ├── pokemon-info.ts      # get_pokemon_info
│   │   ├── pokemon-price.ts     # get_pokemon_price
│   │   ├── search-pokemon.ts    # search_pokemon
│   │   ├── list-types.ts        # list_pokemon_types
│   │   ├── cart-management.ts   # create_cart, get_cart, get_current_cart
│   │   ├── product-info.ts      # get_pokemon_product
│   │   └── index.ts             # Tool registry
│   └── types/
│       ├── pokemon.ts
│       ├── cart.ts
│       └── index.ts
├── build/               # Salida compilada
├── keys/                # Claves RSA (MANTENER UBICACIÓN)
├── client/
│   └── mcp_client.py
├── package.json
├── tsconfig.json
└── README.md
```

**⚠️ CRÍTICO - Preservar funcionalidad:**
- El MCP server usa `npm run build` → debe seguir usando npm (no yarn/pnpm)
- Las claves RSA en `keys/` son necesarias para JWT - copiarlas, no moverlas
- El archivo compilado `build/index.js` es el que usa Claude Desktop
- Scripts actuales ejecutan `cd mcp-server && npm run build` - actualizar paths

### 2. AP2 Protocol (`src/ap2/`)
**Estado Actual (FUNCIONAL):**
```
ap2-integration/
├── .env                # Variables de entorno (GOOGLE_API_KEY, etc.)
├── .env.example
├── pyproject.toml      # Configurado con uv
├── uv.lock             # Lock file de uv
└── src/
    ├── common/
    │   ├── ap2_types.py       # Tipos AP2
    │   ├── jwt_validator.py   # Validación JWT
    │   ├── mcp_client.py      # Cliente MCP
    │   ├── session.py         # Gestión de sesiones
    │   └── utils.py
    ├── shopping_agent/
    │   ├── __main__.py        # Entry point
    │   ├── agent.py           # Lógica del agente
    │   └── web_ui.py          # FastAPI UI (puerto 8000)
    ├── merchant_agent/
    │   ├── __main__.py        # Entry point (puerto 8001)
    │   └── server.py
    ├── payment_processor/
    │   ├── __main__.py        # Entry point (puerto 8003)
    │   └── server.py
    ├── credentials_provider/
    │   ├── __main__.py        # Entry point (puerto 8002)
    │   └── server.py
    └── database/
        ├── engine.py          # SQLAlchemy engine
        ├── models.py          # Modelos DB
        ├── repository.py      # Repositorio
        ├── seed.py            # Seeders
        └── cli.py             # CLI commands
```

**Después de Reestructuración:**
```
src/ap2/
├── .env                # MANTENER variables de entorno
├── .env.example
├── pyproject.toml      # Configuración uv
├── uv.lock
├── agents/
│   ├── shopping/
│   │   ├── __main__.py        # MANTENER entry points
│   │   ├── agent.py
│   │   └── web_ui.py
│   ├── merchant/
│   │   ├── __main__.py
│   │   └── server.py
│   └── credentials_provider/
│       ├── __main__.py
│       └── server.py
├── protocol/
│   ├── types.py        # De ap2_types.py
│   ├── validators.py   # De jwt_validator.py
│   ├── session.py      # MANTENER gestión de sesiones
│   └── utils.py
├── processor/
│   ├── __main__.py
│   └── server.py
└── README.md
```

**⚠️ CRÍTICO - Preservar funcionalidad:**
- Todos los agentes tienen `__main__.py` que configuran puertos y dotenv
- Scripts ejecutan `uv run python -m src.merchant_agent` - actualizar imports
- `.env` con GOOGLE_API_KEY es esencial - copiar a nueva ubicación
- Los entry points deben mantener la lógica de `sys.path.insert()` actualizada

### 3. Database Layer (`src/database/`)
**Estado Actual (FUNCIONAL - dentro de ap2-integration):**
```
ap2-integration/src/database/
├── __init__.py
├── engine.py           # SQLAlchemy engine con SessionLocal
├── models.py           # Pokemon, Transaction, Cart, CartItem
├── repository.py       # CRUD operations
├── seed.py             # Ya existe seeder
└── cli.py              # CLI para operaciones DB
```

**Archivo de Base de Datos Actual:**
```
pokemon_marketplace.db  # En el root del proyecto - FUNCIONAL
```

**Después de Reestructuración:**
```
src/database/
├── __init__.py
├── engine.py           # MANTENER lógica de conexión exacta
├── models.py           # MANTENER modelos como están
├── repository.py       # MANTENER interface
├── seed.py             # Ya existe
├── cli.py              # Ya existe
├── migrations/
│   ├── versions/       # Para migraciones Alembic (NUEVO)
│   ├── env.py
│   └── alembic.ini
└── README.md
```

**⚠️ CRÍTICO - Preservar funcionalidad:**
- La DB `pokemon_marketplace.db` debe seguir accesible desde nueva ubicación
- El engine usa `sqlite:///../../pokemon_marketplace.db` - actualizar path relativo
- Los modelos tienen relaciones y constraints que deben mantenerse intactos
- Repository es usado por merchant_agent y tests - imports críticos
- NO crear migraciones que rompan schema existente - la DB ya tiene datos

### 4. Tests Reorganizados (`tests/`)
**Estado Actual (YA PARCIALMENTE ORGANIZADO):**
```
tests/
├── conftest.py         # Global config con sys.path setup
├── README.md
├── test_unified_mcp.sh # Script shell para tests MCP
├── unit/               # Tests unitarios existentes
│   ├── conftest.py
│   ├── test_e2e_flow.py
│   └── test_inventory_update.py
├── integration/        # YA organizados por módulo
│   ├── mcp/
│   │   ├── test_mcp.py
│   │   ├── test_mcp_simple.py
│   │   ├── test_mcp_debug.py
│   │   └── test_mcp_debugging.py
│   ├── database/
│   │   ├── test_database.py
│   │   ├── test_cart_persistence.py
│   │   └── test_get_cart.py
│   ├── jwt/
│   │   ├── test_jwt_generation.py
│   │   ├── test_jwt_signature.py
│   │   ├── test_jwt_validation.py
│   │   └── test_rsa_persistence.py
│   └── ap2/
└── e2e/
```

**Después de Reestructuración (MEJORAR, NO ROMPER):**
```
tests/
├── conftest.py         # MANTENER configuración global
├── pytest.ini          # NUEVO - configuración pytest
├── README.md
├── mcp/
│   ├── conftest.py     # Fixtures específicas MCP
│   ├── unit/           # NUEVOS tests unitarios por tool
│   │   ├── test_pokemon_info_tool.py
│   │   ├── test_pokemon_price_tool.py
│   │   ├── test_search_tool.py
│   │   └── test_cart_tool.py
│   └── integration/    # MOVER desde tests/integration/mcp/
│       ├── test_mcp_server.py
│       └── test_mcp_client.py
├── ap2/
│   ├── conftest.py
│   ├── unit/           # MOVER desde tests/integration/jwt/
│   │   ├── test_jwt_generation.py
│   │   ├── test_jwt_validation.py
│   │   └── test_protocol_types.py
│   └── integration/    # NUEVOS + algunos movidos
│       ├── test_shopping_agent.py
│       ├── test_merchant_agent.py
│       └── test_full_payment_flow.py
├── database/
│   ├── conftest.py
│   ├── unit/           # NUEVOS tests de modelos
│   │   ├── test_models.py
│   │   └── test_repository.py
│   └── integration/    # MOVER desde tests/integration/database/
│       ├── test_cart_persistence.py
│       └── test_database.py
└── e2e/                # MOVER desde tests/unit/
    ├── test_e2e_flow.py
    └── test_inventory_update.py
```

**⚠️ CRÍTICO - Preservar funcionalidad:**
- `tests/conftest.py` tiene sys.path setup ESENCIAL - debe actualizarse, no eliminarse
- Los tests integration/mcp usan scripts `.sh` - mantener compatibilidad
- Tests usan imports relativos a `ap2-integration/src/` - actualizar tras mover
- NO borrar tests existentes - solo reorganizar
- Algunos tests pueden estar rotos - marcarlos con `@pytest.mark.skip` si es necesario

## 🎯 Beneficios de la Nueva Estructura

### ✅ Separación de Responsabilidades
- **MCP**: Todo lo relacionado con el protocolo MCP en `src/mcp/`
- **AP2**: Todo lo relacionado con pagos en `src/ap2/`
- **Database**: Capa de datos completamente independiente en `src/database/`

### ✅ Tests Organizados
- **Unit tests**: Tests aislados por módulo
- **Integration tests**: Tests de integración entre componentes
- **E2E tests**: Tests de flujo completo

### ✅ Mejor Mantenibilidad
- Archivos más pequeños y enfocados
- Fácil localización de código
- Menos acoplamiento entre módulos

### ✅ Escalabilidad
- Fácil agregar nuevas tools al MCP
- Fácil agregar nuevos agentes AP2
- Fácil agregar nuevos modelos de DB

## 🚀 Plan de Migración

### Fase 1: Preparación
1. ✅ Crear este documento de planificación
2. ⬜ Crear nueva estructura de carpetas
3. ⬜ Configurar pytest.ini y conftest.py
4. ⬜ Actualizar .gitignore

### Fase 2: Migración de MCP
1. ⬜ Crear `src/mcp/server/tools/` con archivos separados
2. ⬜ Crear `src/mcp/server/types/` para TypeScript types
3. ⬜ Refactorizar `index.ts` para usar los nuevos módulos
4. ⬜ Mover `mcp_client.py` a `src/mcp/client/`
5. ⬜ Actualizar imports y paths
6. ⬜ Crear tests unitarios en `tests/mcp/unit/`
7. ⬜ Mover tests existentes a `tests/mcp/integration/`

### Fase 3: Migración de AP2
1. ⬜ Crear `src/ap2/protocol/` y mover `ap2_types.py` → `types.py`
2. ⬜ Crear `src/ap2/agents/` y mover agentes
3. ⬜ Crear `src/ap2/processor/` y mover payment processor
4. ⬜ Actualizar imports en todos los archivos
5. ⬜ Crear tests unitarios en `tests/ap2/unit/`
6. ⬜ Mover tests existentes a `tests/ap2/integration/`

### Fase 4: Migración de Database
1. ⬜ Mover `ap2-integration/src/database/` → `src/database/`
2. ⬜ Crear `src/database/migrations/` con Alembic
3. ⬜ Crear `src/database/seeds/` para data inicial
4. ⬜ Actualizar imports en MCP y AP2
5. ⬜ Crear tests unitarios en `tests/database/unit/`
6. ⬜ Mover tests existentes a `tests/database/integration/`

### Fase 5: Tests E2E
1. ⬜ Crear `tests/e2e/`
2. ⬜ Crear test de flujo completo de compra
3. ⬜ Crear test de integración AP2 completa

### Fase 6: Configuración y Scripts
1. ⬜ Mover configuraciones a `config/`
2. ⬜ Actualizar scripts en `scripts/`
3. ⬜ Crear scripts específicos para cada módulo
4. ⬜ Actualizar Makefile

### Fase 7: Documentación
1. ⬜ Mover docs a `docs/`
2. ⬜ Crear README por módulo
3. ⬜ Actualizar README principal
4. ⬜ Crear diagramas de arquitectura

### Fase 8: Cleanup
1. ⬜ Eliminar carpetas antiguas
2. ⬜ Actualizar todos los imports
3. ⬜ Verificar que todos los tests pasen
4. ⬜ Actualizar CI/CD workflows

## 📝 Comandos Make (Extender los Existentes)

**Comandos Actuales que FUNCIONAN:**
```makefile
make setup      # Install + build (npm + uv)
make install    # Solo dependencias
make build      # Solo compilar TypeScript
make run        # Ejecutar TODO (build + agentes + web)
make run-agents # Solo agentes AP2
make run-web    # Solo Web UI
make stop       # Detener todos los puertos
make clean      # Limpiar builds y caches
make test       # Ejecutar tests (NECESITA IMPLEMENTACIÓN)
```

**Comandos NUEVOS a Agregar (después de reestructuración):**
```makefile
# Tests (NUEVOS - actualmente no implementados)
test:           # Ejecutar todos los tests con pytest
test-mcp:       # pytest tests/mcp -v
test-ap2:       # pytest tests/ap2 -v
test-db:        # pytest tests/database -v
test-e2e:       # pytest tests/e2e -v
test-unit:      # pytest -m unit
test-int:       # pytest -m integration

# Coverage (NUEVOS)
coverage:       # pytest --cov=src --cov-report=html
coverage-mcp:   # Coverage solo MCP
coverage-ap2:   # Coverage solo AP2
coverage-db:    # Coverage solo Database

# Database (NUEVOS)
db-init:        # Inicializar base de datos
db-migrate:     # alembic upgrade head
db-seed:        # python -m src.database.seed
db-reset:       # Limpiar y recrear DB

# Development (YA EXISTEN - mantener)
dev-mcp:        # cd mcp-server && npm run dev
dev-ap2:        # Equivalente a make run-agents
dev-all:        # Equivalente a make run
```

**⚠️ IMPORTANTE:**
- El Makefile actual (173 líneas) está bien estructurado y FUNCIONA
- NO reescribir desde cero - EXTENDER con nuevos comandos
- Mantener colores y formato existente
- Los scripts en `scripts/` ya funcionan - solo actualizar paths cuando se muevan archivos

## ⚠️ Consideraciones CRÍTICAS

1. **Backwards Compatibility - ESENCIAL**: 
   - **Claude Desktop config** (`claude_desktop_config.json`) apunta a `mcp-server/build/index.js`
   - **Scripts en `scripts/`** ejecutan paths específicos: `cd mcp-server`, `cd ap2-integration`
   - **Entry points Python** usan `python -m src.merchant_agent` - depende de estructura actual
   - **Imports** en todos los archivos tienen paths relativos que romperán
   - **Variables de entorno** en `ap2-integration/.env` - debe copiarse

2. **Testing Durante Migración**:
   - Los tests YA están parcialmente organizados - no todos funcionan
   - `tests/integration/` tiene tests que SÍ funcionan - preservarlos
   - Ejecutar `pytest tests/integration/database -v` después de mover DB
   - Ejecutar `pytest tests/integration/mcp -v` después de mover MCP
   - Tests pueden fallar temporalmente - NO borrar, marcar con `@pytest.mark.skip`

3. **Git History**:
   - Usar `git mv` para TODOS los archivos - preserva historia
   - NO copiar y borrar - usar mv
   - Commit por módulo: primero MCP, luego AP2, luego Database

4. **Dependencies**:
   - `mcp-server/package.json` usa npm - mantener npm
   - `ap2-integration/pyproject.toml` usa uv - mantener uv
   - `mcp-server/keys/` contiene claves RSA - COPIAR, no mover (necesarias en ambos lugares durante migración)

5. **Base de Datos Existente**:
   - `pokemon_marketplace.db` tiene datos reales - NO borrar
   - Hacer backup antes de migrar: `cp pokemon_marketplace.db pokemon_marketplace.db.backup`
   - Los paths relativos en `engine.py` deben actualizarse correctamente

6. **Puertos en Uso**:
   - 8000: Shopping Web UI
   - 8001: Merchant Agent
   - 8002: Credentials Provider
   - 8003: Payment Processor
   - Estos están hardcoded en `__main__.py` de cada agente - documentar

## 🎯 Resultado Final

Una estructura clara, modular y escalable que facilita:
- ✅ Desarrollo independiente de cada módulo
- ✅ Testing exhaustivo y organizado
- ✅ Onboarding de nuevos desarrolladores
- ✅ Mantenimiento a largo plazo
- ✅ Expansión futura del proyecto

---

## 📋 Comandos de Verificación Rápida

**Antes de empezar:**
```bash
# Estado actual
git branch --show-current      # Debe ser: refactor/project-restructure
make build                     # Debe compilar sin errores
pytest tests/integration/database -v  # Tests de DB deben correr

# Backup
cp pokemon_marketplace.db pokemon_marketplace.db.backup
```

**Después de cada fase:**
```bash
# Verificar compilación
cd src/mcp && npm run build && cd ../..

# Verificar imports Python
python -c "import sys; sys.path.insert(0, 'src'); from ap2.protocol import types"

# Verificar tests
pytest tests/mcp -v
pytest tests/ap2 -v
pytest tests/database -v

# Verificar sistema completo
make stop && make run
```

**Antes de PR:**
```bash
# Full check
make clean
make setup
make build
make test         # Todos los tests
make run          # Sistema completo

# Verificar no hay duplicados
find . -name "*.py" -path "*/mcp-server/*" 2>/dev/null  # Debe estar vacío
find . -name "*.py" -path "*/ap2-integration/*" 2>/dev/null  # Debe estar vacío
```

---

## 🔗 Referencias

- **MCP SDK Docs:** https://modelcontextprotocol.io/
- **AP2 Protocol:** Ver `docs/architecture/ap2-protocol.md` (crear si no existe)
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **pytest Docs:** https://docs.pytest.org/

---

## 📝 Notas Finales

**Este plan es un documento vivo.** Si encuentras problemas durante la migración:

1. Documenta el problema en este archivo (sección Troubleshooting)
2. Ajusta el plan si es necesario
3. Commitea cambios al plan junto con el código

**Principio guía:** "Si funciona, no lo rompas. Si lo mueves, asegúrate de que sigue funcionando."

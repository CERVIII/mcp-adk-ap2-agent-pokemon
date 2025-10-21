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
**Antes:**
```
mcp-server/
├── src/
│   └── index.ts (694 líneas)
├── package.json
└── tsconfig.json
```

**Después:**
```
src/mcp/
├── server/
│   ├── index.ts           # Entry point (~100 líneas)
│   ├── tools/
│   │   ├── pokemon-info.ts      # get_pokemon_info
│   │   ├── pokemon-price.ts     # get_pokemon_price
│   │   ├── search-pokemon.ts    # search_pokemon
│   │   ├── list-types.ts        # list_pokemon_types
│   │   ├── cart-management.ts   # create_cart, get_cart
│   │   ├── product-info.ts      # get_pokemon_product
│   │   └── index.ts             # Tool registry
│   └── types/
│       ├── pokemon.ts
│       ├── cart.ts
│       └── index.ts
├── client/
│   └── mcp_client.py
├── package.json
├── tsconfig.json
└── README.md
```

### 2. AP2 Protocol (`src/ap2/`)
**Antes:**
```
ap2-integration/
└── src/
    ├── common/
    │   ├── ap2_types.py
    │   ├── mcp_client.py
    │   └── utils.py
    ├── shopping_agent/
    ├── merchant_agent/
    ├── payment_processor/
    └── credentials_provider/
```

**Después:**
```
src/ap2/
├── agents/
│   ├── shopping/
│   │   ├── agent.py
│   │   └── web_ui.py
│   ├── merchant/
│   │   └── server.py
│   └── credentials_provider/
│       └── server.py
├── protocol/
│   ├── types.py        # CartMandate, PaymentRequest, etc.
│   ├── validators.py
│   └── utils.py
├── processor/
│   └── server.py
├── pyproject.toml
└── README.md
```

### 3. Database Layer (`src/database/`)
**Antes:**
```
ap2-integration/src/database/
├── __init__.py
├── engine.py
├── models.py
└── repository.py
```

**Después:**
```
src/database/
├── __init__.py
├── engine.py
├── models.py
├── repository.py
├── migrations/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── seeds/
│   ├── pokemon_seeder.py
│   └── test_data.py
└── README.md
```

### 4. Tests Reorganizados (`tests/`)
**Antes:**
```
tests/
├── test_mcp.py
├── test_mcp_simple.py
├── test_database.py
├── test_cart_persistence.py
├── test_jwt_generation.py
└── ... (mezclados)
```

**Después:**
```
tests/
├── conftest.py
├── mcp/
│   ├── unit/
│   │   ├── test_pokemon_info_tool.py
│   │   ├── test_pokemon_price_tool.py
│   │   ├── test_search_tool.py
│   │   └── test_cart_tool.py
│   └── integration/
│       ├── test_mcp_server.py
│       └── test_mcp_client.py
├── ap2/
│   ├── unit/
│   │   ├── test_jwt_generation.py
│   │   ├── test_jwt_validation.py
│   │   └── test_cart_mandate.py
│   └── integration/
│       ├── test_shopping_agent.py
│       ├── test_merchant_agent.py
│       └── test_full_payment_flow.py
├── database/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_pokemon_repository.py
│   │   └── test_cart_repository.py
│   └── integration/
│       ├── test_cart_persistence.py
│       └── test_transaction_flow.py
└── e2e/
    ├── test_purchase_flow.py
    └── test_ap2_full_integration.py
```

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

## 📝 Comandos Make Propuestos

```makefile
# Tests
test:           # Ejecutar todos los tests
test-mcp:       # Solo tests de MCP
test-ap2:       # Solo tests de AP2
test-db:        # Solo tests de Database
test-e2e:       # Solo tests E2E
test-unit:      # Solo tests unitarios
test-int:       # Solo tests de integración

# Coverage
coverage:       # Coverage de todos los módulos
coverage-mcp:   # Coverage solo MCP
coverage-ap2:   # Coverage solo AP2
coverage-db:    # Coverage solo Database

# Development
dev-mcp:        # Ejecutar MCP server en modo dev
dev-ap2:        # Ejecutar AP2 agents en modo dev
dev-all:        # Ejecutar todo el stack

# Database
db-init:        # Inicializar base de datos
db-migrate:     # Ejecutar migraciones
db-seed:        # Seed data inicial
db-reset:       # Reset completo de DB
```

## ⚠️ Consideraciones

1. **Backwards Compatibility**: Necesitamos actualizar:
   - Claude Desktop config
   - Scripts existentes
   - Imports en todos los archivos Python/TypeScript

2. **Testing**: Ejecutar tests constantemente durante la migración

3. **Git History**: Usar `git mv` para preservar historia

4. **Dependencies**: Actualizar package.json y pyproject.toml

## 🎯 Resultado Final

Una estructura clara, modular y escalable que facilita:
- ✅ Desarrollo independiente de cada módulo
- ✅ Testing exhaustivo y organizado
- ✅ Onboarding de nuevos desarrolladores
- ✅ Mantenimiento a largo plazo
- ✅ Expansión futura del proyecto

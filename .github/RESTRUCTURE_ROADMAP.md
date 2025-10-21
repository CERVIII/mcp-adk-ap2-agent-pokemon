# 🗺️ Roadmap de Reestructuración - Paso a Paso

## 📍 Estado Actual
- Branch: `docs/roadmap-issues`
- Último commit: Labels aplicados a issues
- Base de datos: `pokemon_marketplace.db` existe
- MCP Server: Funcional en `mcp-server/src/index.ts`
- AP2 Agents: Funcionando en `ap2-integration/src/`

---

## 🎯 Fase 1: Preparación y Setup Inicial

### ✅ Step 1.1: Crear branch de reestructuración
**Objetivo:** Trabajar en una rama separada para no afectar `main` ni `feat/cart-persistence`

**Acciones:**
```bash
git checkout main
git pull origin main
git checkout -b refactor/project-restructure
```

**Verificación:** ✓ Branch creado correctamente

---

### ✅ Step 1.2: Crear estructura base de carpetas
**Objetivo:** Crear la nueva estructura de directorios vacía

**Acciones:**
```bash
# Crear directorios principales
mkdir -p src/{mcp,ap2,database}
mkdir -p tests/{mcp,ap2,database,e2e}
mkdir -p config docs/api docs/architecture

# Crear subdirectorios de MCP
mkdir -p src/mcp/{server,client}
mkdir -p src/mcp/server/{tools,types}

# Crear subdirectorios de AP2
mkdir -p src/ap2/{agents,protocol,processor}
mkdir -p src/ap2/agents/{shopping,merchant,credentials_provider}

# Crear subdirectorios de Database
mkdir -p src/database/{migrations,seeds}

# Crear subdirectorios de Tests
mkdir -p tests/mcp/{unit,integration}
mkdir -p tests/ap2/{unit,integration}
mkdir -p tests/database/{unit,integration}
```

**Archivos a crear:**
- `src/mcp/README.md`
- `src/ap2/README.md`
- `src/database/README.md`
- `tests/README.md`
- `tests/conftest.py`

**Verificación:** ✓ Estructura de carpetas creada

---

### ✅ Step 1.3: Configurar pytest
**Objetivo:** Setup de pytest para la nueva estructura

**Archivo:** `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    mcp: MCP related tests
    ap2: AP2 protocol tests
    database: Database tests
```

**Archivo:** `tests/conftest.py`
```python
"""Global pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture(scope="session")
def test_data_dir():
    """Returns path to test data directory"""
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def config_dir():
    """Returns path to config directory"""
    return Path(__file__).parent.parent / "config"
```

**Verificación:** ✓ pytest configurado

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

### ✅ Step 2.1: Extraer types de MCP
**Objetivo:** Separar tipos TypeScript en archivos dedicados

**Archivo:** `src/mcp/server/types/pokemon.ts`
```typescript
export interface PokemonInfo {
  id: number;
  name: string;
  types: string[];
  abilities: string[];
  stats: {
    hp: number;
    attack: number;
    defense: number;
    specialAttack: number;
    specialDefense: number;
    speed: number;
  };
  sprites: {
    front_default: string;
    front_shiny?: string;
  };
}

export interface PokemonPrice {
  numero: number;
  nombre: string;
  precio: number;
  enVenta: boolean;
  inventario: {
    total: number;
    disponibles: number;
    vendidos: number;
  };
}
```

**Archivo:** `src/mcp/server/types/cart.ts`
```typescript
export interface CartMandate {
  contents: {
    id: string;
    user_signature_required: boolean;
    payment_request: PaymentRequest;
  };
  merchant_signature: string;
  timestamp: string;
  merchantName: string;
}

export interface PaymentRequest {
  amount: number;
  currency: string;
  items: CartItem[];
  merchant_info: MerchantInfo;
}
```

**Archivo:** `src/mcp/server/types/index.ts`
```typescript
export * from './pokemon';
export * from './cart';
```

**Verificación:** ✓ Types extraídos

---

### ✅ Step 2.2: Extraer tool: get_pokemon_info
**Objetivo:** Separar la tool en archivo dedicado

**Archivo:** `src/mcp/server/tools/pokemon-info.ts`
```typescript
import { z } from 'zod';
import { PokemonInfo } from '../types';

export const getPokemonInfoSchema = z.object({
  pokemon: z.string().describe("Pokemon name or ID number")
});

export async function getPokemonInfo(pokemon: string): Promise<PokemonInfo> {
  // Implementación actual del tool
  // ... código movido desde index.ts
}
```

**Verificación:** ✓ Tool extraída

---

### ✅ Step 2.3: Extraer tool: get_pokemon_price
**Objetivo:** Separar la tool en archivo dedicado

**Archivo:** `src/mcp/server/tools/pokemon-price.ts`

**Verificación:** ✓ Tool extraída

---

### ✅ Step 2.4: Extraer tool: search_pokemon
**Archivo:** `src/mcp/server/tools/search-pokemon.ts`

---

### ✅ Step 2.5: Extraer tool: list_pokemon_types
**Archivo:** `src/mcp/server/tools/list-types.ts`

---

### ✅ Step 2.6: Extraer tool: create_pokemon_cart
**Archivo:** `src/mcp/server/tools/cart-management.ts`

---

### ✅ Step 2.7: Extraer tool: get_pokemon_product
**Archivo:** `src/mcp/server/tools/product-info.ts`

---

### ✅ Step 2.8: Crear registro de tools
**Objetivo:** Centralizar el registro de todas las tools

**Archivo:** `src/mcp/server/tools/index.ts`
```typescript
import { getPokemonInfo, getPokemonInfoSchema } from './pokemon-info';
import { getPokemonPrice, getPokemonPriceSchema } from './pokemon-price';
// ... otros imports

export const TOOLS = [
  {
    name: "get_pokemon_info",
    description: "Get detailed information about a Pokémon...",
    inputSchema: zodToJsonSchema(getPokemonInfoSchema),
    handler: getPokemonInfo
  },
  // ... otras tools
];

export {
  getPokemonInfo,
  getPokemonPrice,
  // ... otras funciones
};
```

**Verificación:** ✓ Registry creado

---

### ✅ Step 2.9: Refactorizar index.ts
**Objetivo:** Simplificar el archivo principal usando los módulos

**Archivo:** `src/mcp/server/index.ts`
```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { TOOLS } from './tools/index.js';

const server = new Server({
  name: 'pokemon-mcp-server',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
});

// Register tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS.map(t => ({
    name: t.name,
    description: t.description,
    inputSchema: t.inputSchema
  }))
}));

// ... resto del código simplificado
```

**Verificación:** ✓ index.ts refactorizado (~100 líneas)

---

### ✅ Step 2.10: Mover MCP client
**Objetivo:** Mover cliente Python a src/mcp/client/

**Acción:**
```bash
git mv ap2-integration/src/common/mcp_client.py src/mcp/client/mcp_client.py
```

**Actualizar imports en:**
- `ap2-integration/src/shopping_agent/agent.py`
- Otros archivos que usen mcp_client

**Verificación:** ✓ Cliente movido e imports actualizados

---

### ✅ Step 2.11: Crear tests unitarios de MCP
**Objetivo:** Tests para cada tool individual

**Archivo:** `tests/mcp/conftest.py`
```python
import pytest
from pathlib import Path
import json

@pytest.fixture
def pokemon_catalog():
    """Load pokemon catalog for testing"""
    catalog_path = Path(__file__).parent.parent.parent / "config" / "pokemon-gen1.json"
    with open(catalog_path) as f:
        return json.load(f)

@pytest.fixture
def mock_pokeapi(requests_mock):
    """Mock PokeAPI responses"""
    # Setup mocks
    pass
```

**Archivo:** `tests/mcp/unit/test_pokemon_info_tool.py`
```python
import pytest

@pytest.mark.unit
@pytest.mark.mcp
def test_get_pokemon_info_by_name(mock_pokeapi):
    """Test getting pokemon info by name"""
    # Test implementation
    pass

@pytest.mark.unit
@pytest.mark.mcp
def test_get_pokemon_info_by_number(mock_pokeapi):
    """Test getting pokemon info by number"""
    pass
```

**Crear tests para:**
- `test_pokemon_price_tool.py`
- `test_search_tool.py`
- `test_cart_tool.py`
- `test_list_types_tool.py`
- `test_product_info_tool.py`

**Verificación:** ✓ Tests unitarios creados

---

### ✅ Step 2.12: Mover tests de integración de MCP
**Objetivo:** Reorganizar tests existentes

**Acciones:**
```bash
git mv tests/test_mcp_simple.py tests/mcp/integration/test_mcp_server_basic.py
git mv tests/test_mcp.py tests/mcp/integration/test_mcp_server_full.py
git mv tests/test_mcp_debug.py tests/mcp/integration/test_mcp_debugging.py
```

**Actualizar imports en los archivos movidos**

**Verificación:** ✓ Tests de integración reorganizados

---

### ✅ Step 2.13: Actualizar package.json de MCP
**Objetivo:** Configurar correctamente el módulo MCP

**Archivo:** `src/mcp/package.json`
```json
{
  "name": "@pokemon-marketplace/mcp-server",
  "version": "1.0.0",
  "type": "module",
  "main": "build/index.js",
  "types": "build/index.d.ts",
  "bin": {
    "pokemon-mcp-server": "./build/index.js"
  },
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch",
    "test": "pytest ../../tests/mcp"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.4",
    "zod": "^3.23.8",
    "zod-to-json-schema": "^3.23.5"
  }
}
```

**Verificación:** ✓ package.json actualizado

---

### ✅ Step 2.14: Verificar MCP funciona
**Objetivo:** Asegurar que MCP sigue funcionando después de refactorización

**Comandos:**
```bash
cd src/mcp
npm install
npm run build
pytest ../../tests/mcp/unit -v
pytest ../../tests/mcp/integration -v
```

**Verificación:** ✓ Todos los tests pasan

---

## 🎯 Fase 3: Migración del AP2 Protocol

### ✅ Step 3.1: Crear módulo de protocol
**Objetivo:** Separar tipos y validadores AP2

**Archivo:** `src/ap2/protocol/types.py`
```python
"""AP2 Protocol Types"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class PaymentRequest:
    amount: float
    currency: str
    items: List[Dict[str, Any]]
    merchant_info: Dict[str, Any]

@dataclass
class CartMandate:
    contents: Dict[str, Any]
    merchant_signature: str
    timestamp: str
    merchantName: str

# ... otros tipos
```

**Acción:**
```bash
git mv ap2-integration/src/common/ap2_types.py src/ap2/protocol/types.py
```

**Verificación:** ✓ Types movidos

---

### ✅ Step 3.2: Crear utilidades de protocol
**Archivo:** `src/ap2/protocol/utils.py`

**Acción:**
```bash
git mv ap2-integration/src/common/utils.py src/ap2/protocol/utils.py
```

---

### ✅ Step 3.3: Mover Shopping Agent
**Objetivo:** Mover agente de compras

**Acciones:**
```bash
git mv ap2-integration/src/shopping_agent/* src/ap2/agents/shopping/
```

**Actualizar imports en:**
- `src/ap2/agents/shopping/agent.py`
- `src/ap2/agents/shopping/web_ui.py`

**Verificación:** ✓ Shopping agent movido

---

### ✅ Step 3.4: Mover Merchant Agent
**Acciones:**
```bash
git mv ap2-integration/src/merchant_agent/* src/ap2/agents/merchant/
```

---

### ✅ Step 3.5: Mover Credentials Provider
**Acciones:**
```bash
git mv ap2-integration/src/credentials_provider/* src/ap2/agents/credentials_provider/
```

---

### ✅ Step 3.6: Mover Payment Processor
**Acciones:**
```bash
git mv ap2-integration/src/payment_processor/* src/ap2/processor/
```

---

### ✅ Step 3.7: Actualizar pyproject.toml
**Objetivo:** Configurar el módulo AP2

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

**Verificación:** ✓ pyproject.toml creado

---

### ✅ Step 3.8: Crear tests unitarios de AP2
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

**Verificación:** ✓ Tests unitarios creados

---

### ✅ Step 3.9: Mover tests existentes de AP2
**Acciones:**
```bash
git mv tests/test_jwt_generation.py tests/ap2/unit/test_jwt_generation.py
git mv tests/test_jwt_validation.py tests/ap2/unit/test_jwt_validation.py
git mv tests/test_jwt_signature.py tests/ap2/unit/test_jwt_signature.py
git mv tests/test_rsa_persistence.py tests/ap2/unit/test_rsa_persistence.py
```

**Verificación:** ✓ Tests movidos

---

### ✅ Step 3.10: Crear tests de integración AP2
**Crear:**
- `tests/ap2/integration/test_shopping_agent.py`
- `tests/ap2/integration/test_merchant_agent.py`
- `tests/ap2/integration/test_payment_processor.py`
- `tests/ap2/integration/test_full_payment_flow.py`

**Verificación:** ✓ Tests de integración creados

---

### ✅ Step 3.11: Verificar AP2 funciona
**Comandos:**
```bash
cd src/ap2
uv sync
pytest ../../tests/ap2/unit -v
pytest ../../tests/ap2/integration -v
```

**Verificación:** ✓ Todos los tests pasan

---

## 🎯 Fase 4: Migración de Database Layer

### ✅ Step 4.1: Mover módulo de database
**Acciones:**
```bash
git mv ap2-integration/src/database/* src/database/
```

**Archivos movidos:**
- `__init__.py`
- `engine.py`
- `models.py`
- `repository.py`

**Verificación:** ✓ Database movida

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

## 📊 Checklist Final

### Estructura
- [ ] `src/mcp/` creado y poblado
- [ ] `src/ap2/` creado y poblado
- [ ] `src/database/` creado y poblado
- [ ] `tests/` reorganizado por módulo
- [ ] `config/` centralizado
- [ ] `docs/` organizado

### MCP
- [ ] Tools extraídas en archivos separados
- [ ] Types separados
- [ ] index.ts refactorizado
- [ ] Tests unitarios creados
- [ ] Tests de integración movidos

### AP2
- [ ] Protocol types separados
- [ ] Agents reorganizados
- [ ] Processor separado
- [ ] Tests unitarios creados
- [ ] Tests de integración creados

### Database
- [ ] Módulo movido a src/database
- [ ] Alembic configurado
- [ ] Seeders creados
- [ ] Tests unitarios creados
- [ ] Tests de integración creados

### Tests
- [ ] pytest.ini configurado
- [ ] conftest.py globales y por módulo
- [ ] Tests E2E creados
- [ ] Todos los tests pasan
- [ ] Cobertura > 80%

### Configuración
- [ ] .gitignore actualizado
- [ ] Makefile actualizado
- [ ] Scripts actualizados
- [ ] package.json actualizado
- [ ] pyproject.toml actualizado

### Documentación
- [ ] READMEs por módulo
- [ ] Docs movidos a docs/
- [ ] README principal actualizado
- [ ] Diagramas de arquitectura

### Git
- [ ] Branch creado
- [ ] Commits organizados
- [ ] PR creado
- [ ] CI/CD actualizado (si existe)

---

## 🎯 Siguiente Paso Inmediato

**PASO 1.1**: Crear branch de reestructuración

```bash
git checkout main
git pull origin main
git checkout -b refactor/project-restructure
```

**¿Listo para empezar?** Confirma para proceder con el Step 1.1

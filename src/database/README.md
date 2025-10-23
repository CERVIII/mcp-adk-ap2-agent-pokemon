# Database Layer - Pokemon Marketplace

Capa de base de datos con SQLAlchemy para persistencia de transacciones y carritos.

## Estructura

```
src/database/
├── __init__.py
├── engine.py             # SQLAlchemy engine y SessionLocal
├── models.py             # Modelos: Pokemon, Transaction, Cart, CartItem
├── repository.py         # CRUD operations
├── seed.py               # Database seeder
├── cli.py                # CLI commands
└── migrations/           # Alembic migrations (futuro)
    └── versions/
```

## Modelos

- **Pokemon** - Catálogo de Pokemon con inventario
- **Transaction** - Transacciones de compra
- **Cart** - Carritos de compra
- **CartItem** - Items en carritos

## Base de Datos

- **Archivo**: `pokemon_marketplace.db` (SQLite)
- **Ubicación**: Raíz del proyecto
- **Schema**: Ver `models.py`

## Uso

```python
from database import get_db, PokemonRepository

# Obtener sesión
db = next(get_db())

# Usar repository
repo = PokemonRepository(db)
pokemon = repo.get_by_id(25)  # Pikachu
```

## CLI

```bash
# Seed database
python -m src.database.seed

# Otros comandos
python -m src.database.cli --help
```

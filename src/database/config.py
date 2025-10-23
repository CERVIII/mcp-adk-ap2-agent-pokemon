"""
Database configuration

Centralized configuration for SQLite database connection and settings.
"""

from pathlib import Path
import os

# Database file path calculation
# From src/database/config.py -> ../../pokemon_marketplace.db (project root)
BASE_DIR = Path(__file__).parent.parent.parent
DATABASE_PATH = BASE_DIR / "pokemon_marketplace.db"

# Fallback: Use absolute path resolution if relative path calculation fails
if not DATABASE_PATH.parent.name == "mcp-adk-ap2-agent-pokemon":
    DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "pokemon_marketplace.db"

# SQLite connection string
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLite connection arguments
SQLITE_CONNECT_ARGS = {
    "check_same_thread": False,  # Required for FastAPI multi-threading
}

# Engine configuration
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"  # SQL query logging

# Session configuration
SESSION_AUTOCOMMIT = False
SESSION_AUTOFLUSH = False

# SQLite pragmas
ENABLE_FOREIGN_KEYS = True  # Enforce foreign key constraints

# Pool configuration (SQLite doesn't use connection pooling, but kept for consistency)
POOL_SIZE = 5
MAX_OVERFLOW = 10
POOL_PRE_PING = True  # Verify connections before using them

# Pokemon data source
POKEMON_DATA_PATH = BASE_DIR / "pokemon-gen1.json"

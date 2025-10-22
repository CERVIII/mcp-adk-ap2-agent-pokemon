"""
Database Module
SQLite database for Pokemon marketplace with inventory, transactions, and carts.
"""

from .config import DATABASE_URL, DATABASE_PATH, DATABASE_ECHO
from .engine import engine, SessionLocal, get_db, init_db, get_db_stats
from .models import Base, Pokemon, Transaction, TransactionItem, Cart, CartItem
from .repository import PokemonRepository, TransactionRepository, CartRepository

__all__ = [
    # Configuration
    "DATABASE_URL",
    "DATABASE_PATH",
    "DATABASE_ECHO",
    
    # Engine & Sessions
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "get_db_stats",
    
    # Models
    "Base",
    "Pokemon",
    "Transaction",
    "TransactionItem",
    "Cart",
    "CartItem",
    
    # Repositories
    "PokemonRepository",
    "TransactionRepository",
    "CartRepository",
]

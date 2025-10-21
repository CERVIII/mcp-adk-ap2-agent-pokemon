"""
Database engine and session configuration

SQLite database for Pokemon marketplace with:
- Pokemon catalog
- Transaction history
- Inventory management
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from pathlib import Path
import os

# Database file path (in project root)
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATABASE_PATH = BASE_DIR / "pokemon_marketplace.db"

# SQLite connection string
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with SQLite optimizations
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for FastAPI
    echo=False,  # Set to True for SQL query debugging
)


# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints in SQLite"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency function for FastAPI endpoints.
    
    Usage:
        @app.get("/pokemon")
        def get_pokemon(db: Session = Depends(get_db)):
            return db.query(Pokemon).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    
    Call this once at startup to ensure tables exist.
    """
    from .models import Base
    
    print(f"🗄️  Initializing database at: {DATABASE_PATH}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    if DATABASE_PATH.exists():
        size_mb = DATABASE_PATH.stat().st_size / (1024 * 1024)
        print(f"✅ Database initialized ({size_mb:.2f} MB)")
    else:
        print("✅ Database tables created")
    
    return engine


def get_db_stats() -> dict:
    """Get database statistics"""
    from .models import Pokemon, Transaction
    
    with SessionLocal() as db:
        pokemon_count = db.query(Pokemon).count()
        transaction_count = db.query(Transaction).count()
        
        return {
            "database_path": str(DATABASE_PATH),
            "database_size_mb": (
                DATABASE_PATH.stat().st_size / (1024 * 1024)
                if DATABASE_PATH.exists()
                else 0
            ),
            "pokemon_count": pokemon_count,
            "transaction_count": transaction_count,
        }

#!/usr/bin/env python3
"""
Migration script to remove UNIQUE constraint from carts.session_id

This allows multiple carts per session (active, completed, expired, etc.)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.database import engine, SessionLocal


def migrate_cart_schema():
    """Remove UNIQUE constraint from carts.session_id"""
    
    print("🔄 Starting cart schema migration...")
    print(f"📍 Database: {engine.url}")
    
    with SessionLocal() as db:
        try:
            # Check if table exists
            result = db.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='carts'"
            ))
            if not result.fetchone():
                print("⚠️  Table 'carts' does not exist. Nothing to migrate.")
                return
            
            # Backup existing data
            print("💾 Backing up existing cart data...")
            result = db.execute(text("SELECT * FROM carts"))
            carts = result.fetchall()
            columns = result.keys()
            print(f"   Found {len(carts)} carts to preserve")
            
            # Drop and recreate table
            print("🔨 Dropping old 'carts' table...")
            db.execute(text("DROP TABLE IF EXISTS cart_items"))  # Drop dependent table first
            db.execute(text("DROP TABLE IF EXISTS carts"))
            db.commit()
            
            print("✨ Creating new 'carts' table (without UNIQUE constraint)...")
            db.execute(text("""
                CREATE TABLE carts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(100) NOT NULL,
                    user_id VARCHAR(100),
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    expires_at DATETIME
                )
            """))
            
            # Create indexes
            print("📇 Creating indexes...")
            db.execute(text("CREATE INDEX ix_carts_session_id ON carts (session_id)"))
            db.execute(text("CREATE INDEX ix_carts_user_id ON carts (user_id)"))
            db.execute(text("CREATE INDEX ix_carts_status ON carts (status)"))
            db.execute(text("CREATE INDEX ix_carts_created_at ON carts (created_at)"))
            
            # Recreate cart_items table
            print("🔨 Recreating 'cart_items' table...")
            db.execute(text("""
                CREATE TABLE cart_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cart_id INTEGER NOT NULL,
                    pokemon_numero INTEGER NOT NULL,
                    pokemon_name VARCHAR(50) NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    unit_price FLOAT NOT NULL,
                    total_price FLOAT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE
                )
            """))
            
            db.execute(text("CREATE INDEX ix_cart_items_cart_id ON cart_items (cart_id)"))
            db.execute(text("CREATE INDEX ix_cart_items_pokemon_numero ON cart_items (pokemon_numero)"))
            
            db.commit()
            
            # Restore data if any
            if carts:
                print(f"📦 Restoring {len(carts)} carts...")
                for cart in carts:
                    cart_dict = dict(zip(columns, cart))
                    db.execute(text("""
                        INSERT INTO carts (id, session_id, user_id, status, created_at, updated_at, expires_at)
                        VALUES (:id, :session_id, :user_id, :status, :created_at, :updated_at, :expires_at)
                    """), cart_dict)
                db.commit()
                print(f"   ✅ Restored {len(carts)} carts")
            
            print("\n✅ Migration completed successfully!")
            print("   ℹ️  Cart session_id is now NON-UNIQUE")
            print("   ℹ️  Multiple carts per session are now allowed (completed, expired, etc.)")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            db.rollback()
            raise


if __name__ == "__main__":
    migrate_cart_schema()

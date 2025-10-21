#!/usr/bin/env python3
"""
Migration script: JSON to SQLite

Migrates pokemon-gen1.json data to SQLite database.
Run this once to populate the database with initial Pokemon catalog.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import init_db, SessionLocal, Pokemon


def load_pokemon_json():
    """Load Pokemon data from JSON file"""
    json_path = Path(__file__).parent.parent.parent / "pokemon-gen1.json"
    
    if not json_path.exists():
        raise FileNotFoundError(f"Pokemon JSON not found: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def migrate_pokemon_to_db():
    """Migrate all Pokemon from JSON to database"""
    print("\n" + "="*60)
    print("🔄 MIGRATING POKEMON DATA TO DATABASE")
    print("="*60)
    
    # Load JSON data
    print("\n📂 Loading pokemon-gen1.json...")
    pokemon_data = load_pokemon_json()
    print(f"✅ Loaded {len(pokemon_data)} Pokemon from JSON")
    
    # Initialize database
    print("\n🗄️  Initializing database...")
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(Pokemon).count()
        
        if existing_count > 0:
            print(f"\n⚠️  Database already contains {existing_count} Pokemon")
            response = input("   Clear and re-import? (yes/no): ").strip().lower()
            
            if response == "yes":
                print("   Deleting existing data...")
                db.query(Pokemon).delete()
                db.commit()
                print("   ✅ Existing data cleared")
            else:
                print("   ❌ Migration cancelled")
                return
        
        # Insert Pokemon
        print(f"\n💾 Inserting {len(pokemon_data)} Pokemon into database...")
        
        inserted = 0
        errors = 0
        
        for poke_data in pokemon_data:
            try:
                pokemon = Pokemon(
                    numero=poke_data["numero"],
                    nombre=poke_data["nombre"],
                    precio=poke_data["precio"],
                    en_venta=poke_data.get("enVenta", True),
                    inventario_total=poke_data["inventario"]["total"],
                    inventario_disponible=poke_data["inventario"]["disponibles"],
                    inventario_vendido=poke_data["inventario"]["vendidos"],
                )
                
                db.add(pokemon)
                inserted += 1
                
                # Progress indicator
                if inserted % 10 == 0:
                    print(f"   Progress: {inserted}/{len(pokemon_data)}", end="\r")
                
            except Exception as e:
                errors += 1
                print(f"\n   ❌ Error with {poke_data.get('nombre', '???')}: {e}")
        
        # Commit all changes
        print(f"\n   Committing changes...")
        db.commit()
        
        # Summary
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETE")
        print("="*60)
        print(f"   • Inserted: {inserted} Pokemon")
        print(f"   • Errors: {errors}")
        print(f"   • Total in DB: {db.query(Pokemon).count()}")
        
        # Show sample
        print("\n📊 Sample Pokemon in database:")
        sample = db.query(Pokemon).limit(5).all()
        for p in sample:
            print(f"   • #{p.numero:03d} {p.nombre}: ${p.precio} "
                  f"({p.inventario_disponible}/{p.inventario_total} available)")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_migration():
    """Verify migration was successful"""
    print("\n" + "="*60)
    print("🔍 VERIFYING MIGRATION")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Count total
        total = db.query(Pokemon).count()
        print(f"\n✅ Total Pokemon in database: {total}")
        
        # Check inventory
        available = db.query(Pokemon).filter(Pokemon.en_venta == True).count()
        print(f"✅ Pokemon available for sale: {available}")
        
        # Check total inventory
        from sqlalchemy import func
        total_stock = db.query(
            func.sum(Pokemon.inventario_disponible)
        ).scalar() or 0
        print(f"✅ Total stock available: {total_stock} units")
        
        # Price range
        min_price = db.query(func.min(Pokemon.precio)).scalar()
        max_price = db.query(func.max(Pokemon.precio)).scalar()
        avg_price = db.query(func.avg(Pokemon.precio)).scalar()
        print(f"✅ Price range: ${min_price} - ${max_price} (avg: ${avg_price:.2f})")
        
        # Most expensive
        print("\n💎 Most expensive Pokemon:")
        expensive = db.query(Pokemon).order_by(
            Pokemon.precio.desc()
        ).limit(3).all()
        for p in expensive:
            print(f"   • {p.nombre}: ${p.precio}")
        
        # Cheapest
        print("\n💰 Cheapest Pokemon:")
        cheap = db.query(Pokemon).order_by(Pokemon.precio).limit(3).all()
        for p in cheap:
            print(f"   • {p.nombre}: ${p.precio}")
        
        print("\n" + "="*60)
        print("✅ VERIFICATION COMPLETE")
        print("="*60)
        
    finally:
        db.close()


def main():
    """Main migration workflow"""
    try:
        migrate_pokemon_to_db()
        verify_migration()
        
        print("\n🎉 Migration successful!")
        print("   You can now use the database instead of pokemon-gen1.json")
        print(f"   Database file: pokemon_marketplace.db")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

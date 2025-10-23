"""
Seed database with Pokemon data from pokemon-gen1.json
"""
import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from .engine import SessionLocal, init_db
from .models import Pokemon


def load_pokemon_data() -> list:
    """Load Pokemon data from pokemon-gen1.json"""
    # Path from ap2-integration/src/database/seed.py to pokemon-gen1.json
    current_dir = Path(__file__).parent
    json_path = current_dir.parent.parent.parent / "pokemon-gen1.json"
    
    if not json_path.exists():
        raise FileNotFoundError(f"Pokemon data file not found at: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def seed_pokemon(db: Session) -> int:
    """
    Seed Pokemon table with data from pokemon-gen1.json
    
    Returns:
        Number of Pokemon added
    """
    # Check if already seeded
    existing_count = db.query(Pokemon).count()
    if existing_count > 0:
        print(f"⚠️  Database already contains {existing_count} Pokemon")
        print("   Skipping seed (use clear_pokemon() first if you want to reseed)")
        return 0
    
    # Load data
    pokemon_data = load_pokemon_data()
    print(f"📦 Loading {len(pokemon_data)} Pokemon from pokemon-gen1.json...")
    
    # Insert Pokemon
    added_count = 0
    for poke in pokemon_data:
        pokemon = Pokemon(
            numero=poke['numero'],
            nombre=poke['nombre'],
            precio=poke['precio'],
            en_venta=poke['enVenta'],
            inventario_total=poke['inventario']['total'],
            inventario_disponible=poke['inventario']['disponibles'],
            inventario_vendido=poke['inventario']['vendidos']
        )
        db.add(pokemon)
        added_count += 1
    
    db.commit()
    print(f"✅ Successfully seeded {added_count} Pokemon to database")
    return added_count


def clear_pokemon(db: Session) -> int:
    """
    Clear all Pokemon from database
    
    Returns:
        Number of Pokemon removed
    """
    count = db.query(Pokemon).count()
    if count == 0:
        print("ℹ️  Database is already empty")
        return 0
    
    db.query(Pokemon).delete()
    db.commit()
    print(f"🗑️  Removed {count} Pokemon from database")
    return count


def seed_database(force: bool = False):
    """
    Main seed function - initializes database and loads Pokemon
    
    Args:
        force: If True, clears existing data before seeding
    """
    print("=" * 60)
    print("🌱 Pokemon Database Seeder")
    print("=" * 60)
    
    # Initialize database (creates tables if they don't exist)
    init_db()
    
    # Seed data
    with SessionLocal() as db:
        if force:
            print("\n🔄 Force mode: Clearing existing data...")
            clear_pokemon(db)
        
        print("\n📥 Seeding Pokemon data...")
        added = seed_pokemon(db)
        
        # Show stats
        total = db.query(Pokemon).count()
        available = db.query(Pokemon).filter(Pokemon.en_venta == True).count()
        
        print("\n" + "=" * 60)
        print("📊 Database Stats:")
        print(f"   Total Pokemon: {total}")
        print(f"   Available for sale: {available}")
        print(f"   Not for sale: {total - available}")
        print("=" * 60)
        print("✅ Seeding complete!")


if __name__ == "__main__":
    import sys
    
    # Check for --force flag
    force = "--force" in sys.argv
    
    try:
        seed_database(force=force)
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

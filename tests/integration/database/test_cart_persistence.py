#!/usr/bin/env python3
"""
Test Cart Persistence

Tests cart storage, session management, and expiration functionality.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent / "ap2-integration"))

from src.database import (
    init_db,
    SessionLocal,
    Pokemon,
    Cart,
    CartItem,
    PokemonRepository,
    CartRepository
)


def cleanup_test_data():
    """Clean up test data from previous runs"""
    db = SessionLocal()
    try:
        # Delete test carts
        db.execute(text("DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE session_id LIKE 'test_%' OR session_id LIKE 'user_%')"))
        db.execute(text("DELETE FROM carts WHERE session_id LIKE 'test_%' OR session_id LIKE 'user_%'"))
        db.commit()
        print("🧹 Cleaned up test data from previous runs")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean test data: {e}")
        db.rollback()
    finally:
        db.close()


def test_initialize_db():
    """Test 1: Initialize database with cart tables"""
    print("\n" + "=" * 60)
    print("Test 1: Initialize Database with Cart Tables")
    print("=" * 60)
    
    try:
        init_db()
        print("✅ Database initialized with cart tables")
        
        # Clean up test data from previous runs
        cleanup_test_data()
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_create_cart():
    """Test 2: Create cart with session ID"""
    print("\n" + "=" * 60)
    print("Test 2: Create Cart with Session ID")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        cart_repo = CartRepository(db)
        
        # Create cart
        session_id = "test_session_123"
        cart = cart_repo.create_cart(session_id, hours_to_expire=24)
        
        print(f"📦 Cart created: {cart}")
        print(f"   Session ID: {cart.session_id}")
        print(f"   Status: {cart.status}")
        print(f"   Expires at: {cart.expires_at}")
        print(f"   Created at: {cart.created_at}")
        
        assert cart.session_id == session_id
        assert cart.status == "active"
        # SQLite stores naive datetimes, so compare with naive
        assert cart.expires_at > datetime.now()
        
        print("✅ Cart created successfully")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_add_items_to_cart():
    """Test 3: Add Pokemon items to cart"""
    print("\n" + "=" * 60)
    print("Test 3: Add Items to Cart")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        cart_repo = CartRepository(db)
        pokemon_repo = PokemonRepository(db)
        
        # Get or create cart
        session_id = "test_session_456"
        cart = cart_repo.get_or_create_cart(session_id)
        
        # Get some Pokemon
        pikachu = pokemon_repo.get_by_numero(25)  # Pikachu
        charizard = pokemon_repo.get_by_numero(6)  # Charizard
        
        if not pikachu or not charizard:
            print("❌ Pokemon not found in database")
            return False
        
        # Add items
        item1 = cart_repo.add_item(cart, pikachu, quantity=2)
        item2 = cart_repo.add_item(cart, charizard, quantity=1)
        
        print(f"🛒 Added items to cart:")
        print(f"   {item1.quantity}x {item1.pokemon_name} @ ${item1.unit_price} = ${item1.total_price}")
        print(f"   {item2.quantity}x {item2.pokemon_name} @ ${item2.unit_price} = ${item2.total_price}")
        
        # Verify cart
        cart_dict = cart.to_dict()
        print(f"\n📊 Cart summary:")
        print(f"   Total items: {cart_dict['total_items']}")
        print(f"   Total amount: ${cart_dict['total_amount']}")
        
        assert cart_dict['total_items'] == 2
        assert cart_dict['total_amount'] == (pikachu.precio * 2) + charizard.precio
        
        print("✅ Items added successfully")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_session_recovery():
    """Test 4: Recover cart by session ID"""
    print("\n" + "=" * 60)
    print("Test 4: Session Recovery")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        cart_repo = CartRepository(db)
        
        # Get existing cart from previous test
        session_id = "test_session_456"
        cart = cart_repo.get_cart_by_session(session_id)
        
        if not cart:
            print("❌ Cart not found")
            return False
        
        print(f"🔍 Retrieved cart: {cart.session_id}")
        print(f"   Items: {len(cart.items)}")
        print(f"   Total: ${sum(item.total_price for item in cart.items)}")
        
        for item in cart.items:
            print(f"   - {item.quantity}x {item.pokemon_name} @ ${item.unit_price}")
        
        assert len(cart.items) >= 2
        
        print("✅ Session recovered successfully")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_cart_expiration():
    """Test 5: Cart expiration logic"""
    print("\n" + "=" * 60)
    print("Test 5: Cart Expiration")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        cart_repo = CartRepository(db)
        
        # Create cart that expires in 1 hour
        session_id = "test_expired_cart"
        cart = cart_repo.create_cart(session_id, hours_to_expire=1)
        
        # Manually set expiration to past
        cart.expires_at = datetime.now(timezone.utc) - timedelta(hours=2)
        db.commit()
        
        print(f"📅 Cart expires_at: {cart.expires_at}")
        print(f"   Current time: {datetime.now(timezone.utc)}")
        print(f"   Is expired: {cart.is_expired()}")
        
        assert cart.is_expired() == True
        
        # Run expiration cleanup
        expired_count = cart_repo.expire_old_carts(hours=1)
        print(f"\n🗑️  Expired {expired_count} cart(s)")
        
        # Verify cart status changed
        db.refresh(cart)
        print(f"   Cart status after cleanup: {cart.status}")
        
        assert cart.status == "expired"
        
        print("✅ Expiration logic works")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_concurrent_carts():
    """Test 6: Multiple carts for different sessions"""
    print("\n" + "=" * 60)
    print("Test 6: Concurrent Carts")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        cart_repo = CartRepository(db)
        pokemon_repo = PokemonRepository(db)
        
        # Create carts for 3 different users
        sessions = ["user_1", "user_2", "user_3"]
        carts = []
        
        for session_id in sessions:
            cart = cart_repo.get_or_create_cart(session_id)
            
            # Add different Pokemon to each cart
            pokemon = pokemon_repo.get_by_numero(int(session_id.split("_")[1]))
            if pokemon:
                cart_repo.add_item(cart, pokemon, quantity=1)
            
            carts.append(cart)
        
        print(f"🔀 Created {len(carts)} concurrent carts")
        
        # Verify independence
        for cart in carts:
            cart_dict = cart.to_dict()
            print(f"   Cart {cart.session_id}: {cart_dict['total_items']} items, ${cart_dict['total_amount']}")
        
        # Get stats
        stats = cart_repo.get_cart_stats()
        print(f"\n📊 Cart statistics:")
        print(f"   Total carts: {stats['total_carts']}")
        print(f"   Active carts: {stats['active_carts']}")
        print(f"   Abandoned carts: {stats['abandoned_carts']}")
        print(f"   Completed carts: {stats['completed_carts']}")
        
        assert stats['total_carts'] >= 3
        assert stats['active_carts'] >= 3
        
        print("✅ Concurrent carts work independently")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def run_all_tests():
    """Run all cart persistence tests"""
    print("\n" + "🎯" * 30)
    print("CART PERSISTENCE TEST SUITE")
    print("🎯" * 30)
    
    tests = [
        test_initialize_db,
        test_create_cart,
        test_add_items_to_cart,
        test_session_recovery,
        test_cart_expiration,
        test_concurrent_carts,
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

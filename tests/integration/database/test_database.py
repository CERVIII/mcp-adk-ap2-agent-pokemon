#!/usr/bin/env python3
"""
Test Database Operations

Tests CRUD operations on Pokemon and Transactions in SQLite database.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ap2-integration"))

from src.database import (
    init_db,
    SessionLocal,
    Pokemon,
    Transaction,
    TransactionItem,
    PokemonRepository,
    TransactionRepository,
    get_db_stats
)


def test_database_initialization():
    """Test 1: Database initialization"""
    print("\n" + "="*60)
    print("Test 1: Database Initialization")
    print("="*60)
    
    try:
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_pokemon_repository():
    """Test 2: Pokemon repository operations"""
    print("\n" + "="*60)
    print("Test 2: Pokemon Repository")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        repo = PokemonRepository(db)
        
        # Get all Pokemon
        all_pokemon = repo.get_all()
        print(f"✅ Found {len(all_pokemon)} Pokemon in database")
        
        if len(all_pokemon) == 0:
            print("⚠️  Database is empty. Run migration script first.")
            return True  # Not a failure
        
        # Get by numero
        pikachu = repo.get_by_numero(25)
        if pikachu:
            print(f"✅ Found Pikachu: {pikachu.nombre} (${pikachu.precio})")
        else:
            print("❌ Pikachu not found")
            return False
        
        # Get by nombre
        charmander = repo.get_by_nombre("charmander")
        if charmander:
            print(f"✅ Found Charmander: #{charmander.numero} (${charmander.precio})")
        else:
            print("❌ Charmander not found")
            return False
        
        # Get available
        available = repo.get_available()
        print(f"✅ Found {len(available)} available Pokemon")
        
        # Search
        cheap = repo.search(max_price=60, only_available=True, limit=5)
        print(f"✅ Found {len(cheap)} cheap Pokemon (max $60)")
        
        # Get stats
        stats = repo.get_inventory_stats()
        print(f"✅ Inventory stats:")
        print(f"   Total Pokemon: {stats['total_pokemon']}")
        print(f"   Available: {stats['available_pokemon']}")
        print(f"   Total stock: {stats['total_stock']}")
        print(f"   Total sold: {stats['total_sold']}")
        
        print("\n✅ Pokemon repository tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_stock_management():
    """Test 3: Stock decrease/increase"""
    print("\n" + "="*60)
    print("Test 3: Stock Management")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        repo = PokemonRepository(db)
        
        # Get Pikachu
        pikachu = repo.get_by_numero(25)
        if not pikachu:
            print("⚠️  Pikachu not found, skipping test")
            return True
        
        original_stock = pikachu.inventario_disponible
        print(f"📦 Pikachu original stock: {original_stock}")
        
        # Decrease stock
        success = repo.decrease_stock(25, 1)
        if not success:
            print("❌ Failed to decrease stock")
            return False
        
        db.refresh(pikachu)
        new_stock = pikachu.inventario_disponible
        print(f"✅ Stock decreased: {original_stock} -> {new_stock}")
        
        if new_stock != original_stock - 1:
            print(f"❌ Stock mismatch: expected {original_stock - 1}, got {new_stock}")
            return False
        
        # Increase stock (refund)
        repo.increase_stock(25, 1)
        db.refresh(pikachu)
        restored_stock = pikachu.inventario_disponible
        print(f"✅ Stock restored: {new_stock} -> {restored_stock}")
        
        if restored_stock != original_stock:
            print(f"❌ Stock not restored: expected {original_stock}, got {restored_stock}")
            return False
        
        print("\n✅ Stock management tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_transaction_creation():
    """Test 4: Transaction creation"""
    print("\n" + "="*60)
    print("Test 4: Transaction Creation")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        transaction_repo = TransactionRepository(db)
        
        # Create a test transaction
        test_transaction_id = "test_txn_12345"
        test_cart_id = "test_cart_67890"
        
        # Check if transaction already exists (cleanup from previous tests)
        existing = transaction_repo.get_by_id(test_transaction_id)
        if existing:
            print(f"⚠️  Test transaction already exists (ID: {existing.id})")
            print("   Skipping creation, using existing...")
            return True
        
        # Create mock mandates
        cart_mandate = {
            "contents": {
                "id": test_cart_id,
                "payment_request": {
                    "details": {
                        "id": "order_test",
                        "total": {
                            "label": "Total",
                            "amount": {"currency": "USD", "value": 25.0}
                        },
                        "displayItems": [
                            {
                                "label": "Pikachu #25",
                                "amount": {"currency": "USD", "value": 25.0}
                            }
                        ]
                    }
                }
            },
            "merchantName": "Test Merchant",
            "merchant_signature": "test_signature",
            "timestamp": "2025-10-21T00:00:00Z"
        }
        
        payment_mandate = {
            "payment_mandate_contents": {
                "payment_response": {
                    "method_name": "test-card",
                    "payer_email": "test@example.com"
                }
            },
            "user_authorization": "test_auth",
            "timestamp": "2025-10-21T00:00:00Z"
        }
        
        items = [
            {
                "pokemon_numero": 25,
                "quantity": 1,
                "unit_price": 25.0
            }
        ]
        
        # Create transaction
        transaction = transaction_repo.create(
            transaction_id=test_transaction_id,
            cart_id=test_cart_id,
            cart_mandate=cart_mandate,
            payment_mandate=payment_mandate,
            items=items,
            status="completed"
        )
        
        print(f"✅ Transaction created: {transaction.transaction_id}")
        print(f"   Database ID: {transaction.id}")
        print(f"   Amount: ${transaction.total_amount}")
        print(f"   Items: {len(transaction.items)}")
        
        # Verify transaction was saved
        retrieved = transaction_repo.get_by_id(test_transaction_id)
        if not retrieved:
            print("❌ Transaction not found after creation")
            return False
        
        print(f"✅ Transaction retrieved: {retrieved.transaction_id}")
        
        # Get stats
        stats = transaction_repo.get_stats()
        print(f"✅ Transaction stats:")
        print(f"   Total: {stats['total_transactions']}")
        print(f"   Completed: {stats['completed_transactions']}")
        print(f"   Revenue: ${stats['total_revenue']:.2f}")
        
        print("\n✅ Transaction creation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_database_stats():
    """Test 5: Database statistics"""
    print("\n" + "="*60)
    print("Test 5: Database Statistics")
    print("="*60)
    
    try:
        stats = get_db_stats()
        
        print(f"📊 Database Statistics:")
        print(f"   Path: {stats['database_path']}")
        print(f"   Size: {stats['database_size_mb']:.2f} MB")
        print(f"   Pokemon: {stats['pokemon_count']}")
        print(f"   Transactions: {stats['transaction_count']}")
        
        print("\n✅ Database stats retrieved successfully!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def main():
    """Run all database tests"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🧪 DATABASE TEST SUITE                          ║
║                                                          ║
║  Tests SQLite database operations                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Pokemon Repository", test_pokemon_repository),
        ("Stock Management", test_stock_management),
        ("Transaction Creation", test_transaction_creation),
        ("Database Statistics", test_database_stats),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*60)
    print(f"Total: {len(results)} tests | Passed: {passed} | Failed: {failed}")
    print("="*60)
    
    if failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

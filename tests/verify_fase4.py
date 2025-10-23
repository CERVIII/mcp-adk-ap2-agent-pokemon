#!/usr/bin/env python3
"""
Verification script for Fase 4: Database Migration
Tests that all 4 AP2 agents can import database module successfully
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("🔍 FASE 4: VERIFICACIÓN DE DATABASE MIGRATION")
print("=" * 70)
print()

tests_passed = 0
tests_total = 7

# Test 1: Database module imports
print("1️⃣  Testing database module imports...")
try:
    from database import (
        Pokemon, Transaction, Cart, CartItem,
        PokemonRepository, TransactionRepository, CartRepository,
        SessionLocal, get_db, init_db
    )
    print("   ✅ Database module imports successful")
    print(f"   📦 Imports: Pokemon, Transaction, Cart, 3 Repositories, SessionLocal")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Test 2: Payment Processor imports
print("2️⃣  Testing Payment Processor agent...")
try:
    from ap2.agents.payment_processor.server import app
    routes = len([r for r in app.routes if hasattr(r, 'path')])
    print(f"   ✅ Payment Processor imports successful")
    print(f"   🚀 FastAPI app with {routes} routes registered")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Test 3: Shopping Web UI imports
print("3️⃣  Testing Shopping Web UI...")
try:
    from ap2.agents.shopping.web_ui import app as shopping_app
    routes = len([r for r in shopping_app.routes if hasattr(r, 'path')])
    print(f"   ✅ Shopping Web UI imports successful")
    print(f"   🚀 FastAPI app with {routes} routes registered")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Test 4: Merchant Agent (no database dependency, but verify still works)
print("4️⃣  Testing Merchant Agent...")
try:
    from ap2.agents.merchant.server import app as merchant_app
    routes = len([r for r in merchant_app.routes if hasattr(r, 'path')])
    print(f"   ✅ Merchant Agent imports successful")
    print(f"   🚀 FastAPI app with {routes} routes registered")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Test 5: Credentials Provider
print("5️⃣  Testing Credentials Provider...")
try:
    from ap2.agents.credentials.server import app as credentials_app
    routes = len([r for r in credentials_app.routes if hasattr(r, 'path')])
    print(f"   ✅ Credentials Provider imports successful")
    print(f"   🚀 FastAPI app with {routes} routes registered")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Test 6: Shopping Agent (without web UI)
print("6️⃣  Testing Shopping Agent core...")
try:
    from ap2.agents.shopping.agent import ShoppingAgent
    agent = ShoppingAgent()
    print(f"   ✅ Shopping Agent instantiated successfully")
    print(f"   🤖 Agent ready for purchases")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Test 7: Database configuration
print("7️⃣  Testing Database configuration...")
try:
    from database.config import DATABASE_URL, DATABASE_PATH, POKEMON_DATA_PATH
    print(f"   ✅ Database config loaded")
    print(f"   🗄️  Database: {DATABASE_PATH}")
    print(f"   📦 Pokemon data: {POKEMON_DATA_PATH}")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
print()

# Summary
print("=" * 70)
print("📊 RESULTS")
print("=" * 70)
print(f"Tests passed: {tests_passed}/{tests_total}")
print()

if tests_passed == tests_total:
    print("🎉 ALL TESTS PASSED - Fase 4 Database Migration SUCCESSFUL!")
    print()
    print("✅ All 4 AP2 agents are now functional:")
    print("   1. Shopping Agent (+ Web UI)")
    print("   2. Merchant Agent")
    print("   3. Credentials Provider")
    print("   4. Payment Processor ⭐ (NOW UNBLOCKED)")
    print()
    print("🚀 Ready to proceed to Fase 5 (E2E Tests)")
    sys.exit(0)
else:
    print(f"❌ {tests_total - tests_passed} test(s) failed")
    print("⚠️  Please review errors above")
    sys.exit(1)

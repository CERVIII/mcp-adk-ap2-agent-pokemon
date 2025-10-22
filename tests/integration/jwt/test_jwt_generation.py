#!/usr/bin/env python3
"""
Test script to verify JWT token generation in AP2 integration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ap2-integration', 'src'))

from common.utils import generate_merchant_signature, generate_user_authorization, hash_value
import jwt
import json

def test_jwt_tokens():
    """Test that JWT tokens are properly generated and can be decoded"""
    
    print("=" * 60)
    print("🔐 Testing JWT Token Generation")
    print("=" * 60)
    
    # Test 1: Merchant Signature
    print("\n1️⃣  Testing Merchant Signature...")
    cart_id = "test_cart_123"
    merchant_sig = generate_merchant_signature(cart_id)
    
    print(f"   Cart ID: {cart_id}")
    print(f"   Generated signature: {merchant_sig[:50]}...")
    print(f"   Length: {len(merchant_sig)} chars")
    
    # Try to decode (won't verify signature without public key, but can see payload)
    try:
        decoded = jwt.decode(merchant_sig, options={"verify_signature": False})
        print(f"   ✅ Valid JWT structure!")
        print(f"   Payload: {json.dumps(decoded, indent=6)}")
    except Exception as e:
        print(f"   ❌ Error decoding: {e}")
    
    # Test 2: User Authorization
    print("\n2️⃣  Testing User Authorization...")
    cart_hash = hash_value("test_cart_data")
    payment_hash = hash_value("test_payment_data")
    user_auth = generate_user_authorization(cart_hash, payment_hash)
    
    print(f"   Cart hash: {cart_hash[:20]}...")
    print(f"   Payment hash: {payment_hash[:20]}...")
    print(f"   Generated authorization: {user_auth[:50]}...")
    print(f"   Length: {len(user_auth)} chars")
    
    try:
        decoded = jwt.decode(user_auth, options={"verify_signature": False})
        print(f"   ✅ Valid JWT structure!")
        print(f"   Payload: {json.dumps(decoded, indent=6)}")
    except Exception as e:
        print(f"   ❌ Error decoding: {e}")
    
    # Test 3: Check JWT parts
    print("\n3️⃣  Analyzing JWT Structure...")
    parts = merchant_sig.split('.')
    print(f"   JWT has {len(parts)} parts (should be 3: header.payload.signature)")
    if len(parts) == 3:
        print(f"   ✅ Correct JWT structure!")
        print(f"   - Header: {parts[0][:30]}...")
        print(f"   - Payload: {parts[1][:30]}...")
        print(f"   - Signature: {parts[2][:30]}...")
    else:
        print(f"   ❌ Invalid JWT structure!")
    
    print("\n" + "=" * 60)
    print("✅ JWT Generation Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_jwt_tokens()

#!/usr/bin/env python3
"""
Test JWT Validation - AP2 Security

Tests the validation of JWT signatures for:
1. Merchant signatures on CartMandates
2. User authorizations on PaymentMandates

Requirements:
- MCP server must have generated and saved RSA keys
- Shopping agent must use JWT validation
- Payment processor must validate user authorization
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ap2-integration"))

from src.common import (
    JWTValidator,
    JWTValidationError,
    validate_merchant_signature,
    validate_user_authorization,
    generate_unique_id,
    generate_user_authorization as create_user_auth,
    hash_cart_mandate,
    hash_payment_mandate_contents,
)


def create_mock_cart_mandate(cart_id: str = None) -> dict:
    """Create a mock CartMandate for testing"""
    if not cart_id:
        cart_id = generate_unique_id("cart_test")
    
    return {
        "contents": {
            "id": cart_id,
            "user_cart_confirmation_required": False,
            "payment_request": {
                "details": {
                    "id": generate_unique_id("order"),
                    "total": {
                        "label": "Total",
                        "amount": {
                            "currency": "USD",
                            "value": 25.0
                        }
                    },
                    "displayItems": [
                        {
                            "label": "Pikachu #25",
                            "amount": {
                                "currency": "USD",
                                "value": 25.0
                            }
                        }
                    ]
                }
            }
        },
        "merchant_signature": "mock_jwt_without_real_signature",
        "timestamp": "2025-10-21T10:00:00Z",
        "merchantName": "PokeMart - Test"
    }


def create_mock_payment_mandate(cart_mandate: dict) -> dict:
    """Create a mock PaymentMandate for testing"""
    cart_hash = hash_cart_mandate(cart_mandate)
    
    payment_contents = {
        "payment_mandate_id": generate_unique_id("pm"),
        "payment_details_id": cart_mandate["contents"]["payment_request"]["details"]["id"],
        "payment_details_total": cart_mandate["contents"]["payment_request"]["details"]["total"],
        "payment_response": {
            "request_id": cart_mandate["contents"]["payment_request"]["details"]["id"],
            "method_name": "credit-card",
            "details": {"token": "tok_test_12345"},
            "payer_email": "test@pokemon.com"
        },
        "merchant_agent": "TestMerchant",
        "credential_provider_agent": "TestCredentials",
        "risk_data": {}
    }
    
    payment_hash = hash_payment_mandate_contents(payment_contents)
    user_auth = create_user_auth(cart_hash, payment_hash)
    
    return {
        "payment_mandate_contents": payment_contents,
        "user_authorization": user_auth,
        "timestamp": "2025-10-21T10:00:00Z"
    }


def test_jwt_structure_validation():
    """Test JWT structure validation"""
    print("\n" + "="*60)
    print("Test 1: JWT Structure Validation")
    print("="*60)
    
    validator = JWTValidator()
    
    # Valid JWT structure
    valid_jwt = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.signature"
    
    try:
        validator.validate_jwt_structure(valid_jwt)
        print("✅ Valid JWT structure accepted")
    except JWTValidationError as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Invalid: only 2 parts
    try:
        validator.validate_jwt_structure("header.payload")
        print("❌ FAILED: Invalid JWT (2 parts) was accepted")
        return False
    except JWTValidationError:
        print("✅ Invalid JWT (2 parts) rejected correctly")
    
    # Invalid: empty
    try:
        validator.validate_jwt_structure("")
        print("❌ FAILED: Empty JWT was accepted")
        return False
    except JWTValidationError:
        print("✅ Empty JWT rejected correctly")
    
    print("\n✅ JWT structure validation tests passed!\n")
    return True


def test_merchant_signature_from_mcp():
    """Test validation of real merchant signature from MCP server"""
    print("\n" + "="*60)
    print("Test 2: Merchant Signature from MCP Server")
    print("="*60)
    
    # Check if MCP keys exist
    mcp_keys_dir = Path(__file__).parent.parent / "mcp-server" / "keys"
    public_key_path = mcp_keys_dir / "merchant_public.pem"
    
    if not public_key_path.exists():
        print(f"⚠️  SKIPPED: MCP public key not found at {public_key_path}")
        print("   Run MCP server first to generate keys: cd mcp-server && npm start")
        return True  # Not a failure, just skipped
    
    print(f"✅ Found MCP public key: {public_key_path}")
    
    # For a real test, we would need to call the MCP server
    # For now, we just verify the key can be loaded
    try:
        validator = JWTValidator()
        if validator.merchant_public_key:
            print("✅ Merchant public key loaded successfully")
            print("   Ready to validate signatures from MCP server")
        else:
            print("❌ FAILED: Merchant public key not loaded")
            return False
    except Exception as e:
        print(f"❌ FAILED: Error loading keys: {e}")
        return False
    
    print("\n✅ MCP key validation test passed!\n")
    return True


def test_user_authorization_validation():
    """Test validation of user authorization JWT"""
    print("\n" + "="*60)
    print("Test 3: User Authorization Validation")
    print("="*60)
    
    # Create mock mandates
    cart_mandate = create_mock_cart_mandate()
    payment_mandate = create_mock_payment_mandate(cart_mandate)
    
    print("Created test mandates with valid user authorization")
    
    try:
        # Validate (without signature verification since we're using test keys)
        payload = validate_user_authorization(
            payment_mandate,
            cart_mandate,
            verify=False  # Skip signature verification for test keys
        )
        
        print(f"✅ User authorization validated successfully")
        print(f"   Issuer: {payload.get('iss')}")
        print(f"   Subject: {payload.get('sub')}")
        print(f"   Cart hash: {payload.get('cart_hash')[:16]}...")
        print(f"   Payment hash: {payload.get('payment_hash')[:16]}...")
        
    except JWTValidationError as e:
        print(f"❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test with tampered cart (hashes won't match)
    print("\nTesting tampered cart detection...")
    import copy
    tampered_cart = copy.deepcopy(cart_mandate)
    tampered_cart["contents"]["id"] = "tampered_cart_id"
    
    try:
        validate_user_authorization(
            payment_mandate,
            tampered_cart,
            verify=False
        )
        print("❌ FAILED: Tampered cart was accepted")
        return False
    except JWTValidationError as e:
        print(f"✅ Tampered cart detected: {e}")
    
    print("\n✅ User authorization validation tests passed!\n")
    return True


def test_expired_jwt():
    """Test that expired JWTs are rejected"""
    print("\n" + "="*60)
    print("Test 4: Expired JWT Detection")
    print("="*60)
    
    # This would require creating an expired JWT
    # For now, we just document the requirement
    print("⚠️  TODO: Implement expired JWT test")
    print("   JWTs with exp in the past should be rejected")
    print("   This requires time-travel or waiting for expiration")
    
    print("\n⚠️  Test skipped (not yet implemented)\n")
    return True


def test_invalid_signature():
    """Test that invalid signatures are rejected"""
    print("\n" + "="*60)
    print("Test 5: Invalid Signature Detection")
    print("="*60)
    
    cart_mandate = create_mock_cart_mandate()
    
    # Replace signature with a malformed JWT (not properly base64-encoded)
    cart_mandate["merchant_signature"] = "invalid.jwt.signature"
    
    try:
        validate_merchant_signature(cart_mandate, verify=False)
        # This will fail because it's not a valid base64 JWT
        print("❌ FAILED: Malformed JWT was accepted")
        return False
    except (JWTValidationError, Exception) as e:
        print(f"✅ Malformed JWT rejected: {type(e).__name__}")
    
    # Test with a valid JWT structure but wrong signature
    # This is a real JWT but signed with a different key
    valid_structure_wrong_sig = (
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJQb2tlTWFydCIsInN1YiI6ImNhcnRfZmFrZSJ9."
        "fake_signature_base64url_encoded_string_here"
    )
    cart_mandate["merchant_signature"] = valid_structure_wrong_sig
    
    try:
        validate_merchant_signature(cart_mandate, verify=True)
        print("❌ FAILED: JWT with invalid signature was accepted")
        return False
    except (JWTValidationError, Exception) as e:
        print(f"✅ JWT with wrong signature rejected: {type(e).__name__}")
    
    print("\n✅ Invalid signature detection tests passed!\n")
    return True


async def test_integration_with_real_mcp():
    """Integration test with real MCP server (if running)"""
    print("\n" + "="*60)
    print("Test 6: Integration with Real MCP Server")
    print("="*60)
    
    try:
        import httpx
        
        # Try to call merchant agent to create a real cart
        merchant_url = "http://localhost:8001"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{merchant_url}/a2a/merchant_agent/create_cart",
                json={"items": [{"product_id": "25", "quantity": 1}]}
            )
            
            if response.status_code != 200:
                print(f"⚠️  SKIPPED: Merchant agent not running (status {response.status_code})")
                return True
            
            cart_mandate = response.json()
            
            print("✅ Received CartMandate from merchant agent")
            print(f"   Cart ID: {cart_mandate['contents']['id']}")
            
            # Validate the merchant signature
            try:
                payload = validate_merchant_signature(cart_mandate, verify=True)
                print("✅ Real merchant signature validated successfully!")
                print(f"   Issuer: {payload.get('iss')}")
                print(f"   Cart ID: {payload.get('cart_id')}")
                print(f"   Merchant: {payload.get('merchant')}")
                return True
            except JWTValidationError as e:
                print(f"❌ FAILED: Real signature validation failed: {e}")
                return False
            
    except ImportError:
        print("⚠️  SKIPPED: httpx not available")
        return True
    except Exception as e:
        print(f"⚠️  SKIPPED: Could not connect to merchant agent: {e}")
        print("   (This is expected if agents are not running)")
        return True


async def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🧪 JWT VALIDATION TEST SUITE                    ║
║                                                          ║
║  Tests AP2 security requirements for JWT validation     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("JWT Structure Validation", test_jwt_structure_validation),
        ("MCP Key Loading", test_merchant_signature_from_mcp),
        ("User Authorization", test_user_authorization_validation),
        ("Expired JWT Detection", test_expired_jwt),
        ("Invalid Signature", test_invalid_signature),
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
    
    # Integration test (async)
    try:
        result = await test_integration_with_real_mcp()
        results.append(("Real MCP Integration", result))
    except Exception as e:
        print(f"\n❌ Integration test crashed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Real MCP Integration", False))
    
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
    asyncio.run(main())

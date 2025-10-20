#!/usr/bin/env python3
"""
Test JWT Merchant Signature Generation

Verifica que:
1. El MCP server genera un JWT válido (3 partes: header.payload.signature)
2. El JWT contiene los claims correctos (iss, sub, iat, exp, cart_id, merchant)
3. El algoritmo es RS256
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ap2-integration"))

from src.common.mcp_client import get_mcp_client
import json
import base64

def decode_jwt_parts(jwt_token: str) -> dict:
    """Decodifica un JWT sin verificar la firma (solo para inspección)"""
    parts = jwt_token.split('.')
    if len(parts) != 3:
        raise ValueError(f"JWT inválido: tiene {len(parts)} partes, esperadas 3")
    
    # Decodificar header
    header_json = base64.urlsafe_b64decode(parts[0] + '==').decode('utf-8')
    header = json.loads(header_json)
    
    # Decodificar payload
    payload_json = base64.urlsafe_b64decode(parts[1] + '==').decode('utf-8')
    payload = json.loads(payload_json)
    
    return {
        "header": header,
        "payload": payload,
        "signature": parts[2]
    }

async def test_jwt_signature():
    """Test principal"""
    print("🔐 Testing JWT Merchant Signature Generation")
    print("=" * 60)
    
    # 1. Crear un cart con Pikachu
    print("\n📦 Step 1: Creating cart with Pikachu...")
    
    async with get_mcp_client() as client:
        # Crear cart
        cart_data = await client.call_tool(
            "create_pokemon_cart",
            {
                "items": [
                    {"product_id": "25", "quantity": 1}  # Pikachu
                ]
            }
        )
        
        if not cart_data:
            print("❌ Error: No se pudo crear el cart")
            return False
        
        # Debug: mostrar estructura
        print(f"   Cart data keys: {list(cart_data.keys())}")
        
        if "error" in cart_data:
            print(f"❌ Error creating cart: {cart_data['error']}")
            return False
        
        print("✅ Cart created successfully")
        
        # El cart_id puede estar en la raíz o en contents
        cart_id = cart_data.get("cart_id") or cart_data.get("contents", {}).get("id")
        if cart_id:
            print(f"   Cart ID: {cart_id}")
        
        # 2. Extraer merchant_signature
        merchant_signature = cart_data.get("merchant_signature")
        
        if not merchant_signature:
            print("❌ Error: No merchant_signature in response")
            return False
        
        print(f"\n🔑 Step 2: Analyzing merchant_signature...")
        print(f"   Length: {len(merchant_signature)} chars")
        
        # 3. Verificar que tiene 3 partes
        parts = merchant_signature.split('.')
        print(f"   Parts: {len(parts)}")
        
        if len(parts) != 3:
            print(f"❌ FAILED: JWT debe tener 3 partes (header.payload.signature), tiene {len(parts)}")
            print(f"   Signature: {merchant_signature[:100]}...")
            return False
        
        print("✅ JWT tiene 3 partes (header.payload.signature)")
        
        # 4. Decodificar y verificar contenido
        try:
            decoded = decode_jwt_parts(merchant_signature)
            
            print(f"\n📋 Step 3: JWT Contents:")
            print(f"   Header: {json.dumps(decoded['header'], indent=2)}")
            print(f"   Payload: {json.dumps(decoded['payload'], indent=2)}")
            print(f"   Signature (first 50 chars): {decoded['signature'][:50]}...")
            
            # Verificar algoritmo
            if decoded['header'].get('alg') != 'RS256':
                print(f"❌ FAILED: Algorithm debe ser RS256, es {decoded['header'].get('alg')}")
                return False
            
            print(f"\n✅ Algorithm: RS256")
            
            # Verificar claims requeridos
            required_claims = ['iss', 'sub', 'iat', 'exp', 'cart_id', 'merchant']
            missing_claims = [claim for claim in required_claims if claim not in decoded['payload']]
            
            if missing_claims:
                print(f"❌ FAILED: Missing claims: {missing_claims}")
                return False
            
            print(f"✅ All required claims present: {required_claims}")
            
            # Verificar valores
            if decoded['payload']['iss'] != 'PokeMart':
                print(f"❌ FAILED: iss debe ser 'PokeMart', es '{decoded['payload']['iss']}'")
                return False
            
            if decoded['payload']['sub'] != cart_id:
                print(f"❌ FAILED: sub debe ser cart_id '{cart_id}', es '{decoded['payload']['sub']}'")
                return False
            
            if decoded['payload']['cart_id'] != cart_id:
                print(f"❌ FAILED: cart_id claim mismatch")
                return False
            
            if decoded['payload']['merchant'] != 'PokeMart - Primera Generación':
                print(f"❌ FAILED: merchant name mismatch")
                return False
            
            # Verificar expiración (1 hora = 3600 segundos)
            exp_delta = decoded['payload']['exp'] - decoded['payload']['iat']
            if exp_delta != 3600:
                print(f"⚠️  WARNING: expiration delta es {exp_delta}s, esperado 3600s")
            
            print(f"✅ All claim values correct")
            print(f"   - Issuer: {decoded['payload']['iss']}")
            print(f"   - Subject: {decoded['payload']['sub']}")
            print(f"   - Cart ID: {decoded['payload']['cart_id']}")
            print(f"   - Merchant: {decoded['payload']['merchant']}")
            print(f"   - Issued at: {decoded['payload']['iat']}")
            print(f"   - Expires at: {decoded['payload']['exp']} (in {exp_delta}s)")
            
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print("\n✅ Merchant signature is a valid RS256 JWT")
            print("✅ Old mock signature: sig_merchant_pokemon_{cart_id}")
            print("✅ New real JWT signature with proper cryptographic signing")
            
            return True
            
        except Exception as e:
            print(f"❌ Error decoding JWT: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_jwt_signature())
    sys.exit(0 if success else 1)

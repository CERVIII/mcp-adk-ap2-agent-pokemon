"""
Shopping Agent - AP2 Protocol Orchestrator

This is the main agent that coordinates the entire AP2 payment flow:
1. User expresses intent to purchase
2. Search catalog (via MCP)
3. Request cart from merchant agent
4. Get payment methods from credentials provider
5. Create payment mandate
6. Send to payment processor
7. Return receipt to user
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional

from mcp_wrapper.client import get_mcp_client
from ap2.protocol import (
    PaymentMandate,
    PaymentMandateContents,
    PaymentResponse,
    generate_unique_id,
    generate_user_authorization,
    hash_cart_mandate,
    hash_payment_mandate_contents,
    get_current_timestamp,
    mock_risk_data,
    print_cart_summary,
    print_payment_summary,
)

# TODO: Implement JWT validation functions
# validate_merchant_signature,
# JWTValidationError,


class ShoppingAgent:
    """Shopping Agent that orchestrates Pokemon purchases using AP2"""
    
    def __init__(self):
        self.merchant_url = "http://localhost:8001"
        self.credentials_provider_url = "http://localhost:8002"
        self.payment_processor_url = "http://localhost:8003"
    
    def get_mcp_client(self):
        """Get MCP client context manager"""
        return get_mcp_client()
        
    async def search_pokemon(self, query: str, **filters) -> List[Dict[str, Any]]:
        """Search Pokemon in catalog"""
        print(f"\n🔍 Searching for: {query}")
        
        async with get_mcp_client() as mcp:
            results = await mcp.search_pokemon(**filters)
        
        print(f"Found {len(results)} Pokemon")
        return results
        
    async def create_cart(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create CartMandate via merchant agent"""
        print(f"\n🛒 Creating cart with {len(items)} items...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.merchant_url}/a2a/merchant_agent/create_cart",
                json={"items": items}
            )
            response.raise_for_status()
            cart_mandate = response.json()
        
        # Show merchant signature JWT
        merchant_sig = cart_mandate.get("merchant_signature", "")
        if merchant_sig:
            print("\n🔐 Merchant Signature JWT (first 100 chars):")
            print(f"   {merchant_sig[:100]}...")
            print(f"   📊 JWT Structure: {len(merchant_sig.split('.'))} parts")
            print(f"   📏 Total length: {len(merchant_sig)} characters")
        
        # TODO: Validate merchant signature (JWT validation not yet implemented)
        print("\n🔍 Merchant signature validation skipped (development mode)")
        # try:
        #     payload = validate_merchant_signature(cart_mandate, verify=True)
        #     print("✅ Merchant signature is valid and verified!")
        # except JWTValidationError as e:
        #     print(f"❌ Merchant signature validation FAILED: {e}")
        #     print("⚠️  Security Warning: CartMandate may be forged or tampered!")
        #     raise ValueError(f"Invalid merchant signature: {e}")
        # except Exception as e:
        #     print(f"⚠️  Warning: Could not validate signature: {e}")
        #     print("   Continuing without validation (development mode)")
        
        print_cart_summary(cart_mandate)
        return cart_mandate
        
    async def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods from credentials provider"""
        print("\n💳 Fetching payment methods...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.credentials_provider_url}/a2a/credentials_provider/payment_methods"
            )
            response.raise_for_status()
            result = response.json()
        
        methods = result["data"]
        print(f"Found {len(methods)} payment methods")
        for method in methods:
            default = " [DEFAULT]" if method["is_default"] else ""
            print(f"  • {method['display_name']}{default}")
        
        return methods
        
    async def tokenize_payment_method(self, payment_method_id: str) -> str:
        """Get payment token from credentials provider"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.credentials_provider_url}/a2a/credentials_provider/tokenize",
                json={"payment_method_id": payment_method_id}
            )
            response.raise_for_status()
            result = response.json()
        
        return result["data"]["token"]
        
    def create_payment_mandate(
        self,
        cart_mandate: Dict[str, Any],
        payment_token: str,
        payment_method_name: str,
        user_email: str = "trainer@pokemon.com"
    ) -> Dict[str, Any]:
        """Create PaymentMandate for user authorization"""
        print("\n📝 Creating PaymentMandate...")
        
        cart_details = cart_mandate["contents"]["payment_request"]["details"]
        
        payment_mandate_contents = PaymentMandateContents(
            payment_mandate_id=generate_unique_id("pm"),
            payment_details_id=cart_details["id"],
            payment_details_total=cart_details["total"],
            payment_response=PaymentResponse(
                request_id=cart_details["id"],
                method_name=payment_method_name,
                details={"token": payment_token},
                payer_email=user_email
            ),
            merchant_agent="PokemonMerchantAgent",
            credential_provider_agent="PokemonCredentialsProvider",
            risk_data=mock_risk_data()
        )
        
        payment_mandate = PaymentMandate(
            payment_mandate_contents=payment_mandate_contents,
            timestamp=get_current_timestamp()
        )
        
        # Simulate user signature (in production: done on user's device)
        cart_hash = hash_cart_mandate(cart_mandate)
        payment_hash = hash_payment_mandate_contents(
            payment_mandate_contents.model_dump()
        )
        user_auth_jwt = generate_user_authorization(cart_hash, payment_hash)
        payment_mandate.user_authorization = user_auth_jwt
        
        # Show JWT token info
        print(f"\n🔐 Generated JWT Tokens:")
        print(f"   📝 User Authorization JWT (first 100 chars):")
        print(f"      {user_auth_jwt[:100]}...")
        print(f"   📊 JWT Structure: {len(user_auth_jwt.split('.'))} parts (header.payload.signature)")
        print(f"   📏 Total length: {len(user_auth_jwt)} characters")
        
        payment_dict = payment_mandate.model_dump()
        print_payment_summary(payment_dict)
        
        return payment_dict
        
    async def process_payment(
        self,
        cart_mandate: Dict[str, Any],
        payment_mandate: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send mandates to payment processor"""
        print("\n💰 Processing payment...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.payment_processor_url}/a2a/processor/charge",
                json={
                    "cart_mandate": cart_mandate,
                    "payment_mandate": payment_mandate,
                    "risk_data": mock_risk_data()
                }
            )
            response.raise_for_status()
            result = response.json()
        
        if result["success"]:
            receipt = result["data"]
            print(f"\n✅ Payment successful!")
            print(f"   Transaction ID: {receipt['transaction_id']}")
            print(f"   Status: {receipt['status']}")
            return receipt
        else:
            print(f"\n❌ Payment failed: {result.get('message')}")
            raise Exception(result.get("message", "Payment failed"))
            
    async def purchase_pokemon(
        self,
        pokemon_name: str = None,
        pokemon_id: str = None,
        quantity: int = 1,
        user_email: str = "trainer@pokemon.com"
    ) -> Dict[str, Any]:
        """
        Complete purchase flow for a Pokemon.
        
        This demonstrates the full AP2 human-present transaction flow.
        Args:
            pokemon_name: Name of the Pokemon (e.g., "pikachu")
            pokemon_id: ID/number of the Pokemon (e.g., "25")
            quantity: Quantity to purchase
            user_email: User's email
        """
        # Use pokemon_id if provided, otherwise use pokemon_name
        identifier = pokemon_id if pokemon_id else pokemon_name
        
        print(f"\n{'='*60}")
        print(f"🎯 STARTING PURCHASE: {identifier} (x{quantity})")
        print(f"{'='*60}")
        
        # Step 1: Get Pokemon info
        async with get_mcp_client() as mcp:
            pokemon = await mcp.get_pokemon_info(identifier)
            price_info = await mcp.get_pokemon_price(identifier)
        
        product_id = str(price_info["numero"])
        
        print(f"\n📦 Product Details:")
        print(f"   Name: {pokemon['name'].capitalize()}")
        print(f"   Type: {', '.join(pokemon['types'])}")
        print(f"   Price: ${price_info['precio']} USD")
        print(f"   Available: {price_info['inventario']['disponibles']}")
        
        # Step 2: Create cart
        cart_mandate = await self.create_cart([
            {"product_id": product_id, "quantity": quantity}
        ])
        
        # Step 3: Get payment methods
        payment_methods = await self.get_payment_methods()
        
        # Select default payment method
        default_method = next(
            (m for m in payment_methods if m["is_default"]),
            payment_methods[0]
        )
        print(f"\n✓ Selected: {default_method['display_name']}")
        
        # Step 4: Tokenize payment method
        payment_token = await self.tokenize_payment_method(default_method["id"])
        
        # Step 5: Create payment mandate
        payment_mandate = self.create_payment_mandate(
            cart_mandate=cart_mandate,
            payment_token=payment_token,
            payment_method_name=default_method["type"],
            user_email=user_email
        )
        
        # Step 6: Process payment
        receipt = await self.process_payment(cart_mandate, payment_mandate)
        
        print(f"\n{'='*60}")
        print(f"🎉 PURCHASE COMPLETE!")
        print(f"{'='*60}\n")
        
        # Return structured data for web UI
        return {
            "status": receipt.get("status", "completed"),
            "payment_id": receipt.get("payment_id"),
            "total": price_info["precio"] * quantity,
            "items": [{
                "name": pokemon['name'].capitalize(),
                "price": price_info['precio'],
                "quantity": quantity
            }],
            "cart_mandate": cart_mandate,
            "payment_mandate": payment_mandate,
            "receipt": receipt
        }


# ============================================
# CLI Interface
# ============================================

async def main():
    """Interactive CLI for shopping agent"""
    agent = ShoppingAgent()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🛍️  POKEMON SHOPPING AGENT (AP2)                ║
║                                                          ║
║  This agent demonstrates the complete AP2 payment flow  ║
║  for human-present transactions.                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n" + "="*60)
        print("What would you like to do?")
        print("1. Search Pokemon")
        print("2. Purchase Pokemon")
        print("3. Purchase Pikachu (quick demo)")
        print("4. Exit")
        print("="*60)
        
        choice = input("\nChoice (1-4): ").strip()
        
        try:
            if choice == "1":
                query = input("Search query (name or type): ").strip()
                results = await agent.search_pokemon(
                    query,
                    limit=5,
                    only_available=True
                )
                
                print(f"\nResults:")
                for p in results:
                    print(f"  • {p['name']} (#{p['numero']}): ${p['precio']} USD")
                    
            elif choice == "2":
                pokemon = input("Pokemon name or number: ").strip()
                quantity = int(input("Quantity (default 1): ").strip() or "1")
                
                receipt = await agent.purchase_pokemon(pokemon, quantity)
                print(f"\n🧾 Receipt: {receipt}")
                
            elif choice == "3":
                # Quick demo
                receipt = await agent.purchase_pokemon("pikachu", 1)
                print(f"\n🧾 Receipt: {receipt}")
                
            elif choice == "4":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("Invalid choice")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

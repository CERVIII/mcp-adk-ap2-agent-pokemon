"""
Shopping Agent - User's personal shopping assistant
Uses Google Generative AI (Gemini) directly with AP2 protocol support
"""

import os
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

from src.common.ap2_types import (
    CartMandate,
    PaymentMandate,
    PaymentMethod,
    IntentMandate
)

# Load environment
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class ShoppingAssistant:
    """Shopping Assistant with AP2 support"""
    
    def __init__(self, merchant_url: str = "http://localhost:8001"):
        self.merchant_url = merchant_url
        self.current_cart: CartMandate | None = None
        self.conversation_history = []
        
        # Create Gemini model with function calling
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            tools=[
                self.search_pokemon,
                self.create_shopping_cart,
                self.list_payment_methods,
                self.checkout
            ],
            system_instruction="""You are a helpful Pokemon shopping assistant. 
You help users search for Pokemon, create shopping carts, and complete purchases 
using the AP2 (Agent Payments Protocol).

When users ask about Pokemon:
- Use search_pokemon to find Pokemon
- Show prices and availability clearly
- Be enthusiastic about Pokemon!

When users want to buy:
- Use create_shopping_cart to add items
- Confirm the cart contents
- Use checkout to complete the purchase

Always be helpful, friendly, and explain the AP2 protocol when processing payments."""
        )
        self.chat = self.model.start_chat(history=[])
        
    def search_pokemon(
        self,
        query: str,
        max_price: float | None = None,
        only_available: bool = False
    ) -> str:
        """
        Search for Pokemon in the merchant catalog
        
        Args:
            query: Pokemon name or search term
            max_price: Maximum price filter (optional)
            only_available: Only show available Pokemon (default: False)
            
        Returns:
            JSON string with search results
        """
        try:
            response = requests.post(
                f"{self.merchant_url}/catalog/search",
                json={
                    "query": query,
                    "max_price": max_price,
                    "only_available": only_available,
                    "limit": 10
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return json.dumps({
                        "success": False,
                        "message": f"No Pokemon found matching '{query}'"
                    })
                
                # Format results
                pokemon_list = []
                for p in results:
                    pokemon_list.append({
                        "name": p['nombre'].capitalize(),
                        "number": p['numero'],
                        "price": p['precio'],
                        "available": p.get('enVenta', False),
                        "stock": p['inventario']['disponibles']
                    })
                
                return json.dumps({
                    "success": True,
                    "count": len(pokemon_list),
                    "pokemon": pokemon_list
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Error {response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    def create_shopping_cart(self, items: list[dict]) -> str:
        """
        Create a shopping cart with Pokemon
        
        Args:
            items: List of items like [{"pokemon": "pikachu", "quantity": 1}]
            
        Returns:
            JSON string with cart details or error
        """
        try:
            # Format items for the merchant API
            cart_items = []
            for item in items:
                pokemon_name = item.get("pokemon", "").lower()
                quantity = item.get("quantity", 1)
                cart_items.append({
                    "pokemon": pokemon_name,
                    "quantity": quantity
                })
            
            response = requests.post(
                f"{self.merchant_url}/cart/create",
                json={"items": cart_items},
                timeout=5
            )
            
            if response.status_code == 200:
                cart_data = response.json()
                self.current_cart = CartMandate(**cart_data)
                
                return json.dumps({
                    "success": True,
                    "message": "Cart created successfully!",
                    "cart_id": cart_data["mandate_id"],
                    "items": cart_data["items"],
                    "total": cart_data["total_amount"],
                    "currency": cart_data["currency"]
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": response.json().get("detail", "Unknown error")
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    def list_payment_methods(self) -> str:
        """
        List available payment methods for checkout
        
        Returns:
            JSON string with payment methods
        """
        methods = [
            {
                "id": "credit_card",
                "name": "Credit Card",
                "description": "Visa, Mastercard, American Express"
            },
            {
                "id": "paypal",
                "name": "PayPal",
                "description": "Pay with your PayPal account"
            },
            {
                "id": "crypto",
                "name": "Cryptocurrency",
                "description": "Bitcoin, Ethereum"
            }
        ]
        
        return json.dumps({
            "success": True,
            "payment_methods": methods
        })
    
    def checkout(self, payment_method: str = "credit_card") -> str:
        """
        Complete the purchase of items in the current cart
        
        Args:
            payment_method: Payment method ID (default: "credit_card")
            
        Returns:
            JSON string with transaction receipt or error
        """
        if not self.current_cart:
            return json.dumps({
                "success": False,
                "error": "No cart available. Please create a cart first."
            })
        
        try:
            # Create PaymentMandate using AP2 protocol
            payment_mandate = PaymentMandate(
                mandate_id=f"pm_{self.current_cart.mandate_id}",
                cart_mandate=self.current_cart,
                payment_method=PaymentMethod(
                    type=payment_method,
                    details={"provider": payment_method}
                ),
                user_id="demo_user",
                merchant_id="pokemon_merchant"
            )
            
            # Send to merchant for processing
            response = requests.post(
                f"{self.merchant_url}/payment/process",
                json=payment_mandate.model_dump(),
                timeout=10
            )
            
            if response.status_code == 200:
                receipt = response.json()
                self.current_cart = None  # Clear cart after successful purchase
                
                return json.dumps({
                    "success": True,
                    "message": "Payment processed successfully! 🎉",
                    "transaction_id": receipt["transaction_id"],
                    "amount_paid": receipt["amount_paid"],
                    "currency": receipt["currency"],
                    "status": receipt["status"],
                    "timestamp": receipt["timestamp"]
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": response.json().get("detail", "Payment failed")
                })
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Checkout error: {str(e)}"
            })


def main():
    """Run the shopping assistant as an interactive chat"""
    
    print("\n" + "=" * 60)
    print("🛍️  POKEMON SHOP - AP2 Shopping Assistant")
    print("=" * 60)
    print("\n✅ Shopping Assistant ready!")
    print("\nExample shopping flows:")
    print("  1. 'I want to buy a Pikachu'")
    print("  2. 'Show me fire Pokemon under $150'")
    print("  3. 'Add Charizard and Blastoise to my cart'")
    print("  4. 'Proceed to checkout with credit card'")
    print("\n" + "=" * 60)
    print("\n💬 What can I help you with? (or 'exit' to quit)\n")
    
    assistant = ShoppingAssistant()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'salir']:
                print("\n👋 Thanks for shopping! Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Assistant: ", end="", flush=True)
            
            # Send message to Gemini
            response = assistant.chat.send_message(user_input)
            
            # Print the response
            print(response.text)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for shopping! Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()

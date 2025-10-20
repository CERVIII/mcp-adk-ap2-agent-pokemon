"""
Shopping Agent - User's personal shopping assistant (Simplified Version)
Uses Google Generative AI with function calling and AP2 protocol support
"""

import os
import json
import uuid
from typing import List, Dict, Any
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
        self.catalog_data = None
        self._load_catalog()
    
    def _load_catalog(self):
        """Load Pokemon catalog from JSON file (MCP responsibility)"""
        import json
        import os
        
        try:
            # Load from project root
            catalog_path = os.path.join(
                os.path.dirname(__file__),
                "../../../pokemon-gen1.json"
            )
            with open(catalog_path, 'r') as f:
                self.catalog_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load catalog: {e}")
            self.catalog_data = []
        self.current_cart_total: float = 0.0
        
    def search_pokemon(
        self,
        query: str | None = None,
        pokemon_type: str | None = None,
        max_price: float | None = None,
        only_available: bool = False
    ) -> str:
        """
        Search for Pokemon in the catalog (uses MCP data source)
        
        Args:
            query: Pokemon name or search term (optional)
            pokemon_type: Pokemon type like 'Fire', 'Water', 'Grass' (optional)
            max_price: Maximum price filter (optional)
            only_available: Only show available Pokemon
            
        Returns:
            Formatted string with search results
        """
        try:
            if not self.catalog_data:
                return "❌ Catalog not available"
            
            results = []
            
            # Filter by query (name or number)
            if query:
                query_lower = query.lower()
                for p in self.catalog_data:
                    if (query_lower in p['nombre'].lower() or 
                        query_lower == str(p['numero'])):
                        results.append(p)
            else:
                results = self.catalog_data.copy()
            
            # Filter by type (using PokeAPI types from pokemon data)
            if pokemon_type and results:
                # Load PokeAPI type data
                import requests
                filtered = []
                for p in results:
                    try:
                        # Get Pokemon type from PokeAPI
                        response = requests.get(
                            f"https://pokeapi.co/api/v2/pokemon/{p['numero']}"
                        )
                        if response.status_code == 200:
                            data = response.json()
                            types = [t['type']['name'].capitalize() 
                                   for t in data['types']]
                            if pokemon_type.capitalize() in types:
                                filtered.append(p)
                    except:
                        pass
                results = filtered
            
            # Filter by price
            if max_price is not None:
                results = [p for p in results if p['precio'] <= max_price]
            
            # Filter by availability
            if only_available:
                results = [p for p in results 
                          if p.get('enVenta') and 
                          p['inventario']['disponibles'] > 0]
            
            # Limit results
            results = results[:10]
            
            if not results:
                filters = []
                if query:
                    filters.append(f"name '{query}'")
                if pokemon_type:
                    filters.append(f"type '{pokemon_type}'")
                if max_price:
                    filters.append(f"price ≤ ${max_price}")
                return f"No Pokemon found matching {', '.join(filters)}"
            
            # Format results
            output = [f"Found {len(results)} Pokemon:\n"]
            for p in results:
                status = "✅" if p.get('enVenta') else "❌"
                stock = p['inventario']['disponibles']
                output.append(
                    f"  • {p['nombre'].capitalize()} (#{p['numero']}) - "
                    f"${p['precio']:.2f} - Stock: {stock} {status}"
                )
            
            return "\n".join(output)
                
        except Exception as e:
            return f"Error searching catalog: {str(e)}"
    
    def create_shopping_cart(
        self,
        items: List[Dict[str, Any]]
    ) -> str:
        """
        Create a shopping cart with Pokemon
        
        Args:
            items: List of items like [{"pokemon": "pikachu", "quantity": 1}]
            
        Returns:
            Cart mandate details
        """
        import requests
        
        try:
            # Transform items format
            cart_items = []
            for item in items:
                cart_items.append({
                    "pokemon": item.get("pokemon", "").lower(),
                    "quantity": item.get("quantity", 1)
                })
            
            response = requests.post(
                f"{self.merchant_url}/cart/create",
                json={"items": cart_items}
            )
            
            if response.status_code == 200:
                data = response.json()
                cart_mandate_data = data.get("cart_mandate", {})
                cart_contents = cart_mandate_data.get("contents", {})
                
                cart_id = cart_contents.get("id", "unknown")
                cart_items_data = cart_contents.get("items", [])
                total_data = cart_contents.get("total", {})
                
                # Format response
                output = [
                    f"✅ Cart created! ID: {cart_id}\n",
                    f"Items in cart:"
                ]
                
                total = total_data.get("value", 0)
                for item in cart_items_data:
                    name = item.get("name", "Unknown")
                    quantity = item.get("quantity", 1)
                    item_total = item.get("total", 0)
                    output.append(
                        f"  • {name} x{quantity} - ${item_total:.2f}"
                    )
                
                output.append(f"\nTotal: ${total:.2f}")
                output.append(f"\nReady to checkout? Just say 'checkout' or 'pay'!")
                
                # Store simplified cart info
                self.current_cart_id = cart_id
                self.current_cart_total = total
                
                return "\n".join(output)
            else:
                error_detail = response.json().get("detail", "Unknown error")
                return f"❌ Error creating cart: {error_detail}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def list_payment_methods(self) -> str:
        """List available payment methods"""
        return """
💳 Available payment methods:
  1. credit_card - Credit or debit card
  2. agent_balance - Your agent balance
  3. crypto - Cryptocurrency payment

All methods are secured by the AP2 protocol!
"""
    
    def view_cart(self) -> str:
        """
        View the current shopping cart
        
        Returns:
            Formatted string with cart contents
        """
        if not self.current_cart:
            return "🛒 Your cart is empty. Search for Pokemon to add items!"
        
        output = ["🛒 Your Shopping Cart:\n"]
        output.append(f"Cart ID: {self.current_cart.mandate_id}\n")
        
        for item in self.current_cart.items:
            subtotal = item.unit_price * item.quantity
            output.append(
                f"  • {item.item_name} x{item.quantity} - "
                f"${item.unit_price:.2f} each = ${subtotal:.2f}"
            )
        
        total = sum(
            item.unit_price * item.quantity
            for item in self.current_cart.items
        )
        output.append(f"\n💰 Total: ${total:.2f} {self.current_cart.currency}")
        output.append(f"\n✅ Ready to checkout? Just say 'checkout' or 'pay'!")
        
        return "\n".join(output)
    
    def checkout(
        self,
        payment_method: str = "credit_card"
    ) -> str:
        """
        Complete the purchase
        
        Args:
            payment_method: Payment method to use
            
        Returns:
            Transaction receipt
        """
        import requests
        
        if not self.current_cart:
            return "❌ No cart found. Please create a cart first with items."
        
        try:
            # Calculate total
            total = sum(
                item.unit_price * item.quantity
                for item in self.current_cart.items
            )
            
            # Create payment mandate
            payment = PaymentMandate(
                mandate_id=str(uuid.uuid4()),
                cart_mandate_id=self.current_cart.mandate_id,
                payment_method=PaymentMethod(
                    type=payment_method,
                    provider="demo_provider"
                ),
                amount=total,
                currency="USD"
            )
            
            # Process payment
            response = requests.post(
                f"{self.merchant_url}/payment/process",
                json=payment.model_dump()
            )
            
            if response.status_code == 200:
                receipt = response.json()
                
                output = [
                    "🎉 Payment successful!\n",
                    f"Transaction ID: {receipt['transaction_id']}",
                    f"Amount paid: ${receipt['amount']:.2f} {receipt['currency']}",
                    f"Payment method: {payment_method}",
                    f"Status: {receipt['status']}\n",
                    "Items purchased:"
                ]
                
                for item in receipt['items']:
                    output.append(f"  • {item['description']} x{item['quantity']}")
                
                output.append("\n✅ Thank you for your purchase!")
                
                # Clear cart
                self.current_cart = None
                
                return "\n".join(output)
            else:
                return f"❌ Payment failed: {response.json().get('detail')}"
                
        except Exception as e:
            return f"❌ Error processing payment: {str(e)}"


# Define function declarations for Gemini using the correct format
def get_tools():
    """Get function declarations in Gemini format"""
    return [
        genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name="search_pokemon",
                    description="Search for Pokemon in the shop catalog by name, type, or characteristics. Use this when the user wants to browse, search, or find Pokemon. You can search by name (e.g., 'pikachu') or by type (e.g., 'Fire', 'Water', 'Grass').",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "query": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Pokemon name or search term (e.g., 'pikachu', 'charizard'). Optional if pokemon_type is provided."
                            ),
                            "pokemon_type": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Pokemon type to filter by (e.g., 'Fire', 'Water', 'Grass', 'Electric', 'Psychic'). Use this when user asks for Pokemon of a specific type."
                            ),
                            "max_price": genai.protos.Schema(
                                type=genai.protos.Type.NUMBER,
                                description="Optional maximum price filter"
                            ),
                            "only_available": genai.protos.Schema(
                                type=genai.protos.Type.BOOLEAN,
                                description="Only show available Pokemon (default: false)"
                            )
                        },
                        required=[]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="create_shopping_cart",
                    description="Create a shopping cart with Pokemon items. Use this when the user wants to buy or add Pokemon to cart.",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "items": genai.protos.Schema(
                                type=genai.protos.Type.ARRAY,
                                description="List of items to add to cart",
                                items=genai.protos.Schema(
                                    type=genai.protos.Type.OBJECT,
                                    properties={
                                        "pokemon": genai.protos.Schema(
                                            type=genai.protos.Type.STRING,
                                            description="Pokemon name (e.g., 'pikachu', 'charizard')"
                                        ),
                                        "quantity": genai.protos.Schema(
                                            type=genai.protos.Type.INTEGER,
                                            description="Quantity to purchase (default: 1)"
                                        )
                                    },
                                    required=["pokemon"]
                                )
                            )
                        },
                        required=["items"]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="view_cart",
                    description="View the current shopping cart contents. Use this when user asks to see their cart, check items, or review their order.",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={}
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="list_payment_methods",
                    description="List available payment methods for checkout",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={}
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="checkout",
                    description="Complete the purchase of items in the current cart. Use this when user wants to pay or complete the order.",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "payment_method": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Payment method: credit_card, agent_balance, or crypto"
                            )
                        }
                    )
                )
            ]
        )
    ]


def main():
    """Run the shopping agent"""
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not configured")
        print("Please create a .env file with your API key")
        return
    
    print("🛍️  Starting Pokemon Shopping Assistant with AP2...")
    print("=" * 60)
    print("\n⚠️  Make sure the Merchant Agent is running on port 8001")
    print("    Start it with: python -m src.roles.merchant_agent\n")
    print("=" * 60)
    
    # Create assistant instance
    assistant = ShoppingAssistant()
    
    # Create model with tools
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',
        tools=get_tools(),
        system_instruction="""You are a helpful Pokemon shopping assistant. You help users:
- Search for Pokemon in the catalog
- Create shopping carts with their favorite Pokemon
- Process secure payments using the AP2 protocol
- Manage orders and transactions

Always use the available tools to help users. When they want to search, use search_pokemon.
When they want to buy, use create_shopping_cart. When they want to pay, use checkout.

Be friendly, helpful, and guide them through the shopping process!"""
    )
    
    # Start chat session
    chat = model.start_chat(enable_automatic_function_calling=False)
    
    print("\n✅ Shopping Assistant ready!")
    print("\nExample shopping flows:")
    print("  1. 'I want to buy a Pikachu'")
    print("  2. 'Show me fire Pokemon under $150'")
    print("  3. 'Add Charizard and Blastoise to my cart'")
    print("  4. 'Proceed to checkout'")
    print("\n" + "=" * 60)
    print("\n💬 What can I help you with? (or 'exit' to quit)\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'salir']:
                print("\n👋 Thanks for shopping! Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Assistant: ", end="", flush=True)
            
            # Send message
            response = chat.send_message(user_input)
            
            # Process function calls if any
            while response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                # Check if it's a function call
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    print(f"[Calling {function_name}...]", end=" ", flush=True)
                    
                    # Execute the function
                    if function_name == "search_pokemon":
                        result = assistant.search_pokemon(**function_args)
                    elif function_name == "create_shopping_cart":
                        result = assistant.create_shopping_cart(**function_args)
                    elif function_name == "view_cart":
                        result = assistant.view_cart()
                    elif function_name == "list_payment_methods":
                        result = assistant.list_payment_methods()
                    elif function_name == "checkout":
                        result = assistant.checkout(**function_args)
                    else:
                        result = f"Unknown function: {function_name}"
                    
                    # Send function response back
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_name,
                                    response={"result": result}
                                )
                            )]
                        )
                    )
                else:
                    # Regular text response
                    if hasattr(part, 'text'):
                        print(part.text)
                    break
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for shopping! Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


if __name__ == "__main__":
    main()

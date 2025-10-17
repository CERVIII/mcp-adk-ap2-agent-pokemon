"""
Merchant Agent - Manages Pokemon catalog and handles purchases
Following AP2 protocol specifications
"""

import os
import uuid
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from ..common.pokemon_utils import (
    load_pokemon_catalog,
    find_pokemon_by_name,
    find_pokemon_by_number,
    search_pokemon,
    create_cart_item,
    format_price
)
from ..common.ap2_types import (
    CartMandate,
    CartItem,
    PaymentAmount,
    TransactionReceipt
)


app = FastAPI(
    title="Pokemon Merchant Agent",
    description="AP2-compliant merchant agent for Pokemon marketplace",
    version="1.0.0"
)


class SearchRequest(BaseModel):
    """Request to search Pokemon catalog"""
    query: str | None = None
    type: str | None = None
    max_price: float | None = None
    min_price: float | None = None
    only_available: bool = False
    limit: int = 10


class CreateCartRequest(BaseModel):
    """Request to create a cart"""
    items: List[Dict[str, Any]]  # List of {pokemon: str, quantity: int}


class PurchaseRequest(BaseModel):
    """Request to complete a purchase"""
    cart_mandate_id: str
    payment_mandate_id: str


# In-memory storage for demo purposes
carts_storage: Dict[str, CartMandate] = {}
transactions_storage: Dict[str, TransactionReceipt] = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Pokemon Merchant Agent",
        "version": "1.0.0",
        "protocol": "AP2",
        "status": "active"
    }


@app.get("/.well-known/agent-card.json")
async def agent_card():
    """
    A2A Agent Card - Describes the agent's capabilities
    Following A2A protocol specification
    """
    return {
        "name": "PokemonMerchantAgent",
        "description": "A merchant agent for Pokemon marketplace using AP2 protocol",
        "capabilities": {
            "extensions": [
                {
                    "description": "Supports the AP2 payments extension",
                    "required": True,
                    "uri": "https://google-agentic-commerce.github.io/AP2/ext/payments/v1"
                }
            ]
        },
        "skills": [
            {
                "id": "search_catalog",
                "name": "Search Pokemon Catalog",
                "description": "Search for Pokemon in the catalog by name, type, price range, etc.",
                "tags": ["pokemon", "search", "catalog"]
            },
            {
                "id": "create_cart",
                "name": "Create Shopping Cart",
                "description": "Create a cart with Pokemon items",
                "tags": ["cart", "purchase"]
            },
            {
                "id": "process_payment",
                "name": "Process Payment",
                "description": "Process a payment for a cart",
                "tags": ["payment", "purchase"]
            }
        ],
        "url": f"http://localhost:{os.getenv('MERCHANT_AGENT_PORT', 8001)}",
        "version": "1.0.0"
    }


@app.get("/catalog")
async def get_catalog():
    """Get the full Pokemon catalog"""
    try:
        catalog = load_pokemon_catalog()
        return {
            "total": len(catalog),
            "items": catalog
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/catalog/search")
async def search_catalog(request: SearchRequest):
    """Search Pokemon catalog with filters"""
    try:
        # Search by name if query provided
        if request.query:
            pokemon = find_pokemon_by_name(request.query)
            if pokemon:
                return {
                    "total": 1,
                    "results": [pokemon]
                }
            
            # Try by number
            try:
                number = int(request.query)
                pokemon = find_pokemon_by_number(number)
                if pokemon:
                    return {
                        "total": 1,
                        "results": [pokemon]
                    }
            except ValueError:
                pass
        
        # General search with filters
        results = search_pokemon(
            type_filter=request.type,
            max_price=request.max_price,
            min_price=request.min_price,
            only_available=request.only_available,
            limit=request.limit
        )
        
        return {
            "total": len(results),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cart/create")
async def create_cart(request: CreateCartRequest):
    """
    Create a CartMandate - AP2 Core Concept
    
    A CartMandate represents the exact items and prices
    that the user will authorize for purchase
    """
    try:
        cart_items: List[CartItem] = []
        total_amount = 0.0
        
        for item_request in request.items:
            pokemon_query = item_request.get("pokemon")
            quantity = item_request.get("quantity", 1)
            
            # Find the Pokemon
            pokemon = find_pokemon_by_name(pokemon_query)
            if not pokemon:
                try:
                    number = int(pokemon_query)
                    pokemon = find_pokemon_by_number(number)
                except ValueError:
                    pass
            
            if not pokemon:
                raise HTTPException(
                    status_code=404,
                    detail=f"Pokemon '{pokemon_query}' not found"
                )
            
            # Check availability
            if not pokemon.get('enVenta', False):
                raise HTTPException(
                    status_code=400,
                    detail=f"Pokemon '{pokemon['nombre']}' is not available for sale"
                )
            
            available_stock = pokemon['inventario']['disponibles']
            if quantity > available_stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only {available_stock} units of '{pokemon['nombre']}' available"
                )
            
            # Create cart item
            cart_item_data = create_cart_item(pokemon, quantity)
            cart_item = CartItem(**cart_item_data)
            cart_items.append(cart_item)
            total_amount += cart_item.total
        
        # Create CartMandate
        cart_id = f"cart_{uuid.uuid4().hex[:8]}"
        cart_mandate = CartMandate(
            id=cart_id,
            items=cart_items,
            total=PaymentAmount(currency="USD", value=total_amount)
        )
        
        # Store cart
        carts_storage[cart_id] = cart_mandate
        
        return {
            "success": True,
            "cart_mandate": cart_mandate.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cart/{cart_id}")
async def get_cart(cart_id: str):
    """Get a cart by ID"""
    if cart_id not in carts_storage:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return carts_storage[cart_id].to_dict()


@app.post("/payment/process")
async def process_payment(request: PurchaseRequest):
    """
    Process a payment - AP2 Payment Flow
    
    In a real implementation, this would:
    1. Validate the PaymentMandate
    2. Verify user authorization
    3. Process payment through payment processor
    4. Update inventory
    5. Return transaction receipt
    """
    try:
        # Verify cart exists
        if request.cart_mandate_id not in carts_storage:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        cart = carts_storage[request.cart_mandate_id]
        
        # In a real implementation, we would:
        # - Validate payment_mandate signature
        # - Process payment through payment processor
        # - Handle 3DS challenges if needed
        # - Update inventory
        
        # For demo: simulate successful payment
        transaction_id = f"txn_{uuid.uuid4().hex[:8]}"
        receipt = TransactionReceipt(
            transaction_id=transaction_id,
            payment_mandate_id=request.payment_mandate_id,
            status="SUCCESS",
            message=f"Successfully purchased {len(cart.items)} Pokemon for {format_price(cart.total.value)}"
        )
        
        transactions_storage[transaction_id] = receipt
        
        return {
            "success": True,
            "receipt": receipt.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transaction/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get a transaction receipt by ID"""
    if transaction_id not in transactions_storage:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transactions_storage[transaction_id].to_dict()


def main():
    """Run the Merchant Agent server"""
    port = int(os.getenv("MERCHANT_AGENT_PORT", 8001))
    
    print(f"🏪 Starting Pokemon Merchant Agent on port {port}...")
    print(f"📋 Agent Card: http://localhost:{port}/.well-known/agent-card.json")
    print(f"🔍 Catalog: http://localhost:{port}/catalog")
    
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()

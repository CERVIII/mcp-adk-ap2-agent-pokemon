"""
Merchant Agent - Manages Pokemon cart and payment operations
Following AP2 protocol specifications
Catalog data is fetched from MCP Server
"""

import os
import uuid
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from src.common.mcp_client import create_mcp_client
from src.common.pokemon_utils import (
    create_cart_item,
    format_price
)
from src.common.ap2_types import (
    CartMandate,
    CartItem,
    PaymentAmount,
    TransactionReceipt
)


# Initialize MCP client
mcp_client = create_mcp_client(use_real_mcp=False)


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
        "name": "Pokemon Merchant Agent (AP2)",
        "version": "1.0.0",
        "protocol": "AP2",
        "status": "active",
        "description": "Manages carts and payments using AP2 protocol. Catalog managed by MCP Server.",
        "endpoints": {
            "cart": "/cart/create",
            "payment": "/payment/process",
            "agent_card": "/.well-known/agent-card.json"
        }
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
                "id": "create_cart",
                "name": "Create Shopping Cart (AP2 CartMandate)",
                "description": "Create a cart mandate with Pokemon items for purchase authorization",
                "tags": ["cart", "purchase", "ap2", "mandate"]
            },
            {
                "id": "process_payment",
                "name": "Process Payment (AP2 PaymentMandate)",
                "description": "Process a payment mandate and complete the transaction",
                "tags": ["payment", "purchase", "ap2", "mandate"]
            }
        ],
        "url": f"http://localhost:{os.getenv('MERCHANT_AGENT_PORT', 8001)}",
        "version": "1.0.0"
    }


# NOTE: Catalog management has been moved to MCP Server
# The merchant agent now focuses only on AP2 protocol operations:
# - Cart management (CartMandates)
# - Payment processing (PaymentMandates)
# 
# For catalog queries, use the MCP Server tools:
# - get_pokemon_info
# - get_pokemon_price
# - search_pokemon


@app.post("/cart/create")
async def create_cart(request: CreateCartRequest):
    """
    Create a CartMandate - AP2 Core Concept
    
    A CartMandate represents the exact items and prices
    that the user will authorize for purchase.
    
    Pokemon data is fetched from MCP Server.
    """
    try:
        cart_items: List[CartItem] = []
        total_amount = 0.0
        
        for item_request in request.items:
            pokemon_query = item_request.get("pokemon")
            quantity = item_request.get("quantity", 1)
            
            # Fetch Pokemon data from MCP Server
            pokemon = await mcp_client.get_pokemon_price(pokemon_query)
            
            if not pokemon:
                raise HTTPException(
                    status_code=404,
                    detail=f"Pokemon '{pokemon_query}' not found in catalog"
                )
            
            # Check availability
            if not pokemon.get('enVenta', False):
                raise HTTPException(
                    status_code=400,
                    detail=f"Pokemon '{pokemon['nombre']}' not available"
                )
            
            available_stock = pokemon['inventario']['disponibles']
            if quantity > available_stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only {available_stock} of '{pokemon['nombre']}'"
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
    import asyncio
    
    port = int(os.getenv("MERCHANT_AGENT_PORT", 8001))
    
    print(f"🏪 Starting Pokemon Merchant Agent (AP2) on port {port}...")
    print(f"📋 Agent Card: http://localhost:{port}/.well-known/agent-card.json")
    print(f"� MCP Client: Connected to catalog data source")
    print(f"💳 AP2 Endpoints: /cart/create, /payment/process")
    
    # Initialize MCP client
    async def init_mcp():
        await mcp_client.start()
    
    asyncio.run(init_mcp())
    
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()

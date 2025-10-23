"""
Merchant Agent - AP2 Protocol Implementation

This agent handles:
- Cart creation and management
- CartMandate generation and signing
- Product catalog queries (via MCP)
- Integration with payment processor
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional

# Add src/mcp/client to path to import mcp_client
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "mcp" / "client"))
from mcp_client import get_mcp_client

from ap2.protocol import (
    CartMandate,
    CartContents,
    PaymentRequest,
    PaymentMethodData,
    PaymentDetails,
    DisplayItem,
    PaymentAmount,
    PaymentOptions,
    generate_cart_id,
    generate_order_id,
    generate_merchant_signature,
    get_current_timestamp,
    get_future_timestamp,
    create_error_response,
    create_success_response,
    AP2_EXTENSION_URI
)

# Initialize FastAPI app
app = FastAPI(
    title="Pokemon Merchant Agent",
    description="AP2 Protocol Merchant Agent for Pokemon marketplace",
    version="1.0.0"
)

# In-memory cart storage
# In production, use a real database
carts: Dict[str, CartMandate] = {}

# Configuration
MERCHANT_NAME = "PokeMart - Primera Generación"
PAYMENT_PROCESSOR_URL = "http://localhost:8003/a2a/processor"


# ============================================
# AgentCard Endpoint (A2A Discovery)
# ============================================

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """
    Return AgentCard following A2A protocol with AP2 extension.
    
    This endpoint is used for agent discovery and capability negotiation.
    """
    return {
        "name": "PokemonMerchantAgent",
        "description": "A merchant agent for Pokemon marketplace with AP2 support",
        "url": "http://localhost:8001/a2a/merchant_agent",
        "version": "1.0.0",
        "capabilities": {
            "extensions": [
                {
                    "uri": AP2_EXTENSION_URI,
                    "description": "Supports AP2 protocol for secure payments",
                    "required": True,
                    "params": {
                        "roles": ["merchant"]
                    }
                }
            ]
        },
        "skills": [
            {
                "id": "search_catalog",
                "name": "Search Pokemon Catalog",
                "description": "Search for Pokemon by type, price, availability",
                "tags": ["search", "catalog", "pokemon"]
            },
            {
                "id": "create_cart",
                "name": "Create Shopping Cart",
                "description": "Create a CartMandate for selected Pokemon",
                "tags": ["cart", "purchase", "ap2"]
            },
            {
                "id": "get_cart",
                "name": "Get Cart Details",
                "description": "Retrieve existing cart by ID",
                "tags": ["cart", "retrieve"]
            }
        ]
    }


# ============================================
# Cart Management Endpoints
# ============================================

@app.post("/a2a/merchant_agent/create_cart")
async def create_cart(request: Dict[str, Any]):
    """
    Create a CartMandate for Pokemon purchase.
    
    This is the core AP2 operation - creates a signed cart
    that guarantees the merchant will fulfill at the stated price.
    
    Request body:
        {
            "items": [
                {"product_id": "25", "quantity": 1},
                ...
            ]
        }
    
    Returns:
        CartMandate object following AP2 specification
    """
    try:
        items = request.get("items", [])
        
        if not items:
            raise HTTPException(status_code=400, detail="No items provided")
        
        # Use MCP to create the cart
        async with get_mcp_client() as mcp:
            cart_mandate_dict = await mcp.create_pokemon_cart(items)
        
        # Convert dict to CartMandate model for validation
        cart_mandate = CartMandate(**cart_mandate_dict)
        
        # Store cart
        cart_id = cart_mandate.contents.id
        carts[cart_id] = cart_mandate
        
        print(f"✅ Created cart {cart_id} with {len(items)} items")
        
        # Return as dict (FastAPI will serialize to JSON)
        return cart_mandate.model_dump()
        
    except Exception as e:
        print(f"❌ Error creating cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/a2a/merchant_agent/cart/{cart_id}")
async def get_cart(cart_id: str):
    """
    Retrieve a cart by ID.
    
    Returns:
        CartMandate if found, 404 if not
    """
    if cart_id not in carts:
        raise HTTPException(status_code=404, detail=f"Cart {cart_id} not found")
    
    return carts[cart_id].model_dump()


@app.get("/a2a/merchant_agent/carts")
async def list_carts():
    """List all carts (for debugging)"""
    return {
        "carts": [
            {
                "id": cart.contents.id,
                "total": cart.contents.payment_request.details.total.amount.value,
                "items": len(cart.contents.payment_request.details.displayItems),
                "timestamp": cart.timestamp
            }
            for cart in carts.values()
        ]
    }


# ============================================
# Catalog Query Endpoints (Proxy to MCP)
# ============================================

@app.post("/a2a/merchant_agent/search")
async def search_pokemon(request: Dict[str, Any]):
    """
    Search Pokemon catalog.
    
    Request body:
        {
            "type": "fire",          // optional
            "minPrice": 10,          // optional
            "maxPrice": 100,         // optional
            "onlyAvailable": true,   // optional
            "limit": 10              // optional
        }
    """
    try:
        async with get_mcp_client() as mcp:
            results = await mcp.search_pokemon(
                type=request.get("type"),
                min_price=request.get("minPrice"),
                max_price=request.get("maxPrice"),
                only_available=request.get("onlyAvailable", False),
                limit=request.get("limit", 10)
            )
        
        return create_success_response(results)
        
    except Exception as e:
        return create_error_response(str(e))


@app.get("/a2a/merchant_agent/product/{product_id}")
async def get_product(product_id: str):
    """Get detailed product information"""
    try:
        async with get_mcp_client() as mcp:
            product = await mcp.get_pokemon_product(product_id)
        
        return create_success_response(product)
        
    except Exception as e:
        return create_error_response(str(e))


# ============================================
# Health Check
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "merchant_agent",
        "version": "1.0.0",
        "carts_count": len(carts)
    }


# ============================================
# Run Server
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("MERCHANT_AGENT_PORT", 8001))
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🏪 POKEMON MERCHANT AGENT (AP2)                 ║
║                                                          ║
║  Port: {port}                                            ║
║  Role: merchant                                          ║
║  Protocol: AP2                                           ║
║                                                          ║
║  Endpoints:                                              ║
║    • POST /a2a/merchant_agent/create_cart               ║
║    • GET  /a2a/merchant_agent/cart/{{cart_id}}            ║
║    • POST /a2a/merchant_agent/search                    ║
║    • GET  /.well-known/agent-card.json                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

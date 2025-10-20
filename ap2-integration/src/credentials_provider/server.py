"""
Credentials Provider Agent - AP2 Protocol

Manages user payment methods and tokenization.
In a real system, this would integrate with actual payment providers.
"""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.common import (
    PaymentMethodInfo,
    mock_payment_token,
    create_success_response,
    create_error_response,
    AP2_EXTENSION_URI
)

app = FastAPI(title="Pokemon Credentials Provider", version="1.0.0")

# Mock payment methods (in production, fetch from real wallet/provider)
MOCK_PAYMENT_METHODS = [
    PaymentMethodInfo(
        id="pm_visa_1234",
        type="CARD",
        display_name="Visa ending in 1234",
        last_four="1234",
        brand="Visa",
        is_default=True
    ),
    PaymentMethodInfo(
        id="pm_mastercard_5678",
        type="CARD",
        display_name="Mastercard ending in 5678",
        last_four="5678",
        brand="Mastercard",
        is_default=False
    )
]


@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """AgentCard for credentials provider"""
    return {
        "name": "PokemonCredentialsProvider",
        "description": "Credentials provider for Pokemon marketplace payments",
        "url": "http://localhost:8002/a2a/credentials_provider",
        "version": "1.0.0",
        "capabilities": {
            "extensions": [{
                "uri": AP2_EXTENSION_URI,
                "description": "AP2 credentials provider role",
                "required": True,
                "params": {"roles": ["credentials-provider"]}
            }]
        },
        "skills": [
            {
                "id": "get_payment_methods",
                "name": "Get Payment Methods",
                "description": "Retrieve available payment methods",
                "tags": ["payment", "methods"]
            },
            {
                "id": "tokenize_payment",
                "name": "Tokenize Payment Method",
                "description": "Generate payment token",
                "tags": ["token", "payment"]
            }
        ]
    }


@app.get("/a2a/credentials_provider/payment_methods")
async def get_payment_methods():
    """Get list of available payment methods"""
    return create_success_response(
        [pm.model_dump() for pm in MOCK_PAYMENT_METHODS],
        "Payment methods retrieved successfully"
    )


@app.post("/a2a/credentials_provider/tokenize")
async def tokenize_payment_method(request: Dict[str, Any]):
    """
    Tokenize a payment method for secure transmission.
    
    Request:
        {"payment_method_id": "pm_visa_1234"}
    
    Returns:
        {"token": "tok_..."}
    """
    payment_method_id = request.get("payment_method_id")
    
    if not payment_method_id:
        raise HTTPException(status_code=400, detail="payment_method_id required")
    
    # Verify payment method exists
    if not any(pm.id == payment_method_id for pm in MOCK_PAYMENT_METHODS):
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    token = mock_payment_token(payment_method_id)
    
    return create_success_response(
        {"token": token, "method_id": payment_method_id},
        "Payment method tokenized successfully"
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "credentials_provider"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("CREDENTIALS_PROVIDER_PORT", 8002))
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║     💳 CREDENTIALS PROVIDER AGENT (AP2)                 ║
║  Port: {port}                                            ║
║  Role: credentials-provider                              ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

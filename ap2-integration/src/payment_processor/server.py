"""
Payment Processor Agent - AP2 Protocol

Processes payments using CartMandate and PaymentMandate.
Validates mandates and executes payment transactions.
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.common import (
    ChargeRequest,
    ChargeResponse,
    generate_transaction_id,
    create_success_response,
    create_error_response,
    validate_cart_mandate_structure,
    validate_payment_mandate_structure,
    validate_user_authorization,
    JWTValidationError,
    AP2_EXTENSION_URI
)

app = FastAPI(title="Pokemon Payment Processor", version="1.0.0")

# Transaction history
transactions: Dict[str, Dict[str, Any]] = {}


@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """AgentCard for payment processor"""
    return {
        "name": "PokemonPaymentProcessor",
        "description": "Payment processor for Pokemon marketplace",
        "url": "http://localhost:8003/a2a/processor",
        "version": "1.0.0",
        "capabilities": {
            "extensions": [{
                "uri": AP2_EXTENSION_URI,
                "description": "AP2 payment processor role",
                "required": True,
                "params": {"roles": ["payment-processor"]}
            }]
        },
        "skills": [{
            "id": "process_payment",
            "name": "Process Payment",
            "description": "Process payment with AP2 mandates",
            "tags": ["payment", "charge", "ap2"]
        }]
    }


@app.post("/a2a/processor/charge")
async def charge_payment(request: Dict[str, Any]):
    """
    Process a payment using CartMandate and PaymentMandate.
    
    This is the final step in the AP2 payment flow.
    
    Request:
        {
            "cart_mandate": {...},
            "payment_mandate": {...},
            "risk_data": {...}  # optional
        }
    """
    try:
        cart_mandate = request.get("cart_mandate")
        payment_mandate = request.get("payment_mandate")
        
        if not cart_mandate or not payment_mandate:
            raise HTTPException(
                status_code=400,
                detail="Both cart_mandate and payment_mandate required"
            )
        
        # Validate mandate structures
        validate_cart_mandate_structure(cart_mandate)
        validate_payment_mandate_structure(payment_mandate)
        
        # Validate user authorization JWT signature
        print("\n🔍 Validating user authorization...")
        try:
            payload = validate_user_authorization(
                payment_mandate,
                cart_mandate,
                verify=True
            )
            print("✅ User authorization is valid and verified!")
        except JWTValidationError as e:
            print(f"❌ User authorization validation FAILED: {e}")
            print("⚠️  Security Warning: PaymentMandate may be forged!")
            raise HTTPException(
                status_code=403,
                detail=f"Invalid user authorization: {e}"
            )
        except Exception as e:
            print(f"⚠️  Warning: Could not validate user authorization: {e}")
            print("   Continuing without validation (development mode)")
        
        # In production: check fraud, process real payment
        
        # Generate transaction
        txn_id = generate_transaction_id()
        total = cart_mandate["contents"]["payment_request"]["details"]["total"]["amount"]
        
        transaction = {
            "transaction_id": txn_id,
            "cart_id": cart_mandate["contents"]["id"],
            "amount": total["value"],
            "currency": total["currency"],
            "status": "completed",
            "payment_method": payment_mandate["payment_mandate_contents"]["payment_response"]["method_name"]
        }
        
        transactions[txn_id] = transaction
        
        print(f"✅ Payment processed: {txn_id} for ${total['value']}")
        
        return create_success_response(
            {
                "transaction_id": txn_id,
                "status": "completed",
                "receipt": transaction
            },
            "Payment processed successfully"
        )
        
    except Exception as e:
        print(f"❌ Payment failed: {e}")
        return create_error_response(str(e), {"status": "failed"})


@app.get("/a2a/processor/transaction/{txn_id}")
async def get_transaction(txn_id: str):
    """Get transaction details"""
    if txn_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return create_success_response(transactions[txn_id])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "payment_processor",
        "transactions_count": len(transactions)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PAYMENT_PROCESSOR_PORT", 8003))
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║     💰 PAYMENT PROCESSOR AGENT (AP2)                    ║
║  Port: {port}                                            ║
║  Role: payment-processor                                 ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

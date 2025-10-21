"""
Payment Processor Agent - AP2 Protocol

Processes payments using CartMandate and PaymentMandate.
Validates mandates and executes payment transactions.
"""

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
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
from src.database import (
    init_db,
    get_db,
    TransactionRepository,
    PokemonRepository,
    get_db_stats
)

app = FastAPI(title="Pokemon Payment Processor", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Payment Processor initialized with database")


# Transaction history (keeping for backward compatibility, but using DB now)
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
async def charge_payment(request: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Process a payment using CartMandate and PaymentMandate.
    
    This is the final step in the AP2 payment flow.
    Now saves transactions to database.
    
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
        
        # Extract transaction info
        txn_id = generate_transaction_id()
        cart_id = cart_mandate["contents"]["id"]
        total = cart_mandate["contents"]["payment_request"]["details"]["total"]["amount"]
        display_items = cart_mandate["contents"]["payment_request"]["details"]["displayItems"]
        
        # Build items list for transaction
        items = []
        for display_item in display_items:
            # Extract Pokemon numero from label (e.g., "Pikachu #25")
            label = display_item["label"]
            if "#" in label:
                numero_str = label.split("#")[-1].split()[0]
                numero = int(numero_str)
                
                # Get quantity from somewhere (default 1 for now)
                # In a real system, this would come from cart_mandate details
                quantity = 1
                unit_price = display_item["amount"]["value"]
                
                items.append({
                    "pokemon_numero": numero,
                    "quantity": quantity,
                    "unit_price": unit_price
                })
        
        # Save transaction to database
        print(f"\n💾 Saving transaction to database...")
        transaction_repo = TransactionRepository(db)
        
        try:
            db_transaction = transaction_repo.create(
                transaction_id=txn_id,
                cart_id=cart_id,
                cart_mandate=cart_mandate,
                payment_mandate=payment_mandate,
                items=items,
                status="completed"
            )
            
            print(f"✅ Transaction saved to database: {txn_id}")
            print(f"   Amount: ${db_transaction.total_amount}")
            print(f"   Items: {len(db_transaction.items)}")
            
        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            # Rollback and raise
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {db_error}"
            )
        
        # Keep in memory for backward compatibility
        transaction = {
            "transaction_id": txn_id,
            "cart_id": cart_id,
            "amount": total["value"],
            "currency": total["currency"],
            "status": "completed",
            "payment_method": payment_mandate["payment_mandate_contents"]["payment_response"]["method_name"],
            "payment_id": db_transaction.id
        }
        
        transactions[txn_id] = transaction
        
        print(f"✅ Payment processed: {txn_id} for ${total['value']}")
        
        return create_success_response(
            {
                "transaction_id": txn_id,
                "status": "completed",
                "receipt": transaction,
                "database_id": db_transaction.id
            },
            "Payment processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Payment failed: {e}")
        import traceback
        traceback.print_exc()
        return create_error_response(str(e), {"status": "failed"})


@app.get("/a2a/processor/transaction/{txn_id}")
async def get_transaction(txn_id: str, db: Session = Depends(get_db)):
    """Get transaction details from database"""
    transaction_repo = TransactionRepository(db)
    db_transaction = transaction_repo.get_by_id(txn_id)
    
    if not db_transaction:
        # Try in-memory transactions (backward compatibility)
        if txn_id in transactions:
            return create_success_response(transactions[txn_id])
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return create_success_response(db_transaction.to_dict())


@app.get("/a2a/processor/transactions")
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List all transactions from database"""
    transaction_repo = TransactionRepository(db)
    transactions_list = transaction_repo.get_all(skip=skip, limit=limit, status=status)
    
    return create_success_response({
        "transactions": [t.to_dict() for t in transactions_list],
        "count": len(transactions_list)
    })


@app.get("/a2a/processor/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get transaction and inventory statistics"""
    transaction_repo = TransactionRepository(db)
    pokemon_repo = PokemonRepository(db)
    
    transaction_stats = transaction_repo.get_stats()
    inventory_stats = pokemon_repo.get_inventory_stats()
    db_stats = get_db_stats()
    
    return create_success_response({
        "database": db_stats,
        "transactions": transaction_stats,
        "inventory": inventory_stats,
    })


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with database connection test"""
    try:
        # Test database connection
        pokemon_repo = PokemonRepository(db)
        pokemon_count = len(pokemon_repo.get_all(limit=1))
        
        return {
            "status": "healthy",
            "service": "payment_processor",
            "database": "connected",
            "transactions_count_memory": len(transactions),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "payment_processor",
            "database": f"error: {e}",
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

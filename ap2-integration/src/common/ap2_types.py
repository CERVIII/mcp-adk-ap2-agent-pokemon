"""
Tipos de datos para el protocolo AP2
Basado en las especificaciones de AP2
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PaymentAmount(BaseModel):
    """Amount in a payment"""
    currency: str = "USD"
    value: float


class PaymentDetails(BaseModel):
    """Details for a payment"""
    label: str
    amount: PaymentAmount


class CartItem(BaseModel):
    """Item in a shopping cart"""
    product_id: str
    name: str
    quantity: int = 1
    price: float
    total: float
    available: bool = True


class CartMandate(BaseModel):
    """
    Cart Mandate - Represents the user's explicit authorization
    for a specific cart with exact items and prices
    """
    id: str
    items: List[CartItem]
    total: PaymentAmount
    merchant_name: str = "Pokemon Shop"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    user_signature_required: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contents": {
                "id": self.id,
                "items": [item.model_dump() for item in self.items],
                "total": self.total.model_dump(),
                "merchant_name": self.merchant_name,
                "user_signature_required": self.user_signature_required
            },
            "timestamp": self.timestamp
        }


class PaymentMethod(BaseModel):
    """Payment method information"""
    id: str
    type: str  # e.g., "CARD", "DIGITAL_WALLET"
    display_name: str
    last_four: Optional[str] = None


class PaymentMandate(BaseModel):
    """
    Payment Mandate - Contains the user's final authorization
    including payment method and cart details
    """
    payment_mandate_id: str
    cart_mandate_id: str
    payment_method: PaymentMethod
    total: PaymentAmount
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    user_authorization: Optional[str] = None  # Digital signature
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "payment_mandate_contents": {
                "payment_mandate_id": self.payment_mandate_id,
                "cart_mandate_id": self.cart_mandate_id,
                "payment_method": self.payment_method.model_dump(),
                "total": self.total.model_dump()
            },
            "timestamp": self.timestamp,
            "user_authorization": self.user_authorization
        }


class IntentMandate(BaseModel):
    """
    Intent Mandate - Captures conditions under which an AI Agent
    can make a purchase on behalf of the user
    """
    intent_id: str
    description: str
    max_amount: PaymentAmount
    categories: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    valid_until: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "description": self.description,
            "max_amount": self.max_amount.model_dump(),
            "categories": self.categories,
            "timestamp": self.timestamp,
            "valid_until": self.valid_until
        }


class TransactionReceipt(BaseModel):
    """Receipt for a completed transaction"""
    transaction_id: str
    payment_mandate_id: str
    status: str  # "SUCCESS", "FAILED", "PENDING"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "payment_mandate_id": self.payment_mandate_id,
            "status": self.status,
            "timestamp": self.timestamp,
            "message": self.message
        }

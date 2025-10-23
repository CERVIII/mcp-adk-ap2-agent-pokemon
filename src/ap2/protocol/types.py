"""
AP2 Protocol Types - Python implementation

Based on the official AP2 specification:
https://ap2-protocol.org/specification/
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================
# Payment Request Types (W3C Standard)
# ============================================

class PaymentAmount(BaseModel):
    """Currency amount following W3C Payment Request API"""
    currency: str = Field(..., description="ISO 4217 currency code (e.g., USD)")
    value: float = Field(..., description="Numeric amount")


class DisplayItem(BaseModel):
    """Individual line item in a payment"""
    label: str = Field(..., description="Human-readable item name")
    amount: PaymentAmount
    pending: Optional[bool] = Field(None, description="Whether amount might change")


class PaymentMethodData(BaseModel):
    """Payment method accepted by merchant"""
    supported_methods: str = Field(..., description="Payment method identifier (e.g., CARD, X402)")
    data: Dict[str, Any] = Field(..., description="Method-specific configuration")


class PaymentOptions(BaseModel):
    """Options for payment collection"""
    requestPayerName: bool = False
    requestPayerEmail: bool = False
    requestPayerPhone: bool = False
    requestShipping: bool = False
    shippingType: Optional[str] = None


class PaymentDetails(BaseModel):
    """Complete payment details"""
    id: str = Field(..., description="Unique order/payment ID")
    displayItems: List[DisplayItem] = Field(..., description="Line items")
    shipping_options: Optional[List[Any]] = None
    modifiers: Optional[List[Any]] = None
    total: DisplayItem = Field(..., description="Total amount")


class PaymentRequest(BaseModel):
    """W3C Payment Request structure"""
    method_data: List[PaymentMethodData] = Field(..., description="Accepted payment methods")
    details: PaymentDetails = Field(..., description="Payment details")
    options: PaymentOptions = Field(default_factory=PaymentOptions)


class PaymentResponse(BaseModel):
    """Response from payment method selection"""
    request_id: str = Field(..., description="Original request ID")
    method_name: str = Field(..., description="Selected payment method")
    details: Dict[str, Any] = Field(..., description="Payment method specific data (e.g., token)")
    shipping_address: Optional[Dict[str, Any]] = None
    shipping_option: Optional[str] = None
    payer_name: Optional[str] = None
    payer_email: Optional[str] = None
    payer_phone: Optional[str] = None


# ============================================
# AP2 Mandate Types
# ============================================

class CartItem(BaseModel):
    """
    Individual item in a shopping cart.
    Extension field for inventory management.
    """
    product_id: str = Field(..., description="Product identifier")
    quantity: int = Field(default=1, description="Quantity to purchase")


class CartContents(BaseModel):
    """
    Contents of a shopping cart.
    This object gets signed by the merchant to create a CartMandate.
    """
    id: str = Field(..., description="Unique cart identifier")
    user_cart_confirmation_required: bool = Field(
        ...,
        description="Whether user must explicitly confirm this cart"
    )
    payment_request: PaymentRequest = Field(
        ...,
        description="W3C PaymentRequest containing items, prices, and accepted methods"
    )
    cart_expiry: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp when cart expires"
    )
    merchant_name: str = Field(..., description="Name of the merchant")
    items: Optional[List[CartItem]] = Field(
        None,
        description="Extension: Original items for inventory management"
    )


class CartMandate(BaseModel):
    """
    A cart digitally signed by the merchant.
    
    This is the core VDC (Verifiable Digital Credential) for human-present transactions.
    The merchant's signature guarantees they will fulfill the order at the specified price.
    """
    contents: CartContents = Field(..., description="Cart details")
    merchant_signature: str = Field(
        ...,
        description="Base64url-encoded JWT signing the cart_hash (in production, use real JWT)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of cart creation"
    )
    merchantName: Optional[str] = Field(None, description="Merchant display name")

    class Config:
        json_schema_extra = {
            "example": {
                "contents": {
                    "id": "cart_pikachu_abc123",
                    "user_cart_confirmation_required": False,
                    "payment_request": {
                        "method_data": [{
                            "supported_methods": "CARD",
                            "data": {"payment_processor_url": "http://localhost:8003/a2a/processor"}
                        }],
                        "details": {
                            "id": "order_pikachu_xyz789",
                            "displayItems": [{
                                "label": "Pikachu (x1)",
                                "amount": {"currency": "USD", "value": 55.0}
                            }],
                            "total": {
                                "label": "Total",
                                "amount": {"currency": "USD", "value": 55.0}
                            }
                        }
                    },
                    "merchant_name": "PokeMart - Primera Generación"
                },
                "merchant_signature": "sig_merchant_pokemon_abc123",
                "timestamp": "2025-01-20T10:30:00Z"
            }
        }


class PaymentMandateContents(BaseModel):
    """
    Contents of a payment mandate.
    This contains the user's payment authorization details.
    """
    payment_mandate_id: str = Field(..., description="Unique payment mandate ID")
    payment_details_id: str = Field(..., description="Reference to order ID")
    payment_details_total: DisplayItem = Field(..., description="Total amount being authorized")
    payment_response: PaymentResponse = Field(
        ...,
        description="User's selected payment method and details"
    )
    merchant_agent: str = Field(..., description="Identifier of merchant agent")
    credential_provider_agent: str = Field(..., description="Identifier of credentials provider")
    risk_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Risk signals for fraud detection"
    )


class PaymentMandate(BaseModel):
    """
    Payment Mandate - VDC for payment authorization.
    
    This is shared with the payment network/issuer to provide visibility
    into the agentic transaction and help assess transaction context.
    """
    payment_mandate_contents: PaymentMandateContents
    user_authorization: Optional[str] = Field(
        None,
        description="Base64url-encoded verifiable credential with user's signature (e.g., sd-jwt-vc)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of mandate creation"
    )


class IntentMandate(BaseModel):
    """
    Intent Mandate - For human-not-present transactions.
    
    Captures conditions under which an AI Agent can make purchases
    on behalf of the user without real-time confirmation.
    """
    user_cart_confirmation_required: bool = Field(
        True,
        description="If False, agent can purchase without additional confirmation"
    )
    natural_language_description: str = Field(
        ...,
        description="User's intent in natural language, confirmed by user"
    )
    merchants: Optional[List[str]] = Field(
        None,
        description="Allowed merchants to fulfill intent"
    )
    skus: Optional[List[str]] = Field(
        None,
        description="Specific SKUs authorized"
    )
    intent_expiry: str = Field(
        ...,
        description="ISO 8601 timestamp when intent expires"
    )
    max_amount: Optional[PaymentAmount] = Field(
        None,
        description="Maximum authorized spend"
    )


# ============================================
# AP2 Request/Response Types
# ============================================

class CreateCartRequest(BaseModel):
    """Request to create a cart mandate"""
    items: List[Dict[str, Any]] = Field(..., description="Items to add to cart")
    user_id: Optional[str] = Field(None, description="User identifier")


class PaymentMethodInfo(BaseModel):
    """Information about an available payment method"""
    id: str = Field(..., description="Unique payment method ID")
    type: str = Field(..., description="Payment method type (CARD, X402, etc)")
    display_name: str = Field(..., description="Human-readable name")
    last_four: Optional[str] = Field(None, description="Last 4 digits of card")
    brand: Optional[str] = Field(None, description="Card brand (Visa, Mastercard, etc)")
    is_default: bool = Field(False, description="Whether this is the default method")


class ChargeRequest(BaseModel):
    """Request to charge a payment"""
    cart_mandate: CartMandate = Field(..., description="Signed cart mandate")
    payment_mandate: PaymentMandate = Field(..., description="Signed payment mandate")
    risk_data: Optional[Dict[str, Any]] = Field(None, description="Additional risk signals")


class ChargeResponse(BaseModel):
    """Response from payment charge"""
    success: bool = Field(..., description="Whether charge succeeded")
    transaction_id: Optional[str] = Field(None, description="Transaction ID if successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    receipt: Optional[Dict[str, Any]] = Field(None, description="Payment receipt")


# ============================================
# A2A Extension Types
# ============================================

class AP2Extension(BaseModel):
    """AP2 extension parameters for A2A AgentCard"""
    roles: List[str] = Field(
        ...,
        description="AP2 roles this agent performs (merchant, shopper, credentials-provider, payment-processor)"
    )


class AgentCard(BaseModel):
    """A2A Agent Card with AP2 extension"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    url: str = Field(..., description="Agent base URL")
    version: str = Field(default="1.0.0", description="Agent version")
    capabilities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Agent capabilities including extensions"
    )
    skills: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Agent skills/operations"
    )


# ============================================
# Data Keys for A2A Messages
# ============================================

# Standard data part keys used in A2A messages
CART_MANDATE_DATA_KEY = "ap2.mandates.CartMandate"
PAYMENT_MANDATE_DATA_KEY = "ap2.mandates.PaymentMandate"
INTENT_MANDATE_DATA_KEY = "ap2.mandates.IntentMandate"

# AP2 Extension URI
AP2_EXTENSION_URI = "https://google-a2a.github.io/A2A/extensions/payments/v1"

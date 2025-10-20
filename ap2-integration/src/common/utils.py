"""
Common utilities for AP2 integration
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate RSA key pair for demo (in production, use proper key management)
# Merchant's private key for signing CartMandates
MERCHANT_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

MERCHANT_PUBLIC_KEY = MERCHANT_PRIVATE_KEY.public_key()

# User's private key for signing PaymentMandates (simulating user's device)
USER_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

USER_PUBLIC_KEY = USER_PRIVATE_KEY.public_key()

# Convert keys to PEM format for JWT
MERCHANT_PRIVATE_PEM = MERCHANT_PRIVATE_KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

USER_PRIVATE_PEM = USER_PRIVATE_KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)


def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id[:8]}"
    return unique_id


def generate_cart_id() -> str:
    """Generate unique cart ID"""
    return generate_unique_id("cart_pokemon")


def generate_order_id() -> str:
    """Generate unique order ID"""
    return generate_unique_id("order_pokemon")


def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    return generate_unique_id("txn")


def generate_merchant_signature(cart_id: str) -> str:
    """
    Generate merchant signature for cart as a JWT.
    
    Creates a real JWT signed with the merchant's private key according to AP2 spec.
    The JWT contains the cart_id and merchant identity information.
    
    Args:
        cart_id: The cart identifier to sign
        
    Returns:
        Base64url-encoded JWT string
    """
    now = datetime.now(timezone.utc)
    payload = {
        "iss": "PokeMart",  # Issuer (merchant name)
        "sub": cart_id,      # Subject (cart ID)
        "iat": int(now.timestamp()),  # Issued at
        "exp": int((now + timedelta(hours=1)).timestamp()),  # Expires in 1 hour
        "cart_id": cart_id,
        "merchant": "PokeMart - Primera Generación"
    }
    
    # Sign with RS256 algorithm using merchant's private key
    token = jwt.encode(payload, MERCHANT_PRIVATE_PEM, algorithm="RS256")
    return token


def generate_user_authorization(cart_hash: str, payment_hash: str) -> str:
    """
    Generate user authorization signature as a JWT.
    
    Creates a verifiable credential (JWT-VC format) signed by the user's device key
    according to AP2 specification. In production, this would be generated on the
    user's device with their private key.
    
    Args:
        cart_hash: Hash of the CartMandate
        payment_hash: Hash of the PaymentMandateContents
        
    Returns:
        Base64url-encoded JWT string (simulating sd-jwt-vc)
    """
    now = datetime.now(timezone.utc)
    payload = {
        "iss": "user_device",  # Issuer (user's device)
        "sub": "trainer@pokemon.com",  # Subject (user ID)
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),  # Short expiry for security
        "cart_hash": cart_hash,
        "payment_hash": payment_hash,
        "vc": {  # Verifiable Credential
            "type": ["VerifiableCredential", "PaymentAuthorization"],
            "credentialSubject": {
                "id": "did:example:user123",
                "cart_hash": cart_hash,
                "payment_hash": payment_hash,
                "consent": "explicit"
            }
        }
    }
    
    # Sign with RS256 algorithm using user's private key
    token = jwt.encode(payload, USER_PRIVATE_PEM, algorithm="RS256")
    return token


def get_current_timestamp() -> str:
    """Get current ISO 8601 timestamp"""
    return datetime.now(timezone.utc).isoformat()


def get_future_timestamp(hours: int = 1) -> str:
    """Get future ISO 8601 timestamp"""
    future = datetime.now(timezone.utc) + timedelta(hours=hours)
    return future.isoformat()


def hash_object(obj: Dict[str, Any]) -> str:
    """
    Generate SHA-256 hash of an object.
    
    Used for creating non-repudiable hashes of mandates.
    """
    # Convert to canonical JSON (sorted keys)
    json_str = json.dumps(obj, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(json_str.encode()).hexdigest()


def hash_cart_mandate(cart_mandate: Dict[str, Any]) -> str:
    """Hash CartMandate contents"""
    return hash_object(cart_mandate.get("contents", {}))


def hash_payment_mandate_contents(payment_contents: Dict[str, Any]) -> str:
    """Hash PaymentMandateContents"""
    return hash_object(payment_contents)


def validate_cart_mandate_structure(cart_mandate: Dict[str, Any]) -> bool:
    """
    Validate CartMandate has required fields.
    
    Returns:
        True if valid, raises ValueError if not
    """
    required_fields = ["contents", "merchant_signature", "timestamp"]
    
    for field in required_fields:
        if field not in cart_mandate:
            raise ValueError(f"CartMandate missing required field: {field}")
    
    contents = cart_mandate["contents"]
    required_content_fields = ["id", "user_cart_confirmation_required", "payment_request"]
    
    for field in required_content_fields:
        if field not in contents:
            raise ValueError(f"CartMandate contents missing required field: {field}")
    
    return True


def validate_payment_mandate_structure(payment_mandate: Dict[str, Any]) -> bool:
    """
    Validate PaymentMandate has required fields.
    
    Returns:
        True if valid, raises ValueError if not
    """
    required_fields = ["payment_mandate_contents", "timestamp"]
    
    for field in required_fields:
        if field not in payment_mandate:
            raise ValueError(f"PaymentMandate missing required field: {field}")
    
    return True


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string"""
    if currency == "USD":
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"


def parse_pokemon_identifier(identifier: str) -> tuple[str, str]:
    """
    Parse Pokemon identifier into (type, value).
    
    Args:
        identifier: Can be name ("pikachu") or number ("25" or "025")
        
    Returns:
        ("name", value) or ("number", value)
    """
    # Check if it's a number
    if identifier.isdigit():
        return ("number", identifier.lstrip("0") or "0")
    
    # Otherwise it's a name
    return ("name", identifier.lower())


def create_error_response(message: str, details: Any = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "error": True,
        "message": message,
        "timestamp": get_current_timestamp()
    }
    
    if details is not None:
        response["details"] = details
    
    return response


def create_success_response(data: Any, message: str = None) -> Dict[str, Any]:
    """Create standardized success response"""
    response = {
        "success": True,
        "data": data,
        "timestamp": get_current_timestamp()
    }
    
    if message:
        response["message"] = message
    
    return response


# ============================================
# Demo/Mock functions
# ============================================

def mock_risk_data() -> Dict[str, Any]:
    """
    Generate mock risk data.
    
    In production, this would come from real fraud detection systems.
    """
    return {
        "device_fingerprint": generate_unique_id("device"),
        "ip_address": "127.0.0.1",
        "user_agent": "Pokemon-Shopping-Agent/1.0",
        "session_id": generate_unique_id("session"),
        "risk_score": 0.15,  # Low risk
        "timestamp": get_current_timestamp()
    }


def mock_payment_token(payment_method_id: str) -> str:
    """
    Generate mock payment token.
    
    In production, this would be a real tokenized payment credential.
    """
    return f"tok_{payment_method_id}_{uuid.uuid4().hex[:16]}"


# ============================================
# Pretty printing
# ============================================

def print_cart_summary(cart_mandate: Dict[str, Any]):
    """Pretty print cart summary"""
    contents = cart_mandate["contents"]
    details = contents["payment_request"]["details"]
    
    print("\n" + "="*60)
    print("🛒 CART SUMMARY")
    print("="*60)
    print(f"Cart ID: {contents['id']}")
    print(f"Merchant: {contents.get('merchant_name', 'Unknown')}")
    print(f"Expires: {contents.get('cart_expiry', 'N/A')}")
    print("\nItems:")
    
    for item in details["displayItems"]:
        print(f"  • {item['label']}: {format_currency(item['amount']['value'], item['amount']['currency'])}")
    
    total = details["total"]["amount"]
    print(f"\nTotal: {format_currency(total['value'], total['currency'])}")
    print("="*60 + "\n")


def print_payment_summary(payment_mandate: Dict[str, Any]):
    """Pretty print payment summary"""
    contents = payment_mandate["payment_mandate_contents"]
    
    print("\n" + "="*60)
    print("💳 PAYMENT SUMMARY")
    print("="*60)
    print(f"Payment ID: {contents['payment_mandate_id']}")
    print(f"Order ID: {contents['payment_details_id']}")
    
    total = contents["payment_details_total"]["amount"]
    print(f"Amount: {format_currency(total['value'], total['currency'])}")
    
    method = contents["payment_response"]["method_name"]
    print(f"Payment Method: {method}")
    
    print("="*60 + "\n")

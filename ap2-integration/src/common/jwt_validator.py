"""
JWT Validation Module - AP2 Security

This module handles validation of JWT signatures according to AP2 specification:
1. Merchant signatures on CartMandates (from MCP server)
2. User authorizations on PaymentMandates (from user device)

Security requirements:
- Verify JWT structure (3 parts: header.payload.signature)
- Validate signature using public keys
- Check expiration timestamps
- Validate issuer and subject claims
- Reject invalid or expired tokens
"""

import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import requests
import os
from pathlib import Path


class JWTValidationError(Exception):
    """Exception raised when JWT validation fails"""
    pass


class JWTValidator:
    """Validates JWT tokens for AP2 mandates"""
    
    def __init__(self):
        """Initialize validator with public keys"""
        # Path to MCP server's public keys
        self.mcp_keys_dir = self._get_mcp_keys_directory()
        self.merchant_public_key = None
        self.user_public_key = None
        
        # Load keys
        self._load_keys()
    
    def _get_mcp_keys_directory(self) -> Path:
        """Get path to MCP server keys directory"""
        # From ap2-integration/src/common -> ../../../mcp-server/keys
        current_dir = Path(__file__).parent
        mcp_keys = current_dir.parent.parent.parent / "mcp-server" / "keys"
        return mcp_keys
    
    def _load_keys(self):
        """Load public keys from disk"""
        try:
            # Load merchant public key from MCP server
            merchant_key_path = self.mcp_keys_dir / "merchant_public.pem"
            
            if merchant_key_path.exists():
                with open(merchant_key_path, 'rb') as f:
                    self.merchant_public_key = serialization.load_pem_public_key(
                        f.read(),
                        backend=default_backend()
                    )
                print(f"✅ Loaded merchant public key from: {merchant_key_path}")
            else:
                print(f"⚠️  Warning: Merchant public key not found at {merchant_key_path}")
                print("   JWT validation will fail. Run MCP server first to generate keys.")
            
            # User public key would be loaded from a user registry in production
            # For now, we'll use the one from utils.py for backward compatibility
            from .utils import USER_PUBLIC_KEY
            self.user_public_key = USER_PUBLIC_KEY
            print("✅ Loaded user public key (from memory)")
            
        except Exception as e:
            print(f"❌ Error loading public keys: {e}")
            raise
    
    def validate_jwt_structure(self, token: str) -> bool:
        """
        Validate JWT has correct structure.
        
        Args:
            token: JWT string
            
        Returns:
            True if valid structure
            
        Raises:
            JWTValidationError if invalid structure
        """
        if not token:
            raise JWTValidationError("JWT token is empty")
        
        parts = token.split('.')
        if len(parts) != 3:
            raise JWTValidationError(
                f"Invalid JWT structure: expected 3 parts (header.payload.signature), "
                f"got {len(parts)} parts"
            )
        
        # Check each part is base64url encoded
        for i, part in enumerate(parts):
            if not part or not part.strip():
                part_names = ['header', 'payload', 'signature']
                raise JWTValidationError(
                    f"JWT {part_names[i]} is empty"
                )
        
        return True
    
    def validate_merchant_signature(
        self,
        cart_mandate: Dict[str, Any],
        verify_signature: bool = True
    ) -> Dict[str, Any]:
        """
        Validate merchant signature on CartMandate.
        
        Args:
            cart_mandate: The CartMandate to validate
            verify_signature: Whether to verify cryptographic signature (default True)
            
        Returns:
            Decoded JWT payload if valid
            
        Raises:
            JWTValidationError if validation fails
        """
        # Extract merchant signature
        merchant_sig = cart_mandate.get("merchant_signature")
        if not merchant_sig:
            raise JWTValidationError("CartMandate missing merchant_signature")
        
        # Validate structure
        self.validate_jwt_structure(merchant_sig)
        
        if not verify_signature:
            # Decode without verification (for testing)
            try:
                payload = jwt.decode(merchant_sig, options={"verify_signature": False})
                print("⚠️  JWT decoded WITHOUT signature verification (testing mode)")
                return payload
            except jwt.DecodeError as e:
                raise JWTValidationError(f"Failed to decode JWT: {e}")
        
        # Verify signature with merchant's public key
        if not self.merchant_public_key:
            raise JWTValidationError(
                "Merchant public key not loaded. Cannot verify signature. "
                "Make sure MCP server has generated keys."
            )
        
        try:
            # Convert public key to PEM format for jwt library
            public_key_pem = self.merchant_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Decode and verify
            payload = jwt.decode(
                merchant_sig,
                public_key_pem,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,  # Verify expiration
                    "verify_iat": True,  # Verify issued-at
                }
            )
            
            # Validate claims
            cart_id = cart_mandate["contents"]["id"]
            
            # Check subject matches cart_id
            if payload.get("sub") != cart_id:
                raise JWTValidationError(
                    f"JWT subject '{payload.get('sub')}' doesn't match cart_id '{cart_id}'"
                )
            
            # Check issuer is expected merchant
            expected_issuer = "PokeMart"
            if payload.get("iss") != expected_issuer:
                raise JWTValidationError(
                    f"Unexpected issuer: '{payload.get('iss')}', expected '{expected_issuer}'"
                )
            
            # Check cart_id claim
            if payload.get("cart_id") != cart_id:
                raise JWTValidationError(
                    f"JWT cart_id claim '{payload.get('cart_id')}' doesn't match '{cart_id}'"
                )
            
            print(f"✅ Merchant signature validated successfully")
            print(f"   Issuer: {payload.get('iss')}")
            print(f"   Cart ID: {payload.get('cart_id')}")
            print(f"   Issued: {datetime.fromtimestamp(payload.get('iat'), tz=timezone.utc)}")
            print(f"   Expires: {datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise JWTValidationError("JWT signature has expired")
        except jwt.InvalidSignatureError:
            raise JWTValidationError("JWT signature verification failed - signature is invalid")
        except jwt.DecodeError as e:
            raise JWTValidationError(f"Failed to decode JWT: {e}")
        except Exception as e:
            raise JWTValidationError(f"JWT validation error: {e}")
    
    def validate_user_authorization(
        self,
        payment_mandate: Dict[str, Any],
        cart_mandate: Dict[str, Any],
        verify_signature: bool = True
    ) -> Dict[str, Any]:
        """
        Validate user authorization on PaymentMandate.
        
        Args:
            payment_mandate: The PaymentMandate to validate
            cart_mandate: The associated CartMandate
            verify_signature: Whether to verify cryptographic signature (default True)
            
        Returns:
            Decoded JWT payload if valid
            
        Raises:
            JWTValidationError if validation fails
        """
        # Extract user authorization
        user_auth = payment_mandate.get("user_authorization")
        if not user_auth:
            raise JWTValidationError("PaymentMandate missing user_authorization")
        
        # Validate structure
        self.validate_jwt_structure(user_auth)
        
        if not verify_signature:
            # Decode without signature verification (for testing)
            # But still validate hashes for tampering detection
            try:
                payload = jwt.decode(user_auth, options={"verify_signature": False})
                print("⚠️  JWT decoded WITHOUT signature verification (testing mode)")
                
                # Still validate hashes even without signature verification
                from .utils import hash_cart_mandate, hash_payment_mandate_contents
                
                expected_cart_hash = hash_cart_mandate(cart_mandate)
                actual_cart_hash = payload.get("cart_hash")
                
                if actual_cart_hash != expected_cart_hash:
                    raise JWTValidationError(
                        "Cart hash mismatch - CartMandate may have been tampered with"
                    )
                
                payment_contents = payment_mandate["payment_mandate_contents"]
                expected_payment_hash = hash_payment_mandate_contents(payment_contents)
                actual_payment_hash = payload.get("payment_hash")
                
                if actual_payment_hash != expected_payment_hash:
                    raise JWTValidationError(
                        "Payment hash mismatch - PaymentMandate may have been tampered with"
                    )
                
                return payload
            except jwt.DecodeError as e:
                raise JWTValidationError(f"Failed to decode JWT: {e}")
        
        # Verify signature with user's public key
        if not self.user_public_key:
            raise JWTValidationError("User public key not loaded. Cannot verify signature.")
        
        try:
            # Convert public key to PEM format for jwt library
            public_key_pem = self.user_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Decode and verify
            payload = jwt.decode(
                user_auth,
                public_key_pem,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                }
            )
            
            # Validate hashes match (non-repudiation)
            from .utils import hash_cart_mandate, hash_payment_mandate_contents
            
            expected_cart_hash = hash_cart_mandate(cart_mandate)
            actual_cart_hash = payload.get("cart_hash")
            
            if actual_cart_hash != expected_cart_hash:
                raise JWTValidationError(
                    "Cart hash mismatch - CartMandate may have been tampered with"
                )
            
            payment_contents = payment_mandate["payment_mandate_contents"]
            expected_payment_hash = hash_payment_mandate_contents(payment_contents)
            actual_payment_hash = payload.get("payment_hash")
            
            if actual_payment_hash != expected_payment_hash:
                raise JWTValidationError(
                    "Payment hash mismatch - PaymentMandate may have been tampered with"
                )
            
            print(f"✅ User authorization validated successfully")
            print(f"   Subject: {payload.get('sub')}")
            print(f"   Issued: {datetime.fromtimestamp(payload.get('iat'), tz=timezone.utc)}")
            print(f"   Expires: {datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc)}")
            print(f"   Cart hash: {actual_cart_hash[:16]}...")
            print(f"   Payment hash: {actual_payment_hash[:16]}...")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise JWTValidationError("User authorization has expired")
        except jwt.InvalidSignatureError:
            raise JWTValidationError("User authorization signature verification failed")
        except jwt.DecodeError as e:
            raise JWTValidationError(f"Failed to decode user authorization: {e}")
        except Exception as e:
            raise JWTValidationError(f"User authorization validation error: {e}")
    
    def reload_keys(self):
        """Reload public keys from disk (useful if keys were rotated)"""
        print("🔄 Reloading public keys...")
        self._load_keys()


# Global validator instance
_validator_instance = None


def get_jwt_validator() -> JWTValidator:
    """Get singleton JWT validator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = JWTValidator()
    return _validator_instance


# Convenience functions
def validate_merchant_signature(cart_mandate: Dict[str, Any], verify: bool = True) -> Dict[str, Any]:
    """Validate merchant signature on CartMandate"""
    validator = get_jwt_validator()
    return validator.validate_merchant_signature(cart_mandate, verify_signature=verify)


def validate_user_authorization(
    payment_mandate: Dict[str, Any],
    cart_mandate: Dict[str, Any],
    verify: bool = True
) -> Dict[str, Any]:
    """Validate user authorization on PaymentMandate"""
    validator = get_jwt_validator()
    return validator.validate_user_authorization(
        payment_mandate,
        cart_mandate,
        verify_signature=verify
    )

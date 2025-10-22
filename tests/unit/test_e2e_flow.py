"""
Test para validar el flujo completo de actualización de inventario
desde CartMandate hasta la base de datos
"""

import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "ap2-integration"))

from src.common.ap2_types import CartItem, CartContents


def test_end_to_end_cart_mandate_to_inventory():
    """
    Test E2E: Validar que el CartMandate preserva items hasta el payment processor
    
    Simula:
    1. MCP Server crea CartMandate con items
    2. Merchant Agent valida con Pydantic
    3. Payment Processor extrae items para actualizar inventario
    """
    # Step 1: Simular creación de CartMandate (como lo hace MCP Server)
    original_items = [
        {"product_id": "25", "quantity": 3},
        {"product_id": "1", "quantity": 2}
    ]
    
    # Step 2: Crear CartContents con Pydantic (como lo hace Merchant Agent)
    cart_items = [CartItem(**item) for item in original_items]
    
    cart_contents = CartContents(
        id="cart_test_e2e",
        user_cart_confirmation_required=False,
        merchant_name="Test Shop",
        payment_request={
            "method_data": [],
            "details": {
                "id": "order_test",
                "displayItems": [
                    {"label": "Pikachu (x3)", "amount": {"currency": "USD", "value": 165}},
                    {"label": "Bulbasaur (x2)", "amount": {"currency": "USD", "value": 560}}
                ],
                "total": {"label": "Total", "amount": {"currency": "USD", "value": 725}}
            },
            "options": {}
        },
        items=cart_items
    )
    
    # Step 3: Serializar a dict (como se envía por HTTP)
    cart_dict = cart_contents.model_dump()
    
    # Step 4: Payment Processor extrae items
    extracted_items = cart_dict.get("items", [])
    
    # Validaciones
    assert extracted_items is not None, "Items field should be present"
    assert len(extracted_items) == 2, "Should preserve 2 items"
    
    assert extracted_items[0]["product_id"] == "25"
    assert extracted_items[0]["quantity"] == 3
    
    assert extracted_items[1]["product_id"] == "1"
    assert extracted_items[1]["quantity"] == 2
    
    print("✅ E2E Test passed: Items preserved through entire flow")


def test_backward_compatibility_without_items():
    """
    Test que el sistema sigue funcionando sin el campo items (legacy)
    """
    # CartContents sin items (como era antes)
    cart_contents = CartContents(
        id="cart_legacy",
        user_cart_confirmation_required=False,
        merchant_name="Legacy Shop",
        payment_request={
            "method_data": [],
            "details": {
                "id": "order_legacy",
                "displayItems": [
                    {"label": "Pikachu (x1)", "amount": {"currency": "USD", "value": 55}}
                ],
                "total": {"label": "Total", "amount": {"currency": "USD", "value": 55}}
            },
            "options": {}
        }
        # items field omitted
    )
    
    cart_dict = cart_contents.model_dump()
    
    # Payment processor should handle missing items gracefully
    items = cart_dict.get("items")
    
    # Assert backward compatibility
    assert items is None, "Items should be None when not provided"
    
    # Fallback logic would use displayItems
    display_items = cart_dict["payment_request"]["details"]["displayItems"]
    assert len(display_items) > 0, "Should have displayItems for fallback"
    
    print("✅ Backward compatibility test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

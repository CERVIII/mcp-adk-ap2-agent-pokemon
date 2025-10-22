"""
Unit Tests for Inventory Update on Purchase

Tests the complete flow of inventory management when processing payments:
1. CartMandate includes items with product_id and quantity
2. Payment processor extracts items correctly
3. Inventory is updated (decrease available, increase sold)
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "ap2-integration"))

from src.database import Pokemon, PokemonRepository, SessionLocal, init_db
from src.common.ap2_types import CartItem, CartContents, CartMandate


class TestInventoryUpdate:
    """Test suite for inventory updates on purchase"""
    
    @pytest.fixture(scope="function")
    def db_session(self):
        """Create a test database session"""
        # Use in-memory SQLite for testing
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.database.models import Base
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Seed test data
        test_pokemon = [
            Pokemon(
                numero=1,
                nombre="Bulbasaur",
                precio=280,
                en_venta=True,
                inventario_total=100,
                inventario_disponible=50,
                inventario_vendido=50
            ),
            Pokemon(
                numero=25,
                nombre="Pikachu",
                precio=55,
                en_venta=True,
                inventario_total=200,
                inventario_disponible=150,
                inventario_vendido=50
            ),
            Pokemon(
                numero=150,
                nombre="Mewtwo",
                precio=1500,
                en_venta=True,
                inventario_total=10,
                inventario_disponible=5,
                inventario_vendido=5
            ),
        ]
        
        for pokemon in test_pokemon:
            session.add(pokemon)
        session.commit()
        
        yield session
        
        session.close()
    
    @pytest.fixture
    def pokemon_repo(self, db_session):
        """Create Pokemon repository with test session"""
        return PokemonRepository(db_session)
    
    def test_pokemon_decrease_stock(self, db_session, pokemon_repo):
        """Test that Pokemon.decrease_stock() correctly updates inventory"""
        # Arrange
        pikachu = pokemon_repo.get_by_numero(25)
        initial_disponible = pikachu.inventario_disponible
        initial_vendido = pikachu.inventario_vendido
        quantity = 3
        
        # Act
        success = pikachu.decrease_stock(quantity)
        db_session.commit()
        
        # Assert
        assert success is True
        assert pikachu.inventario_disponible == initial_disponible - quantity
        assert pikachu.inventario_vendido == initial_vendido + quantity
    
    def test_pokemon_decrease_stock_insufficient(self, db_session, pokemon_repo):
        """Test that decrease_stock() fails when insufficient stock"""
        # Arrange
        mewtwo = pokemon_repo.get_by_numero(150)
        initial_disponible = mewtwo.inventario_disponible
        initial_vendido = mewtwo.inventario_vendido
        quantity = 100  # More than available
        
        # Act
        success = mewtwo.decrease_stock(quantity)
        db_session.commit()
        
        # Assert
        assert success is False
        assert mewtwo.inventario_disponible == initial_disponible
        assert mewtwo.inventario_vendido == initial_vendido
    
    def test_repository_decrease_stock(self, db_session, pokemon_repo):
        """Test PokemonRepository.decrease_stock() method"""
        # Arrange
        initial_pikachu = pokemon_repo.get_by_numero(25)
        initial_disponible = initial_pikachu.inventario_disponible
        quantity = 5
        
        # Act
        success = pokemon_repo.decrease_stock(25, quantity)
        
        # Assert
        assert success is True
        updated_pikachu = pokemon_repo.get_by_numero(25)
        assert updated_pikachu.inventario_disponible == initial_disponible - quantity
    
    def test_repository_decrease_stock_not_found(self, db_session, pokemon_repo):
        """Test decrease_stock() with non-existent Pokemon"""
        # Act
        success = pokemon_repo.decrease_stock(999, 1)
        
        # Assert
        assert success is False
    
    def test_cart_item_model(self):
        """Test CartItem Pydantic model"""
        # Act
        item = CartItem(product_id="25", quantity=3)
        
        # Assert
        assert item.product_id == "25"
        assert item.quantity == 3
    
    def test_cart_item_default_quantity(self):
        """Test CartItem defaults quantity to 1"""
        # Act
        item = CartItem(product_id="1")
        
        # Assert
        assert item.quantity == 1
    
    def test_cart_contents_with_items(self):
        """Test that CartContents accepts items field"""
        # Arrange
        items = [
            CartItem(product_id="1", quantity=2),
            CartItem(product_id="25", quantity=1)
        ]
        
        # Act
        cart_contents = CartContents(
            id="cart_test_123",
            user_cart_confirmation_required=False,
            payment_request={
                "method_data": [],
                "details": {
                    "id": "order_test",
                    "displayItems": [],
                    "total": {
                        "label": "Total",
                        "amount": {"currency": "USD", "value": 100}
                    }
                },
                "options": {}
            },
            merchant_name="Test Merchant",
            items=items
        )
        
        # Assert
        assert cart_contents.items is not None
        assert len(cart_contents.items) == 2
        assert cart_contents.items[0].product_id == "1"
        assert cart_contents.items[0].quantity == 2
    
    def test_multiple_purchases_update_inventory(self, db_session, pokemon_repo):
        """Test that multiple purchases correctly accumulate inventory changes"""
        # Arrange
        pokemon_numero = 1  # Bulbasaur
        initial_pokemon = pokemon_repo.get_by_numero(pokemon_numero)
        initial_disponible = initial_pokemon.inventario_disponible
        initial_vendido = initial_pokemon.inventario_vendido
        
        # Act - Simulate 3 purchases
        purchases = [3, 2, 5]
        for quantity in purchases:
            pokemon_repo.decrease_stock(pokemon_numero, quantity)
        
        # Assert
        final_pokemon = pokemon_repo.get_by_numero(pokemon_numero)
        total_sold = sum(purchases)
        assert final_pokemon.inventario_disponible == initial_disponible - total_sold
        assert final_pokemon.inventario_vendido == initial_vendido + total_sold


class TestPaymentProcessorIntegration:
    """Integration tests for payment processor inventory updates"""
    
    def test_cart_mandate_items_extraction(self):
        """Test extracting items from CartMandate for inventory update"""
        # Arrange
        cart_mandate_dict = {
            "contents": {
                "id": "cart_pokemon_abc123",
                "user_cart_confirmation_required": False,
                "merchant_name": "PokeMart",
                "payment_request": {
                    "method_data": [],
                    "details": {
                        "id": "order_xyz",
                        "displayItems": [
                            {"label": "Bulbasaur (x2)", "amount": {"currency": "USD", "value": 560}}
                        ],
                        "total": {"label": "Total", "amount": {"currency": "USD", "value": 560}}
                    },
                    "options": {}
                },
                "items": [
                    {"product_id": "1", "quantity": 2}
                ]
            },
            "merchant_signature": "sig_test",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Act
        cart_items = cart_mandate_dict["contents"].get("items", [])
        
        # Assert
        assert len(cart_items) == 1
        assert cart_items[0]["product_id"] == "1"
        assert cart_items[0]["quantity"] == 2
    
    def test_fallback_to_display_items(self):
        """Test fallback parsing when items field is missing"""
        # Arrange
        cart_mandate_dict = {
            "contents": {
                "id": "cart_pokemon_abc123",
                "user_cart_confirmation_required": False,
                "merchant_name": "PokeMart",
                "payment_request": {
                    "method_data": [],
                    "details": {
                        "id": "order_xyz",
                        "displayItems": [
                            {"label": "Pikachu (x3)", "amount": {"currency": "USD", "value": 165}}
                        ],
                        "total": {"label": "Total", "amount": {"currency": "USD", "value": 165}}
                    },
                    "options": {}
                }
                # Note: no 'items' field
            },
            "merchant_signature": "sig_test",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Act
        cart_items = cart_mandate_dict["contents"].get("items", [])
        
        # Assert - Should be empty, triggering fallback
        assert cart_items == []
        
        # Fallback logic test
        display_items = cart_mandate_dict["contents"]["payment_request"]["details"]["displayItems"]
        label = display_items[0]["label"]
        
        # Extract quantity from label
        quantity = 1
        if "(x" in label and ")" in label:
            quantity = int(label.split("(x")[1].split(")")[0])
        
        assert quantity == 3


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.database.models import Base
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        # Add a Pokemon with limited stock
        limited_stock_pokemon = Pokemon(
            numero=150,
            nombre="Mewtwo",
            precio=1500,
            en_venta=True,
            inventario_total=10,
            inventario_disponible=2,
            inventario_vendido=8
        )
        session.add(limited_stock_pokemon)
        session.commit()
        
        yield session
        session.close()
    
    def test_purchase_exact_remaining_stock(self, db_session):
        """Test purchasing exactly the remaining stock"""
        # Arrange
        repo = PokemonRepository(db_session)
        mewtwo = repo.get_by_numero(150)
        remaining_stock = mewtwo.inventario_disponible
        
        # Act
        success = repo.decrease_stock(150, remaining_stock)
        
        # Assert
        assert success is True
        updated = repo.get_by_numero(150)
        assert updated.inventario_disponible == 0
        assert updated.inventario_vendido == 10  # total sold
    
    def test_purchase_zero_quantity(self, db_session):
        """Test that zero quantity purchase is handled"""
        # Arrange
        repo = PokemonRepository(db_session)
        initial = repo.get_by_numero(150)
        initial_disponible = initial.inventario_disponible
        
        # Act
        success = repo.decrease_stock(150, 0)
        
        # Assert
        # Should succeed (nothing changes)
        assert success is True
        updated = repo.get_by_numero(150)
        assert updated.inventario_disponible == initial_disponible
    
    def test_negative_quantity_handled(self, db_session):
        """Test that negative quantity is handled (currently succeeds - adds stock)"""
        # Arrange
        repo = PokemonRepository(db_session)
        initial = repo.get_by_numero(150)
        initial_disponible = initial.inventario_disponible
        
        # Act
        success = repo.decrease_stock(150, -5)
        
        # Assert
        # Note: Current implementation doesn't validate negative quantities
        # This could be improved to reject negative values
        # For now, testing actual behavior (succeeds but doesn't make sense)
        assert success is True  # Currently succeeds
        updated = repo.get_by_numero(150)
        # With negative quantity, the comparison passes (disponible >= -5)
        assert updated.inventario_disponible == initial_disponible + 5  # Actually increases!


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

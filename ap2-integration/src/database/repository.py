"""
Repository pattern for database access

Provides clean interface for CRUD operations on Pokemon and Transactions.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from .models import Pokemon, Transaction, TransactionItem, Cart, CartItem


class PokemonRepository:
    """Repository for Pokemon catalog and inventory operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 151) -> List[Pokemon]:
        """Get all Pokemon with pagination"""
        return self.db.query(Pokemon).offset(skip).limit(limit).all()
    
    def get_by_numero(self, numero: int) -> Optional[Pokemon]:
        """Get Pokemon by numero"""
        return self.db.query(Pokemon).filter(Pokemon.numero == numero).first()
    
    def get_by_nombre(self, nombre: str) -> Optional[Pokemon]:
        """Get Pokemon by nombre"""
        return self.db.query(Pokemon).filter(
            Pokemon.nombre == nombre.lower()
        ).first()
    
    def get_available(self) -> List[Pokemon]:
        """Get all Pokemon available for sale"""
        return self.db.query(Pokemon).filter(
            Pokemon.en_venta == True,
            Pokemon.inventario_disponible > 0
        ).all()
    
    def search(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        only_available: bool = False,
        limit: int = 151
    ) -> List[Pokemon]:
        """Search Pokemon with filters"""
        query = self.db.query(Pokemon)
        
        if min_price is not None:
            query = query.filter(Pokemon.precio >= min_price)
        
        if max_price is not None:
            query = query.filter(Pokemon.precio <= max_price)
        
        if only_available:
            query = query.filter(
                Pokemon.en_venta == True,
                Pokemon.inventario_disponible > 0
            )
        
        return query.limit(limit).all()
    
    def decrease_stock(self, numero: int, quantity: int) -> bool:
        """
        Decrease stock for a Pokemon.
        
        Returns:
            True if successful, False if insufficient stock
        """
        pokemon = self.get_by_numero(numero)
        if not pokemon:
            return False
        
        success = pokemon.decrease_stock(quantity)
        if success:
            self.db.commit()
        
        return success
    
    def increase_stock(self, numero: int, quantity: int):
        """Increase stock for a Pokemon (e.g., for refunds)"""
        pokemon = self.get_by_numero(numero)
        if pokemon:
            pokemon.increase_stock(quantity)
            self.db.commit()
    
    def get_inventory_stats(self) -> Dict[str, Any]:
        """Get inventory statistics"""
        total_pokemon = self.db.query(Pokemon).count()
        available_pokemon = self.db.query(Pokemon).filter(
            Pokemon.en_venta == True,
            Pokemon.inventario_disponible > 0
        ).count()
        total_stock = self.db.query(
            func.sum(Pokemon.inventario_disponible)
        ).scalar() or 0
        total_sold = self.db.query(
            func.sum(Pokemon.inventario_vendido)
        ).scalar() or 0
        
        return {
            "total_pokemon": total_pokemon,
            "available_pokemon": available_pokemon,
            "total_stock": total_stock,
            "total_sold": total_sold,
        }


class TransactionRepository:
    """Repository for Transaction operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        transaction_id: str,
        cart_id: str,
        cart_mandate: Dict[str, Any],
        payment_mandate: Dict[str, Any],
        items: List[Dict[str, Any]],
        status: str = "completed"
    ) -> Transaction:
        """
        Create a new transaction with items.
        
        Args:
            transaction_id: Unique transaction identifier
            cart_id: Cart identifier
            cart_mandate: Complete CartMandate dict
            payment_mandate: Complete PaymentMandate dict
            items: List of items with pokemon_numero, quantity, unit_price
            status: Transaction status (default: completed)
        
        Returns:
            Created Transaction object
        """
        # Extract info from mandates
        payment_details = cart_mandate["contents"]["payment_request"]["details"]
        total_amount = payment_details["total"]["amount"]["value"]
        currency = payment_details["total"]["amount"]["currency"]
        
        payment_response = payment_mandate["payment_mandate_contents"]["payment_response"]
        payment_method = payment_response["method_name"]
        payer_email = payment_response.get("payer_email")
        
        merchant_name = cart_mandate.get("merchantName")
        merchant_signature = cart_mandate.get("merchant_signature")
        user_authorization = payment_mandate.get("user_authorization")
        
        # Create transaction
        transaction = Transaction(
            transaction_id=transaction_id,
            cart_id=cart_id,
            status=status,
            total_amount=total_amount,
            currency=currency,
            payment_method=payment_method,
            payer_email=payer_email,
            cart_mandate=cart_mandate,
            payment_mandate=payment_mandate,
            merchant_name=merchant_name,
            merchant_signature=merchant_signature,
            user_authorization=user_authorization,
            completed_at=datetime.now(timezone.utc) if status == "completed" else None
        )
        
        self.db.add(transaction)
        self.db.flush()  # Get transaction.id
        
        # Create transaction items
        for item in items:
            pokemon_repo = PokemonRepository(self.db)
            pokemon = pokemon_repo.get_by_numero(item["pokemon_numero"])
            
            if not pokemon:
                raise ValueError(f"Pokemon #{item['pokemon_numero']} not found")
            
            transaction_item = TransactionItem(
                transaction_id=transaction.id,
                pokemon_numero=item["pokemon_numero"],
                pokemon_name=pokemon.nombre,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                total_price=item["quantity"] * item["unit_price"]
            )
            
            self.db.add(transaction_item)
            
            # Decrease stock
            pokemon_repo.decrease_stock(pokemon.numero, item["quantity"])
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Transaction]:
        """Get all transactions with pagination"""
        query = self.db.query(Transaction).order_by(desc(Transaction.created_at))
        
        if status:
            query = query.filter(Transaction.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        total_transactions = self.db.query(Transaction).count()
        completed_transactions = self.db.query(Transaction).filter(
            Transaction.status == "completed"
        ).count()
        total_revenue = self.db.query(
            func.sum(Transaction.total_amount)
        ).filter(Transaction.status == "completed").scalar() or 0.0
        
        avg_transaction = (
            total_revenue / completed_transactions
            if completed_transactions > 0
            else 0.0
        )
        
        return {
            "total_transactions": total_transactions,
            "completed_transactions": completed_transactions,
            "total_revenue": total_revenue,
            "average_transaction": avg_transaction,
        }


class CartRepository:
    """Repository for shopping cart operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_cart(self, session_id: str, user_id: Optional[str] = None, hours_to_expire: int = 24) -> Cart:
        """Create a new cart"""
        from datetime import timedelta
        
        cart = Cart(
            session_id=session_id,
            user_id=user_id,
            status="active",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=hours_to_expire)
        )
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart
    
    def get_cart_by_session(self, session_id: str) -> Optional[Cart]:
        """Get cart by session ID"""
        return self.db.query(Cart).filter(
            Cart.session_id == session_id,
            Cart.status == "active"
        ).first()
    
    def get_or_create_cart(self, session_id: str, user_id: Optional[str] = None) -> Cart:
        """Get existing cart or create new one"""
        cart = self.get_cart_by_session(session_id)
        
        if cart:
            # Check if expired
            if cart.is_expired():
                cart.status = "expired"
                self.db.commit()
                # Create new cart
                return self.create_cart(session_id, user_id)
            return cart
        
        return self.create_cart(session_id, user_id)
    
    def add_item(
        self,
        cart: Cart,
        pokemon: Pokemon,
        quantity: int = 1
    ) -> CartItem:
        """Add item to cart or update quantity if already exists"""
        # Check if item already in cart
        existing_item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.pokemon_numero == pokemon.numero
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.update_quantity(existing_item.quantity + quantity)
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item
        
        # Create new item
        item = CartItem(
            cart_id=cart.id,
            pokemon_numero=pokemon.numero,
            pokemon_name=pokemon.nombre,
            quantity=quantity,
            unit_price=float(pokemon.precio),
            total_price=float(pokemon.precio) * quantity
        )
        self.db.add(item)
        
        # Update cart timestamp
        cart.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def update_item_quantity(self, item_id: int, quantity: int) -> Optional[CartItem]:
        """Update item quantity"""
        item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        
        if not item:
            return None
        
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            self.db.delete(item)
            self.db.commit()
            return None
        
        item.update_quantity(quantity)
        
        # Update cart timestamp
        cart = item.cart
        cart.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def remove_item(self, item_id: int) -> bool:
        """Remove item from cart"""
        item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        
        if not item:
            return False
        
        # Update cart timestamp before deleting
        cart = item.cart
        cart.updated_at = datetime.now(timezone.utc)
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    def clear_cart(self, cart_id: int) -> bool:
        """Remove all items from cart"""
        cart = self.db.query(Cart).filter(Cart.id == cart_id).first()
        
        if not cart:
            return False
        
        # Delete all items
        self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        
        # Update cart timestamp
        cart.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        return True
    
    def mark_cart_as_checkout(self, cart_id: int) -> Optional[Cart]:
        """Mark cart as in checkout process"""
        cart = self.db.query(Cart).filter(Cart.id == cart_id).first()
        
        if not cart:
            return None
        
        cart.status = "checkout"
        cart.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(cart)
        return cart
    
    def mark_cart_as_completed(self, cart_id: int) -> Optional[Cart]:
        """Mark cart as completed (after successful payment)"""
        cart = self.db.query(Cart).filter(Cart.id == cart_id).first()
        
        if not cart:
            return None
        
        cart.status = "completed"
        cart.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(cart)
        return cart
    
    def expire_old_carts(self, hours: int = 24) -> int:
        """Expire carts older than specified hours"""
        from datetime import timedelta
        
        # Use naive datetime for SQLite compatibility
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Convert to naive datetime for comparison with SQLite
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        
        expired_count = self.db.query(Cart).filter(
            Cart.status == "active",
            Cart.expires_at < now_naive
        ).update({"status": "expired"}, synchronize_session=False)
        
        self.db.commit()
        return expired_count
    
    def get_cart_stats(self) -> Dict[str, Any]:
        """Get cart statistics"""
        total_carts = self.db.query(func.count(Cart.id)).scalar()
        active_carts = self.db.query(func.count(Cart.id)).filter(
            Cart.status == "active"
        ).scalar()
        abandoned_carts = self.db.query(func.count(Cart.id)).filter(
            Cart.status == "abandoned"
        ).scalar()
        completed_carts = self.db.query(func.count(Cart.id)).filter(
            Cart.status == "completed"
        ).scalar()
        
        return {
            "total_carts": total_carts,
            "active_carts": active_carts,
            "abandoned_carts": abandoned_carts,
            "completed_carts": completed_carts,
        }

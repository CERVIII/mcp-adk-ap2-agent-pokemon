"""
SQLAlchemy models for Pokemon marketplace

Models:
- Pokemon: Catalog and inventory
- Transaction: Purchase history
- TransactionItem: Items in each transaction
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

# Base class for all models
Base = declarative_base()


class Pokemon(Base):
    """
    Pokemon catalog and inventory.
    
    Replaces pokemon-gen1.json with database storage.
    """
    __tablename__ = "pokemon"
    
    # Primary key
    numero = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    precio = Column(Integer, nullable=False)  # Price in USD (integer)
    
    # Inventory
    en_venta = Column(Boolean, default=True, nullable=False)
    inventario_total = Column(Integer, default=0, nullable=False)
    inventario_disponible = Column(Integer, default=0, nullable=False)
    inventario_vendido = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    transaction_items = relationship("TransactionItem", back_populates="pokemon")
    
    def __repr__(self):
        return f"<Pokemon {self.numero}: {self.nombre} (${self.precio})>"
    
    def to_dict(self):
        """Convert to dictionary (compatible with JSON format)"""
        return {
            "numero": self.numero,
            "nombre": self.nombre,
            "precio": self.precio,
            "enVenta": self.en_venta,
            "inventario": {
                "total": self.inventario_total,
                "disponibles": self.inventario_disponible,
                "vendidos": self.inventario_vendido,
            }
        }
    
    def decrease_stock(self, quantity: int) -> bool:
        """
        Decrease available stock.
        
        Returns:
            True if successful, False if insufficient stock
        """
        if self.inventario_disponible >= quantity:
            self.inventario_disponible -= quantity
            self.inventario_vendido += quantity
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False
    
    def increase_stock(self, quantity: int):
        """Increase available stock (e.g., for refunds)"""
        self.inventario_disponible += quantity
        self.inventario_vendido = max(0, self.inventario_vendido - quantity)
        self.updated_at = datetime.now(timezone.utc)


class Transaction(Base):
    """
    Transaction/purchase history.
    
    Stores complete AP2 payment flow results.
    """
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Transaction identifiers
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    cart_id = Column(String(100), nullable=False, index=True)
    payment_id = Column(String(100), index=True)
    
    # Status
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True
    )  # pending, completed, failed, refunded
    
    # Amounts
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Payment info
    payment_method = Column(String(50))
    payer_email = Column(String(255))
    
    # AP2 Mandates (stored as JSON)
    cart_mandate = Column(JSON)
    payment_mandate = Column(JSON)
    
    # Merchant/Agent info
    merchant_name = Column(String(100))
    merchant_signature = Column(Text)  # JWT signature
    user_authorization = Column(Text)  # JWT signature
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    items = relationship(
        "TransactionItem",
        back_populates="transaction",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (
            f"<Transaction {self.transaction_id}: "
            f"{self.status} ${self.total_amount}>"
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "cart_id": self.cart_id,
            "payment_id": self.payment_id,
            "status": self.status,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "payer_email": self.payer_email,
            "merchant_name": self.merchant_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "items": [item.to_dict() for item in self.items],
        }


class TransactionItem(Base):
    """
    Individual items in a transaction.
    
    Links transactions to specific Pokemon with quantities.
    """
    __tablename__ = "transaction_items"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    transaction_id = Column(
        Integer,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    pokemon_numero = Column(
        Integer,
        ForeignKey("pokemon.numero", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Item details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)  # Price at time of purchase
    total_price = Column(Float, nullable=False)  # quantity * unit_price
    
    # Pokemon name (denormalized for faster queries)
    pokemon_name = Column(String(50), nullable=False)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="items")
    pokemon = relationship("Pokemon", back_populates="transaction_items")
    
    def __repr__(self):
        return (
            f"<TransactionItem: {self.pokemon_name} "
            f"x{self.quantity} @ ${self.unit_price}>"
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "pokemon_numero": self.pokemon_numero,
            "pokemon_name": self.pokemon_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
        }


class Cart(Base):
    """
    Shopping cart for persistent cart storage.
    
    Stores active shopping carts with session tracking and expiration.
    Allows multiple carts per session (for completed/expired carts history).
    """
    __tablename__ = "carts"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Session tracking
    # NOTE: Removed unique=True to allow multiple carts per session (completed, expired, etc.)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), index=True)  # Optional: for authenticated users
    
    # Status
    status = Column(
        String(20),
        nullable=False,
        default="active",
        index=True
    )  # active, checkout, abandoned, expired, completed
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )  # Auto-expire after 24 hours
    
    # Relationships
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Cart {self.session_id}: {self.status} ({len(self.items)} items)>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "items": [item.to_dict() for item in self.items],
            "total_items": len(self.items),
            "total_amount": sum(item.total_price for item in self.items),
        }
    
    def is_expired(self) -> bool:
        """Check if cart has expired"""
        # Ensure expires_at has timezone info
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at
    
    def extend_expiration(self, hours: int = 24):
        """Extend cart expiration by specified hours"""
        from datetime import timedelta
        self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        self.updated_at = datetime.now(timezone.utc)


class CartItem(Base):
    """
    Individual items in a shopping cart.
    
    Links carts to specific Pokemon with quantities and price snapshots.
    """
    __tablename__ = "cart_items"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    cart_id = Column(
        Integer,
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    pokemon_numero = Column(
        Integer,
        ForeignKey("pokemon.numero", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Item details
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)  # Price snapshot at add time
    total_price = Column(Float, nullable=False)  # quantity * unit_price
    
    # Pokemon name (denormalized for faster queries)
    pokemon_name = Column(String(50), nullable=False)
    
    # Timestamps
    added_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    pokemon = relationship("Pokemon")
    
    def __repr__(self):
        return (
            f"<CartItem: {self.pokemon_name} "
            f"x{self.quantity} @ ${self.unit_price}>"
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "pokemon_numero": self.pokemon_numero,
            "pokemon_name": self.pokemon_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "added_at": self.added_at.isoformat() if self.added_at else None,
        }
    
    def update_quantity(self, new_quantity: int):
        """Update item quantity and recalculate total"""
        self.quantity = new_quantity
        self.total_price = self.quantity * self.unit_price
        self.updated_at = datetime.now(timezone.utc)

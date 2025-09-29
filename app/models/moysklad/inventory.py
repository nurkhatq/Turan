# app/models/moysklad/inventory.py (FIXED VERSION)
from sqlalchemy import Boolean, Column, String, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..base import BaseModel, ExternalIdMixin


class Store(BaseModel, ExternalIdMixin):
    """Store/warehouse from MoySklad."""
    __tablename__ = "store"
    
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    stock_items = relationship("Stock", back_populates="store")


class Stock(BaseModel, ExternalIdMixin):
    """Stock levels from MoySklad with fixed external ID relationships."""
    __tablename__ = "stock"
    
    # Quantities
    stock = Column(Numeric(15, 3), default=0, nullable=False)  # Current stock
    in_transit = Column(Numeric(15, 3), default=0, nullable=False)  # In transit
    reserve = Column(Numeric(15, 3), default=0, nullable=False)  # Reserved
    available = Column(Numeric(15, 3), default=0, nullable=False)  # Available
    
    # Pricing from stock report
    price = Column(Numeric(15, 2), nullable=True)  # Current price
    sale_price = Column(Numeric(15, 2), nullable=True)  # Sale price
    
    # FIXED: Use external IDs for relationships
    product_external_id = Column(String(255), nullable=True, index=True)
    variant_external_id = Column(String(255), nullable=True, index=True)
    store_external_id = Column(String(255), nullable=True, index=True)  # Made nullable
    
    # Foreign keys for actual relationships (populated after sync)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=True)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="stock_items")
    variant = relationship("ProductVariant", back_populates="stock_items")
    store = relationship("Store", back_populates="stock_items")
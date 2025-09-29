# app/models/moysklad/products.py (FIXED VERSION)
from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..base import BaseModel, ExternalIdMixin


class ProductFolder(BaseModel, ExternalIdMixin):
    """Product folder/category from MoySklad."""
    __tablename__ = "product_folder"
    
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    path_name = Column(String(500), nullable=True)  # Full path name from MoySklad
    archived = Column(Boolean, default=False, nullable=False)
    
    # Parent-child relationship using external IDs
    parent_external_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    products = relationship("Product", back_populates="folder")


class UnitOfMeasure(BaseModel, ExternalIdMixin):
    """Unit of measure from MoySklad."""
    __tablename__ = "unit_of_measure"
    
    name = Column(String(255), nullable=False)
    code = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)


class Product(BaseModel, ExternalIdMixin):
    """Product from MoySklad with fixed external ID relationships."""
    __tablename__ = "product"
    
    name = Column(String(500), nullable=False, index=True)
    code = Column(String(255), nullable=True, index=True)
    article = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Pricing
    sale_price = Column(Numeric(15, 2), nullable=True)
    buy_price = Column(Numeric(15, 2), nullable=True)
    min_price = Column(Numeric(15, 2), nullable=True)
    
    # Product properties
    weight = Column(Numeric(10, 3), nullable=True)
    volume = Column(Numeric(10, 3), nullable=True)
    
    # Status flags
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # FIXED: Use external IDs instead of integer foreign keys
    folder_external_id = Column(String(255), nullable=True, index=True)
    unit_external_id = Column(String(255), nullable=True, index=True)
    supplier_external_id = Column(String(255), nullable=True, index=True)
    
    # FIXED: Use integer foreign keys for actual relationships (will be populated after sync)
    folder_id = Column(Integer, ForeignKey("product_folder.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("unit_of_measure.id"), nullable=True)
    
    # Relationships
    folder = relationship("ProductFolder", back_populates="products")
    unit = relationship("UnitOfMeasure")
    variants = relationship("ProductVariant", back_populates="product")
    stock_items = relationship("Stock", back_populates="product")


class ProductVariant(BaseModel, ExternalIdMixin):
    """Product variant from MoySklad."""
    __tablename__ = "product_variant"
    
    name = Column(String(500), nullable=False)
    code = Column(String(255), nullable=True)
    
    # Pricing
    sale_price = Column(Numeric(15, 2), nullable=True)
    buy_price = Column(Numeric(15, 2), nullable=True)
    
    # Characteristics (stored as JSON)
    characteristics = Column(Text, nullable=True)  # JSON with variant characteristics
    
    # FIXED: Use external ID for product relationship
    product_external_id = Column(String(255), nullable=False, index=True)
    
    # Foreign keys
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    stock_items = relationship("Stock", back_populates="variant")


class Service(BaseModel, ExternalIdMixin):
    """Service from MoySklad."""
    __tablename__ = "service"
    
    name = Column(String(500), nullable=False)
    code = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Pricing
    sale_price = Column(Numeric(15, 2), nullable=True)
    buy_price = Column(Numeric(15, 2), nullable=True)
    min_price = Column(Numeric(15, 2), nullable=True)
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # FIXED: Use external IDs
    folder_external_id = Column(String(255), nullable=True, index=True)
    unit_external_id = Column(String(255), nullable=True, index=True)
    
    # Foreign keys for relationships
    folder_id = Column(Integer, ForeignKey("product_folder.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("unit_of_measure.id"), nullable=True)
    
    # Relationships
    folder = relationship("ProductFolder")
    unit = relationship("UnitOfMeasure")
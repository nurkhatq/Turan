from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ..base import BaseModel, ExternalIdMixin


class SalesDocument(BaseModel, ExternalIdMixin):
    """Sales documents (orders, invoices, etc.) from MoySklad."""
    __tablename__ = "sales_document"
    
    # Document info
    document_type = Column(String(50), nullable=False)  # order, invoice, shipment, etc.
    name = Column(String(255), nullable=False)
    number = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Dates
    moment = Column(DateTime, nullable=False, default=datetime.utcnow)
    applicable = Column(Boolean, default=True, nullable=False)
    
    # Financial data
    sum_total = Column(Numeric(15, 2), default=0, nullable=False)
    vat_enabled = Column(Boolean, default=True, nullable=False)
    vat_included = Column(Boolean, default=True, nullable=False)
    vat_sum = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Status
    state = Column(String(100), nullable=True)  # Document state
    shared = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    counterparty_id = Column(Integer, ForeignKey("counterparty.id"), nullable=True)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=True)
    
    # Relationships
    counterparty = relationship("Counterparty", back_populates="sales_documents")
    store = relationship("Store")
    positions = relationship("SalesDocumentPosition", back_populates="document")


class SalesDocumentPosition(BaseModel, ExternalIdMixin):
    """Sales document line items."""
    __tablename__ = "sales_document_position"
    
    quantity = Column(Numeric(15, 3), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    discount = Column(Numeric(5, 2), default=0, nullable=False)
    vat = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Foreign keys
    document_id = Column(Integer, ForeignKey("sales_document.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=True)
    
    # Relationships
    document = relationship("SalesDocument", back_populates="positions")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    service = relationship("Service")


class PurchaseDocument(BaseModel, ExternalIdMixin):
    """Purchase documents from MoySklad."""
    __tablename__ = "purchase_document"
    
    # Document info
    document_type = Column(String(50), nullable=False)  # order, invoice, supply, etc.
    name = Column(String(255), nullable=False)
    number = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Dates
    moment = Column(DateTime, nullable=False, default=datetime.utcnow)
    applicable = Column(Boolean, default=True, nullable=False)
    
    # Financial data
    sum_total = Column(Numeric(15, 2), default=0, nullable=False)
    vat_enabled = Column(Boolean, default=True, nullable=False)
    vat_included = Column(Boolean, default=True, nullable=False)
    vat_sum = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Status
    state = Column(String(100), nullable=True)
    shared = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    counterparty_id = Column(Integer, ForeignKey("counterparty.id"), nullable=True)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=True)
    
    # Relationships
    counterparty = relationship("Counterparty", back_populates="purchase_documents")
    store = relationship("Store")
    positions = relationship("PurchaseDocumentPosition", back_populates="document")


class PurchaseDocumentPosition(BaseModel, ExternalIdMixin):
    """Purchase document line items."""
    __tablename__ = "purchase_document_position"
    
    quantity = Column(Numeric(15, 3), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    discount = Column(Numeric(5, 2), default=0, nullable=False)
    vat = Column(Numeric(5, 2), default=0, nullable=False)
    
    # Foreign keys
    document_id = Column(Integer, ForeignKey("purchase_document.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variant.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=True)
    
    # Relationships
    document = relationship("PurchaseDocument", back_populates="positions")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    service = relationship("Service")

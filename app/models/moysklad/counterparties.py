# app/models/moysklad/counterparties.py (Updated)
"""Counterparty models with contract relationship."""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..base import BaseModel, ExternalIdMixin


class Counterparty(BaseModel, ExternalIdMixin):
    """Counterparty (customer/supplier) from MoySklad."""
    __tablename__ = "counterparty"
    
    # Basic info
    name = Column(String(500), nullable=False, index=True)
    code = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Contact info
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    
    # Legal info
    legal_title = Column(String(500), nullable=True)
    legal_address = Column(Text, nullable=True)
    actual_address = Column(Text, nullable=True)
    
    # Tax identifiers
    inn = Column(String(12), nullable=True, index=True)
    kpp = Column(String(9), nullable=True)
    ogrn = Column(String(15), nullable=True)
    okpo = Column(String(10), nullable=True)
    
    # Type flags
    is_supplier = Column(Boolean, default=False, nullable=False)
    is_customer = Column(Boolean, default=True, nullable=False)
    
    # Financial
    discount_percentage = Column(Numeric(5, 2), default=0, nullable=False)
    bonus_points = Column(Integer, default=0, nullable=False)
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # Default contract (optional)
    default_contract_id = Column(Integer, ForeignKey("contract.id"), nullable=True)
    
    # Relationships
    sales_documents = relationship("SalesDocument", back_populates="counterparty")
    purchase_documents = relationship("PurchaseDocument", back_populates="counterparty")
    contracts = relationship("Contract", 
                           foreign_keys="Contract.counterparty_id",
                           back_populates="counterparty",
                           post_update=True)
    default_contract = relationship("Contract", 
                                  foreign_keys=[default_contract_id],
                                  post_update=True)  # Avoid circular dependency
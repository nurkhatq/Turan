# app/models/moysklad/counterparties.py
from sqlalchemy import Column, String, Text, Boolean, Numeric
from sqlalchemy.orm import relationship

from ..base import BaseModel, ExternalIdMixin


class Counterparty(BaseModel, ExternalIdMixin):
    """Counterparty (customer/supplier) from MoySklad."""
    __tablename__ = "counterparty"
    
    name = Column(String(500), nullable=False, index=True)
    code = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    fax = Column(String(100), nullable=True)
    
    # Legal information
    legal_title = Column(String(500), nullable=True)
    legal_address = Column(Text, nullable=True)
    actual_address = Column(Text, nullable=True)
    inn = Column(String(20), nullable=True)  # Tax ID
    kpp = Column(String(20), nullable=True)  # Tax registration reason code
    ogrn = Column(String(20), nullable=True)  # Primary state registration number
    okpo = Column(String(20), nullable=True)  # All-Russian classifier of enterprises
    
    # Financial information
    account_number = Column(String(50), nullable=True)
    bank_name = Column(String(255), nullable=True)
    bik = Column(String(20), nullable=True)  # Bank identification code
    correspondent_account = Column(String(50), nullable=True)
    
    # Business properties
    is_supplier = Column(Boolean, default=False, nullable=False)
    is_customer = Column(Boolean, default=True, nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    sales_documents = relationship("SalesDocument", back_populates="counterparty")
    purchase_documents = relationship("PurchaseDocument", back_populates="counterparty")

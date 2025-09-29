# app/models/moysklad/organizations.py
"""MoySklad organization entities."""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..base import BaseModel, ExternalIdMixin


class Organization(BaseModel, ExternalIdMixin):
    """Organization (company) from MoySklad."""
    __tablename__ = "organization"
    
    # Basic info
    name = Column(String(500), nullable=False, index=True)
    code = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Legal info
    legal_title = Column(String(500), nullable=True)
    legal_address = Column(Text, nullable=True)
    actual_address = Column(Text, nullable=True)
    
    # Tax info
    inn = Column(String(12), nullable=True, index=True)
    kpp = Column(String(9), nullable=True)
    ogrn = Column(String(15), nullable=True)
    okpo = Column(String(10), nullable=True)
    
    # Contact info
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    fax = Column(String(50), nullable=True)
    
    # Bank details
    bank_accounts = Column(JSON, nullable=True)  # Store as JSON for flexibility
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # Chief accountant
    chief_accountant_external_id = Column(String(255), nullable=True)
    
    # Relationships
    employees = relationship("Employee", back_populates="organization")


class Employee(BaseModel, ExternalIdMixin):
    """Employee from MoySklad."""
    __tablename__ = "employee"
    
    # Personal info
    first_name = Column(String(255), nullable=True)
    middle_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=False)
    full_name = Column(String(500), nullable=False, index=True)
    
    # Work info
    position = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True, index=True)
    
    # Contact info
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    
    # Permissions
    permissions_data = Column(JSON, nullable=True)  # Store permissions as JSON
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # Cashier info (for retail)
    retail_store_external_id = Column(String(255), nullable=True)
    cashier_inn = Column(String(12), nullable=True)
    
    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    organization_external_id = Column(String(255), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="employees")
    projects = relationship("EmployeeProject", back_populates="employee")


class Project(BaseModel, ExternalIdMixin):
    """Project from MoySklad."""
    __tablename__ = "project"
    
    name = Column(String(500), nullable=False, index=True)
    code = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    employees = relationship("EmployeeProject", back_populates="project")
    contracts = relationship("Contract", back_populates="project")


class EmployeeProject(BaseModel):
    """Many-to-many relationship between employees and projects."""
    __tablename__ = "employee_project"
    
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    role = Column(String(100), nullable=True)  # Role in project
    
    # Relationships
    employee = relationship("Employee", back_populates="projects")
    project = relationship("Project", back_populates="employees")


class Contract(BaseModel, ExternalIdMixin):
    """Contract from MoySklad."""
    __tablename__ = "contract"
    
    # Contract info
    name = Column(String(500), nullable=False, index=True)
    code = Column(String(255), nullable=True, index=True)
    number = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Dates
    moment = Column(DateTime, nullable=False, default=datetime.utcnow)
    contract_date = Column(DateTime, nullable=True)
    
    # Type
    contract_type = Column(String(50), nullable=False, default="sales")  # sales, commission
    
    # Financial
    sum_amount = Column(Numeric(15, 2), default=0, nullable=False)
    reward_percent = Column(Numeric(5, 2), nullable=True)  # For commission contracts
    reward_type = Column(String(50), nullable=True)  # percentOfSales, none
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)
    shared = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys - using external IDs first, then resolved to actual IDs
    counterparty_external_id = Column(String(255), nullable=True)
    counterparty_id = Column(Integer, ForeignKey("counterparty.id"), nullable=True)
    
    organization_external_id = Column(String(255), nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    
    project_external_id = Column(String(255), nullable=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    
    # Relationships
    counterparty = relationship("Counterparty", 
                             foreign_keys=[counterparty_id],
                             back_populates="contracts",
                             post_update=True)
    organization = relationship("Organization", 
                              foreign_keys=[organization_id])
    project = relationship("Project", 
                         foreign_keys=[project_id],
                         back_populates="contracts")


class Currency(BaseModel, ExternalIdMixin):
    """Currency from MoySklad."""
    __tablename__ = "currency"
    
    name = Column(String(255), nullable=False)
    full_name = Column(String(500), nullable=True)
    code = Column(String(3), nullable=False, unique=True, index=True)  # ISO code
    iso_code = Column(String(3), nullable=True)
    
    # Settings
    is_default = Column(Boolean, default=False, nullable=False)
    is_indirect = Column(Boolean, default=False, nullable=False)
    multiplicity = Column(Integer, default=1, nullable=False)
    rate = Column(Numeric(20, 10), default=1, nullable=False)
    
    # Minor units
    minor_units = Column(JSON, nullable=True)  # Store minor unit settings as JSON
    
    # Status
    archived = Column(Boolean, default=False, nullable=False)


class PriceType(BaseModel, ExternalIdMixin):
    """Price type from MoySklad."""
    __tablename__ = "price_type"
    
    name = Column(String(255), nullable=False, unique=True)
    external_code = Column(String(255), nullable=True)
    
    # Settings
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Currency
    currency_external_id = Column(String(255), nullable=True)
    currency_id = Column(Integer, ForeignKey("currency.id"), nullable=True)
    
    # Relationship
    currency = relationship("Currency", 
                          foreign_keys=[currency_id])


class Country(BaseModel, ExternalIdMixin):
    """Country from MoySklad."""
    __tablename__ = "country"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(10), nullable=True, unique=True, index=True)
    external_code = Column(String(10), nullable=True)
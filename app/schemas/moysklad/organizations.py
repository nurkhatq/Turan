# app/schemas/moysklad/organizations.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from decimal import Decimal
from datetime import datetime


class OrganizationResponse(BaseModel):
    """Organization response schema."""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    legal_title: Optional[str]
    legal_address: Optional[str]
    actual_address: Optional[str]
    inn: Optional[str]
    kpp: Optional[str]
    ogrn: Optional[str]
    okpo: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    fax: Optional[str]
    bank_accounts: Optional[Dict[str, Any]]
    archived: bool
    shared: bool
    external_id: Optional[str]
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    """Employee response schema."""
    id: int
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: str
    full_name: str
    position: Optional[str]
    code: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    archived: bool
    organization_id: Optional[int]
    external_id: Optional[str]
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    """Project response schema."""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    archived: bool
    shared: bool
    external_id: Optional[str]
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    """Contract response schema."""
    id: int
    name: str
    code: Optional[str]
    number: Optional[str]
    description: Optional[str]
    moment: datetime
    contract_date: Optional[datetime]
    contract_type: str
    sum_amount: Decimal
    reward_percent: Optional[Decimal]
    reward_type: Optional[str]
    archived: bool
    counterparty_id: Optional[int]
    organization_id: Optional[int]
    project_id: Optional[int]
    external_id: Optional[str]
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CurrencyResponse(BaseModel):
    """Currency response schema."""
    id: int
    name: str
    full_name: Optional[str]
    code: str
    iso_code: Optional[str]
    is_default: bool
    multiplicity: int
    rate: Decimal
    archived: bool
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class CountryResponse(BaseModel):
    """Country response schema."""
    id: int
    name: str
    description: Optional[str]
    code: Optional[str]
    external_code: Optional[str]
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class OrganizationListFilter(BaseModel):
    """Organization list filter parameters."""
    search: Optional[str] = None
    archived: Optional[bool] = None


class EmployeeListFilter(BaseModel):
    """Employee list filter parameters."""
    search: Optional[str] = None
    organization_id: Optional[int] = None
    archived: Optional[bool] = None


class ProjectListFilter(BaseModel):
    """Project list filter parameters."""
    search: Optional[str] = None
    archived: Optional[bool] = None


class ContractListFilter(BaseModel):
    """Contract list filter parameters."""
    search: Optional[str] = None
    contract_type: Optional[str] = None
    counterparty_id: Optional[int] = None
    archived: Optional[bool] = None
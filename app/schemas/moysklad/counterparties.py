# app/schemas/moysklad/counterparties.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from decimal import Decimal


class CounterpartyResponse(BaseModel):
    """Counterparty response schema."""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    legal_title: Optional[str]
    legal_address: Optional[str]
    actual_address: Optional[str]
    inn: Optional[str]
    kpp: Optional[str]
    is_supplier: bool
    is_customer: bool
    discount_percentage: Optional[Decimal]
    archived: bool
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class CounterpartyListFilter(BaseModel):
    """Counterparty list filter parameters."""
    search: Optional[str] = None
    is_supplier: Optional[bool] = None
    is_customer: Optional[bool] = None
    archived: Optional[bool] = None

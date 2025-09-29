# app/schemas/moysklad/products.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime


class ProductFolderResponse(BaseModel):
    """Product folder response schema."""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    path_name: Optional[str]
    archived: bool
    parent_external_id: Optional[str]
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class UnitOfMeasureResponse(BaseModel):
    """Unit of measure response schema."""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class ProductVariantResponse(BaseModel):
    """Product variant response schema."""
    id: int
    name: str
    code: Optional[str]
    sale_price: Optional[Decimal]
    buy_price: Optional[Decimal]
    characteristics: Optional[Dict[str, Any]]
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Product response schema."""
    id: int
    name: str
    code: Optional[str]
    article: Optional[str]
    description: Optional[str]
    sale_price: Optional[Decimal]
    buy_price: Optional[Decimal]
    min_price: Optional[Decimal]
    weight: Optional[Decimal]
    volume: Optional[Decimal]
    archived: bool
    folder: Optional[ProductFolderResponse]
    unit: Optional[UnitOfMeasureResponse]
    variants: List[ProductVariantResponse] = []
    external_id: Optional[str]
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProductListFilter(BaseModel):
    """Product list filter parameters."""
    search: Optional[str] = None
    folder_id: Optional[int] = None
    archived: Optional[bool] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock: Optional[bool] = None


class ServiceResponse(BaseModel):
    """Service response schema."""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    sale_price: Optional[Decimal]
    buy_price: Optional[Decimal]
    min_price: Optional[Decimal]
    archived: bool
    folder: Optional[ProductFolderResponse]
    unit: Optional[UnitOfMeasureResponse]
    external_id: Optional[str]
    
    class Config:
        from_attributes = True

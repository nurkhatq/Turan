# app/schemas/moysklad/inventory.py (FIXED VERSION)
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class StoreResponse(BaseModel):
    """Store response schema."""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    address: Optional[str]
    archived: bool
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class StockResponse(BaseModel):
    """Stock response schema."""
    id: int
    stock: Decimal
    in_transit: Decimal
    reserve: Decimal
    available: Decimal
    store: StoreResponse
    external_id: Optional[str]
    last_sync_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StockListFilter(BaseModel):
    """Stock list filter parameters."""
    store_id: Optional[int] = None
    product_id: Optional[int] = None
    low_stock_threshold: Optional[Decimal] = None
    zero_stock: Optional[bool] = None
# app/schemas/common.py
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    limit: int = 50
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be greater than 0')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError('Limit must be greater than 0')
        if v > 1000:
            raise ValueError('Limit must not exceed 1000')
        return v


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int


class ResponseStatus(str, Enum):
    """Response status enumeration."""
    success = "success"
    error = "error"
    warning = "warning"


class StandardResponse(BaseModel):
    """Standard API response format."""
    status: ResponseStatus
    message: str
    data: Optional[Any] = None
    errors: Optional[Dict[str, Any]] = None

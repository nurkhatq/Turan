# app/schemas/exports.py
from typing import Dict, Optional, List, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class ExportFormat(str, Enum):
    """Export format enumeration."""
    csv = "csv"
    xlsx = "xlsx"
    json = "json"
    pdf = "pdf"


class ExportType(str, Enum):
    """Export type enumeration."""
    products = "products"
    customers = "customers"
    sales = "sales"
    inventory = "inventory"
    analytics = "analytics"


class ExportRequest(BaseModel):
    """Export request schema."""
    export_type: ExportType
    format: ExportFormat
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None  # Specific columns to export


class ExportResponse(BaseModel):
    """Export response schema."""
    export_id: str
    status: str  # pending, processing, completed, failed
    download_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
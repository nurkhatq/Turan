# app/schemas/moysklad/documents.py
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from enum import Enum
from .products import ProductResponse, ProductVariantResponse, ServiceResponse
from .inventory import StoreResponse
from .counterparties import CounterpartyResponse

class DocumentType(str, Enum):
    """Document type enumeration."""
    # Sales documents
    customer_order = "customerorder"
    invoice_out = "invoiceout"
    shipment = "shipment"
    sales_return = "salesreturn"
    
    # Purchase documents
    supplier_order = "supplierorder"
    invoice_in = "invoicein"
    supply = "supply"
    purchase_return = "purchasereturn"


class DocumentPositionResponse(BaseModel):
    """Document position response schema."""
    id: int
    quantity: Decimal
    price: Decimal
    discount: Decimal
    vat: Decimal
    product: Optional[ProductResponse]
    variant: Optional[ProductVariantResponse]
    service: Optional[ServiceResponse]
    
    class Config:
        from_attributes = True


class SalesDocumentResponse(BaseModel):
    """Sales document response schema."""
    id: int
    document_type: str
    name: str
    number: Optional[str]
    description: Optional[str]
    moment: datetime
    applicable: bool
    sum_total: Decimal
    vat_sum: Decimal
    state: Optional[str]
    counterparty: Optional[CounterpartyResponse]
    store: Optional[StoreResponse]
    positions: List[DocumentPositionResponse] = []
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class PurchaseDocumentResponse(BaseModel):
    """Purchase document response schema."""
    id: int
    document_type: str
    name: str
    number: Optional[str]
    description: Optional[str]
    moment: datetime
    applicable: bool
    sum_total: Decimal
    vat_sum: Decimal
    state: Optional[str]
    counterparty: Optional[CounterpartyResponse]
    store: Optional[StoreResponse]
    positions: List[DocumentPositionResponse] = []
    external_id: Optional[str]
    
    class Config:
        from_attributes = True


class DocumentListFilter(BaseModel):
    """Document list filter parameters."""
    document_type: Optional[DocumentType] = None
    counterparty_id: Optional[int] = None
    store_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    state: Optional[str] = None
    min_sum: Optional[Decimal] = None
    max_sum: Optional[Decimal] = None

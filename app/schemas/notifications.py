# app/schemas/notifications.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from .moysklad.products import ProductResponse, ProductVariantResponse, ServiceResponse
from .moysklad.inventory import StoreResponse
from .moysklad.counterparties import CounterpartyResponse

class NotificationType(str, Enum):
    """Notification type enumeration."""
    email = "email"
    system = "system"
    webhook = "webhook"


class NotificationSeverity(str, Enum):
    """Notification severity."""
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class NotificationCreate(BaseModel):
    """Notification creation schema."""
    title: str
    message: str
    notification_type: NotificationType
    severity: NotificationSeverity = NotificationSeverity.info
    recipients: List[str] = []  # User IDs or email addresses
    data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Notification response schema."""
    id: int
    title: str
    message: str
    notification_type: str
    severity: str
    is_sent: bool
    sent_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
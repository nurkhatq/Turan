# app/schemas/integrations.py
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class WebhookEvent(BaseModel):
    """Webhook event schema."""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    signature: Optional[str] = None


class MoySkladWebhookEvent(BaseModel):
    """MoySklad specific webhook event."""
    entityType: str
    action: str
    accountId: str
    entityId: str
    entityMeta: Dict[str, Any]
    moment: datetime
    events: List[Dict[str, Any]] = []


class SyncResult(BaseModel):
    """Synchronization result schema."""
    success: bool
    service_name: str
    job_type: str
    started_at: datetime
    completed_at: Optional[datetime]
    
    # Counters
    total_processed: int
    created_count: int
    updated_count: int
    deleted_count: int
    error_count: int
    
    # Details
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []
    summary: Dict[str, Any] = {}


class IntegrationTest(BaseModel):
    """Integration connection test."""
    service_name: str
    test_type: str = "connection"  # connection, auth, data_access
    parameters: Optional[Dict[str, Any]] = None


class IntegrationTestResult(BaseModel):
    """Integration test result."""
    success: bool
    service_name: str
    test_type: str
    response_time_ms: int
    message: str
    details: Optional[Dict[str, Any]] = None
    tested_at: datetime

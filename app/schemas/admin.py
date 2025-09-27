# app/schemas/admin.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class IntegrationStatus(str, Enum):
    """Integration status enumeration."""
    inactive = "inactive"
    active = "active"
    error = "error"
    syncing = "syncing"


class IntegrationConfigResponse(BaseModel):
    """Integration configuration response."""
    id: int
    service_name: str
    is_enabled: bool
    sync_interval_minutes: int
    last_sync_at: Optional[datetime]
    next_sync_at: Optional[datetime]
    sync_status: str
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class IntegrationConfigUpdate(BaseModel):
    """Integration configuration update schema."""
    is_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None
    config_data: Optional[Dict[str, Any]] = None
    credentials_data: Optional[Dict[str, str]] = None


class SyncJobResponse(BaseModel):
    """Sync job response schema."""
    id: int
    job_id: str
    service_name: str
    job_type: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_items: int
    processed_items: int
    failed_items: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class SyncJobStart(BaseModel):
    """Start sync job request."""
    service_name: str
    job_type: str = "incremental_sync"
    force_full_sync: bool = False


class SystemHealthResponse(BaseModel):
    """System health response."""
    status: str
    timestamp: datetime
    
    # Service status
    database_status: str
    redis_status: str
    celery_status: str
    
    # Integration status
    integrations_status: Dict[str, str]
    
    # Performance metrics
    active_users: int
    pending_jobs: int
    failed_jobs: int
    avg_response_time_ms: int
    
    # Resource usage
    memory_usage_percent: Optional[float]
    cpu_usage_percent: Optional[float]
    disk_usage_percent: Optional[float]


class SystemAlertResponse(BaseModel):
    """System alert response."""
    id: int
    alert_type: str
    title: str
    message: str
    severity: str
    alert_data: Optional[Dict[str, Any]]
    is_read: bool
    is_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertFilter(BaseModel):
    """Alert filter parameters."""
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    is_read: Optional[bool] = None
    is_resolved: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class PermissionResponse(BaseModel):
    """Permission response schema."""
    id: int
    name: str
    description: Optional[str]
    category: str
    
    class Config:
        from_attributes = True


class ApiLogResponse(BaseModel):
    """API log response schema."""
    id: int
    method: str
    endpoint: str
    user_id: Optional[int]
    ip_address: Optional[str]
    status_code: int
    response_time_ms: int
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApiLogFilter(BaseModel):
    """API log filter parameters."""
    method: Optional[str] = None
    endpoint: Optional[str] = None
    user_id: Optional[int] = None
    status_code: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_error: Optional[bool] = None


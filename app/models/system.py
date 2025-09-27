# app/models/system.py
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON
from datetime import datetime
from ..models.user import *
from ..models.moysklad.products import *
from ..models.moysklad.counterparties import *
from ..models.moysklad.inventory import *
from ..models.moysklad.documents import *
from .base import BaseModel


class IntegrationConfig(BaseModel):
    """Integration configuration for external services."""
    __tablename__ = "integration_config"
    
    service_name = Column(String(100), nullable=False, unique=True)  # moysklad, kaspi, etc.
    is_enabled = Column(Boolean, default=False, nullable=False)
    
    # Configuration data (stored as JSON)
    config_data = Column(JSON, nullable=True)
    
    # Credentials (encrypted)
    credentials_data = Column(Text, nullable=True)
    
    # Sync settings
    sync_interval_minutes = Column(Integer, default=15, nullable=False)
    last_sync_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    
    # Status
    sync_status = Column(String(50), default="inactive", nullable=False)
    error_message = Column(Text, nullable=True)


class SyncJob(BaseModel):
    """Background synchronization job tracking."""
    __tablename__ = "sync_job"
    
    job_id = Column(String(255), unique=True, nullable=False)  # Celery task ID
    service_name = Column(String(100), nullable=False)
    job_type = Column(String(100), nullable=False)  # full_sync, incremental_sync, etc.
    
    # Status tracking
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Progress tracking
    total_items = Column(Integer, default=0, nullable=False)
    processed_items = Column(Integer, default=0, nullable=False)
    failed_items = Column(Integer, default=0, nullable=False)
    
    # Result data
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)


class ApiLog(BaseModel):
    """API request logging."""
    __tablename__ = "api_log"
    
    # Request info
    method = Column(String(10), nullable=False)
    endpoint = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Response info
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    
    # Request/Response data (optional, for debugging)
    request_data = Column(Text, nullable=True)
    response_data = Column(Text, nullable=True)
    
    # Error info
    error_message = Column(Text, nullable=True)


class SystemAlert(BaseModel):
    """System alerts and notifications."""
    __tablename__ = "system_alert"
    
    alert_type = Column(String(100), nullable=False)  # stock_low, sync_error, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info", nullable=False)  # info, warning, error, critical
    
    # Alert data (JSON with specific alert information)
    alert_data = Column(JSON, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    # Relationships
    resolved_by = relationship("User")


class Permission(BaseModel):
    """Available system permissions."""
    __tablename__ = "permission"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # products, sales, admin, etc.
    is_system_permission = Column(Boolean, default=True, nullable=False)

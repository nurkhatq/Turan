# app/models/base.py (COMPLETE FIXED VERSION)
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields for all tables."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

class ExternalIdMixin:
    """Mixin for models that have external IDs from integrated services."""
    __abstract__ = True
    
    external_id = Column(String(255), nullable=True, index=True)
    last_sync_at = Column(DateTime, nullable=True)
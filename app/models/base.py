# app/models/base.py
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, String, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all tables."""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)  # Soft delete


class ExternalIdMixin:
    """Mixin for models that sync with external systems."""
    external_id = Column(String(255), index=True, nullable=True)  # External system ID
    external_meta = Column(Text, nullable=True)  # JSON metadata from external system
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="pending", nullable=False)  # pending, synced, error

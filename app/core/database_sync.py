"""
Synchronous database operations for Celery tasks.

This module provides synchronous database operations to avoid
asyncio event loop conflicts in Celery workers.
"""

import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from .config import Settings

settings = Settings()

# Create synchronous engine for Celery tasks
def get_sync_database_url():
    """Get database URL - keep asyncpg for now and handle sync differently."""
    return settings.DATABASE_URL

# For now, let's disable the sync engine and use a simpler approach
sync_engine = None

# Create sessionmaker
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

@contextmanager
def get_sync_db() -> Session:
    """Get synchronous database session for Celery tasks."""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_sync_db():
    """Initialize database tables (synchronous)."""
    from app.models.base import Base
    Base.metadata.create_all(bind=sync_engine)

def close_sync_db():
    """Close synchronous database connections."""
    sync_engine.dispose()

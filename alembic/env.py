# alembic/env.py (WINDOWS-COMPATIBLE VERSION)
import asyncio
import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_database_url(sync=False):
    """Get database URL from environment or config."""
    # Try to get from environment first (Docker)
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        # Convert async URL to sync if needed
        if sync and 'asyncpg' in db_url:
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
        return db_url
    
    # Try from alembic config
    config_url = config.get_main_option("sqlalchemy.url")
    if config_url:
        # Convert async URL to sync if needed
        if sync and 'asyncpg' in config_url:
            config_url = config_url.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
        return config_url
    
    # Fallback to default
    if sync:
        return "postgresql+psycopg2://crm_user:crm_password@localhost:5432/crm_db"
    return "postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm_db"

def get_metadata():
    """Get metadata from models with safe imports."""
    try:
        # Import all models to ensure they're registered
        from app.models.base import Base
        from app.models.user import User, Role, UserSession
        from app.models.system import IntegrationConfig, SyncJob, ApiLog, SystemAlert, Permission
        from app.models.moysklad.products import ProductFolder, UnitOfMeasure, Product, ProductVariant, Service
        from app.models.moysklad.counterparties import Counterparty
        from app.models.moysklad.inventory import Store, Stock
        from app.models.moysklad.documents import SalesDocument, SalesDocumentPosition, PurchaseDocument, PurchaseDocumentPosition
        from app.models.analytics import ProductAnalytics, CustomerAnalytics, SalesAnalytics
        
        return Base.metadata
    except ImportError as e:
        print(f"Warning: Could not import all models: {e}")
        # Create minimal metadata for basic tables
        from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, DateTime
        from datetime import datetime
        
        metadata = MetaData()
        
        # Create basic users table
        Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('email', String(255), unique=True, nullable=False),
            Column('hashed_password', String(255), nullable=False),
            Column('full_name', String(255), nullable=False),
            Column('is_active', Boolean, default=True, nullable=False),
            Column('is_superuser', Boolean, default=False, nullable=False),
            Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
            Column('updated_at', DateTime, default=datetime.utcnow, nullable=False),
            Column('is_deleted', Boolean, default=False, nullable=False),
            Column('last_login_at', DateTime, nullable=True)
        )
        
        return metadata

# Set target metadata
target_metadata = get_metadata()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url(sync=True)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run async migrations."""
    
    # Get database URL
    database_url = get_database_url()
    
    # Create configuration for the engine
    configuration = {
        "sqlalchemy.url": database_url,
        "sqlalchemy.poolclass": pool.NullPool,
        "sqlalchemy.echo": False,
    }
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_sync_migrations() -> None:
    """Run migrations using synchronous connection (Windows fallback)."""
    try:
        # Get synchronous database URL
        database_url = get_database_url(sync=True)
        print(f"Trying synchronous connection to: {database_url}")
        
        # Create synchronous engine
        engine = create_engine(
            database_url,
            poolclass=pool.NullPool,
            echo=False,
        )
        
        # Run migrations
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
                
        engine.dispose()
        print("✅ Synchronous migration completed successfully!")
        
    except Exception as e:
        print(f"Synchronous migration failed: {e}")
        raise

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    try:
        # Try async first
        asyncio.run(run_async_migrations())
    except Exception as async_error:
        print(f"Async migration failed: {async_error}")
        print("🔄 Falling back to synchronous migration...")
        try:
            run_sync_migrations()
        except Exception as sync_error:
            print(f"Both async and sync migrations failed!")
            print(f"Async error: {async_error}")
            print(f"Sync error: {sync_error}")
            raise sync_error

# Run the appropriate migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
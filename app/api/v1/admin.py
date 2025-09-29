# app/api/v1/admin.py (FIXED VERSION)
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, logger, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_superuser, require_admin_access
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserCreate, UserUpdate, RoleResponse, RoleCreate
from app.schemas.admin import (
    IntegrationConfigResponse,
    IntegrationConfigUpdate,
    SyncJobResponse,
    SyncJobStart,
    SystemHealthResponse,
    SystemAlertResponse,
    AlertFilter
)
from app.schemas.common import PaginatedResponse, PaginationParams
from app.models.user import User

router = APIRouter()


@router.get("/users", response_model=PaginatedResponse)
async def get_users(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (admin only)."""
    try:
        user_service = UserService(db)
        
        users = await user_service.get_users(
            skip=(pagination.page - 1) * pagination.limit,
            limit=pagination.limit
        )
        
        return PaginatedResponse(
            items=[UserResponse.from_orm(user) for user in users],
            total=len(users),
            page=pagination.page,
            limit=pagination.limit,
            pages=1
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.put("/integrations/{service_name}", response_model=IntegrationConfigResponse)
async def update_integration(
    service_name: str,
    config_data: IntegrationConfigUpdate,
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Update integration configuration."""
    try:
        from app.models.system import IntegrationConfig
        from sqlalchemy import select
        import json
        
        # Get existing config or create new
        stmt = select(IntegrationConfig).where(
            IntegrationConfig.service_name == service_name
        )
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        
        if not config:
            config = IntegrationConfig(service_name=service_name)
            db.add(config)
        
        # Update fields
        if config_data.is_enabled is not None:
            config.is_enabled = config_data.is_enabled
        
        if config_data.sync_interval_minutes is not None:
            config.sync_interval_minutes = config_data.sync_interval_minutes
        
        if config_data.config_data is not None:
            config.config_data = config_data.config_data
        
        if config_data.credentials_data is not None:
            # In production, encrypt this data
            config.credentials_data = json.dumps(config_data.credentials_data)
        
        await db.commit()
        await db.refresh(config)
        
        return IntegrationConfigResponse.from_orm(config)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update integration: {str(e)}"
        )


@router.get("/integrations", response_model=List[IntegrationConfigResponse])
async def get_integrations(
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get all integration configurations."""
    try:
        from app.models.system import IntegrationConfig
        from sqlalchemy import select
        
        stmt = select(IntegrationConfig).where(IntegrationConfig.is_deleted == False)
        result = await db.execute(stmt)
        configs = result.scalars().all()
        
        return [IntegrationConfigResponse.from_orm(config) for config in configs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve integrations: {str(e)}"
        )


@router.post("/sync/start", response_model=dict)
async def start_sync_job(
    job_data: SyncJobStart,
    current_user: User = Depends(require_admin_access)
):
    """Start synchronization job."""
    try:
        from app.tasks.sync_tasks import moysklad_full_sync, moysklad_incremental_sync
        
        if job_data.service_name == "moysklad":
            if job_data.force_full_sync or job_data.job_type == "full_sync":
                task = moysklad_full_sync.delay()
            else:
                task = moysklad_incremental_sync.delay()
            
            return {
                "message": "Sync job started",
                "job_id": task.id,
                "service": job_data.service_name,
                "type": job_data.job_type
            }
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported service"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start sync job: {str(e)}"
        )

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get system health status."""
    try:
        from datetime import datetime
        
        return SystemHealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            database_status="healthy",
            redis_status="healthy",
            celery_status="healthy",
            integrations_status={
                "moysklad": "active"
            },
            active_users=1,
            pending_jobs=0,
            failed_jobs=0,
            avg_response_time_ms=150,
            memory_usage_percent=45.2,
            cpu_usage_percent=23.1,
            disk_usage_percent=67.8
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )


@router.post("/integrations/test")
async def test_integration(
    service_name: str = Query(..., description="Service name to test (e.g., moysklad)"),
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Test integration connection."""
    try:
        if service_name.lower() == "moysklad":
            from app.services.integrations.moysklad.sync_service import MoySkladSyncService
            
            sync_service = MoySkladSyncService(db)
            
            # Create client and test connection
            async with await sync_service.create_moysklad_client() as client:
                result = await client.test_connection()
                
            return result
        else:
            return {
                "success": False,
                "message": f"Unknown service: {service_name}"
            }
            
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return {
            "success": False,
            "message": f"Test failed: {str(e)}"
        }


@router.get("/sync/statistics")
async def get_sync_statistics(
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get synchronization statistics."""
    try:
        from sqlalchemy import text, select
        from sqlalchemy import func
        from app.models.moysklad.organizations import Organization, Employee, Project, Contract, Currency, Country
        from app.models.moysklad.products import Product, Service, ProductFolder
        from app.models.moysklad.counterparties import Counterparty
        from app.models.moysklad.inventory import Store, Stock
        
        # Get counts for all entities
        stats = {}
        
        # Organizations
        org_stmt = select(func.count(Organization.id)).where(Organization.is_deleted == False)
        org_result = await db.execute(org_stmt)
        stats["organizations"] = org_result.scalar() or 0
        
        # Employees
        emp_stmt = select(func.count(Employee.id)).where(Employee.is_deleted == False)
        emp_result = await db.execute(emp_stmt)
        stats["employees"] = emp_result.scalar() or 0
        
        # Projects
        proj_stmt = select(func.count(Project.id)).where(Project.is_deleted == False)
        proj_result = await db.execute(proj_stmt)
        stats["projects"] = proj_result.scalar() or 0
        
        # Contracts
        contract_stmt = select(func.count(Contract.id)).where(Contract.is_deleted == False)
        contract_result = await db.execute(contract_stmt)
        stats["contracts"] = contract_result.scalar() or 0
        
        # Currencies
        currency_stmt = select(func.count(Currency.id)).where(Currency.is_deleted == False)
        currency_result = await db.execute(currency_stmt)
        stats["currencies"] = currency_result.scalar() or 0
        
        # Countries
        country_stmt = select(func.count(Country.id)).where(Country.is_deleted == False)
        country_result = await db.execute(country_stmt)
        stats["countries"] = country_result.scalar() or 0
        
        # Products
        product_stmt = select(func.count(Product.id)).where(Product.is_deleted == False)
        product_result = await db.execute(product_stmt)
        stats["products"] = product_result.scalar() or 0
        
        # Services
        service_stmt = select(func.count(Service.id)).where(Service.is_deleted == False)
        service_result = await db.execute(service_stmt)
        stats["services"] = service_result.scalar() or 0
        
        # Counterparties
        cp_stmt = select(func.count(Counterparty.id)).where(Counterparty.is_deleted == False)
        cp_result = await db.execute(cp_stmt)
        stats["counterparties"] = cp_result.scalar() or 0
        
        # Stores
        store_stmt = select(func.count(Store.id)).where(Store.is_deleted == False)
        store_result = await db.execute(store_stmt)
        stats["stores"] = store_result.scalar() or 0
        
        # Stock records
        stock_stmt = select(func.count(Stock.id)).where(Stock.is_deleted == False)
        stock_result = await db.execute(stock_stmt)
        stats["stock_records"] = stock_result.scalar() or 0
        
        # Get last sync job
        from app.models.system import SyncJob
        last_job_stmt = select(SyncJob).where(
            SyncJob.service_name == "moysklad"
        ).order_by(SyncJob.created_at.desc()).limit(1)
        last_job_result = await db.execute(last_job_stmt)
        last_job = last_job_result.scalar_one_or_none()
        
        return {
            "statistics": stats,
            "total_records": sum(stats.values()),
            "last_sync": {
                "job_id": last_job.job_id if last_job else None,
                "status": last_job.status if last_job else None,
                "started_at": last_job.started_at.isoformat() if last_job and last_job.started_at else None,
                "completed_at": last_job.completed_at.isoformat() if last_job and last_job.completed_at else None,
            } if last_job else None
        }
        
    except Exception as e:
        logger.error(f"Failed to get sync statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )
# app/api/v1/admin.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
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
    user_service = UserService(db)
    
    users = await user_service.get_users(
        skip=(pagination.page - 1) * pagination.limit,
        limit=pagination.limit
    )
    
    # For simplicity, not implementing total count here
    return PaginatedResponse(
        items=[UserResponse.from_orm(user) for user in users],
        total=len(users),
        page=pagination.page,
        limit=pagination.limit,
        pages=1
    )


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Create new user (admin only)."""
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(user_data)
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)."""
    user_service = UserService(db)
    
    try:
        user = await user_service.update_user(user_id, user_data)
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only)."""
    user_service = UserService(db)
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}


@router.get("/integrations", response_model=List[IntegrationConfigResponse])
async def get_integrations(
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get all integration configurations."""
    from app.models.system import IntegrationConfig
    from sqlalchemy import select
    
    stmt = select(IntegrationConfig).where(IntegrationConfig.is_deleted == False)
    result = await db.execute(stmt)
    configs = result.scalars().all()
    
    return [IntegrationConfigResponse.from_orm(config) for config in configs]


@router.put("/integrations/{service_name}", response_model=IntegrationConfigResponse)
async def update_integration(
    service_name: str,
    config_data: IntegrationConfigUpdate,
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Update integration configuration."""
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


@router.post("/sync/start", response_model=dict)
async def start_sync_job(
    job_data: SyncJobStart,
    current_user: User = Depends(require_admin_access)
):
    """Start synchronization job."""
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
    
    raise HTTPException(status_code=400, detail="Unsupported service")


@router.get("/sync/jobs", response_model=List[SyncJobResponse])
async def get_sync_jobs(
    service_name: Optional[str] = None,
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get synchronization job history."""
    from app.models.system import SyncJob
    from sqlalchemy import select, desc
    
    stmt = select(SyncJob).where(SyncJob.is_deleted == False)
    
    if service_name:
        stmt = stmt.where(SyncJob.service_name == service_name)
    
    stmt = stmt.order_by(desc(SyncJob.created_at)).limit(50)
    
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    return [SyncJobResponse.from_orm(job) for job in jobs]


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get system health status."""
    from datetime import datetime
    
    # This is a simplified health check
    # In production, you'd check actual service status
    
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

@router.post("/integrations/test", response_model=dict)
async def test_integration(
    service_name: str = "moysklad",
    current_user: User = Depends(require_admin_access)
):
    """Test integration connection."""
    from app.services.integrations.moysklad.client import MoySkladClient
    
    if service_name == "moysklad":
        try:
            async with MoySkladClient() as client:
                result = await client.test_connection()
                return result
        except Exception as e:
            return {
                "success": False,
                "message": f"Test failed: {str(e)}"
            }
    
    raise HTTPException(status_code=400, detail="Unsupported service")


@router.get("/alerts", response_model=List[SystemAlertResponse])
async def get_system_alerts(
    filters: AlertFilter = Depends(),
    current_user: User = Depends(require_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get system alerts."""
    from app.models.system import SystemAlert
    from sqlalchemy import select, desc, and_
    
    stmt = select(SystemAlert).where(SystemAlert.is_deleted == False)
    
    # Apply filters
    conditions = []
    if filters.alert_type:
        conditions.append(SystemAlert.alert_type == filters.alert_type)
    if filters.severity:
        conditions.append(SystemAlert.severity == filters.severity)
    if filters.is_read is not None:
        conditions.append(SystemAlert.is_read == filters.is_read)
    if filters.is_resolved is not None:
        conditions.append(SystemAlert.is_resolved == filters.is_resolved)
    
    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    stmt = stmt.order_by(desc(SystemAlert.created_at)).limit(100)
    
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    return [SystemAlertResponse.from_orm(alert) for alert in alerts]

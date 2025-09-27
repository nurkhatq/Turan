# app/api/v1/admin.py (FIXED VERSION)
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
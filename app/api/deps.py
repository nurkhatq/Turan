# app/api/deps.py
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import get_db
from app.core.redis import get_redis, RedisManager
from app.core.security import verify_token
from app.core.exceptions import authentication_exception, authorization_exception
from app.services.auth_service import AuthService
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    
    try:
        # Verify JWT token
        payload = verify_token(token)
        if payload is None:
            raise authentication_exception("Invalid token")
        
        # Check token type
        if payload.get("type") != "access":
            raise authentication_exception("Invalid token type")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise authentication_exception("Invalid token payload")
        
        # Get user from database
        auth_service = AuthService(db, redis)
        user = await auth_service.get_user_by_id(int(user_id))
        
        if user is None:
            raise authentication_exception("User not found")
        
        if not user.is_active:
            raise authentication_exception("User account is disabled")
        
        return user
        
    except JWTError:
        raise authentication_exception("Invalid token")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise authentication_exception("User account is disabled")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise authorization_exception("Superuser access required")
    return current_user


def require_permission(permission: str):
    """Dependency factory for permission checking."""
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.has_permission(permission):
            raise authorization_exception(f"Permission '{permission}' required")
        return current_user
    
    return permission_checker


# Common permission dependencies
require_products_read = require_permission("products.read")
require_products_write = require_permission("products.write")
require_sales_read = require_permission("sales.read")
require_analytics_read = require_permission("analytics.read")
require_admin_access = require_permission("admin.access")
require_integrations_manage = require_permission("integrations.manage")

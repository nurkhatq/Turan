# app/services/auth_service.py (SIMPLIFIED VERSION)
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.security import (
    create_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.core.redis import RedisManager
from app.core.exceptions import AuthenticationError, ValidationError
from app.models.user import User
from app.schemas.user import TokenResponse


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: AsyncSession, redis: RedisManager):
        self.db = db
        self.redis = redis
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        stmt = select(User).where(
            User.email == email,
            User.is_deleted == False
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def create_user_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for user (simplified)."""
        # Create tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        # Update last login (simplified - no session tracking for now)
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        # Create simplified response without full user object
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                last_login_at=user.last_login_at,
                created_at=user.created_at,
                roles=[],
                permissions=user.permissions or []
            )
        )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).where(
            User.id == user_id,
            User.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(
            User.email == email,
            User.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


# Import UserResponse at the bottom to avoid circular imports
from app.schemas.user import UserResponse
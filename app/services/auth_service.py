# app/services/auth_service.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
from app.models.user import User, Role, UserSession
from app.schemas.user import UserCreate, TokenResponse


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
        """Create access and refresh tokens for user."""
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        # Store session in database
        session = UserSession(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        self.db.add(session)
        await self.db.commit()
        
        # Cache user permissions in Redis
        permissions_key = f"user_permissions:{user.id}"
        await self.redis.set(
            permissions_key,
            user.permissions,
            ttl=1800  # 30 minutes
        )
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user=user
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        # Get user and session
        user = await self.get_user_by_id(int(user_id))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        stmt = select(UserSession).where(
            UserSession.refresh_token == refresh_token,
            UserSession.user_id == user.id,
            UserSession.is_deleted == False
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise AuthenticationError("Invalid session")
        
        # Create new tokens
        return await self.create_user_tokens(user)
    
    async def logout_user(self, user: User, access_token: str):
        """Logout user and invalidate session."""
        # Find and invalidate session
        stmt = select(UserSession).where(
            UserSession.session_token == access_token,
            UserSession.user_id == user.id,
            UserSession.is_deleted == False
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session:
            session.is_deleted = True
            await self.db.commit()
        
        # Remove cached permissions
        permissions_key = f"user_permissions:{user.id}"
        await self.redis.delete(permissions_key)
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).options(
            selectinload(User.roles)
        ).where(
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
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        # Check if email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValidationError("Email already registered")
        
        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=create_password_hash(user_data.password),
            is_active=user_data.is_active
        )
        
        self.db.add(user)
        await self.db.flush()  # Get user ID
        
        # Assign roles
        if user_data.role_ids:
            stmt = select(Role).where(Role.id.in_(user_data.role_ids))
            result = await self.db.execute(stmt)
            roles = result.scalars().all()
            user.roles.extend(roles)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user_password(
        self, 
        user: User, 
        current_password: str, 
        new_password: str
    ):
        """Update user password."""
        if not verify_password(current_password, user.hashed_password):
            raise AuthenticationError("Current password is incorrect")
        
        user.hashed_password = create_password_hash(new_password)
        await self.db.commit()
        
        # Invalidate all user sessions
        stmt = select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.is_deleted == False
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        for session in sessions:
            session.is_deleted = True
        
        await self.db.commit()
        
        # Clear cached permissions
        permissions_key = f"user_permissions:{user.id}"
        await self.redis.delete(permissions_key)

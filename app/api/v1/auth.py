# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis, RedisManager
from app.core.exceptions import AuthenticationError
from app.services.auth_service import AuthService
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserPasswordUpdate,
    UserResponse
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """User login endpoint."""
    auth_service = AuthService(db, redis)
    
    # Authenticate user
    user = await auth_service.authenticate_user(
        login_data.email,
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    return await auth_service.create_user_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """Refresh access token."""
    auth_service = AuthService(db, redis)
    
    try:
        return await auth_service.refresh_access_token(refresh_data.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """User logout endpoint."""
    auth_service = AuthService(db, redis)
    await auth_service.logout_user(current_user, credentials.credentials)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user


@router.put("/me/password")
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis)
):
    """Update current user password."""
    auth_service = AuthService(db, redis)
    
    try:
        await auth_service.update_user_password(
            current_user,
            password_data.current_password,
            password_data.new_password
        )
        return {"message": "Password updated successfully"}
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

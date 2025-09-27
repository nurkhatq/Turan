# app/schemas/user.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema."""
    password: str
    role_ids: Optional[List[int]] = []
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserPasswordUpdate(BaseModel):
    """Password update schema."""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_superuser: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    roles: List['RoleResponse'] = []
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base role schema."""
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleCreate(RoleBase):
    """Role creation schema."""
    pass


class RoleUpdate(BaseModel):
    """Role update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(RoleBase):
    """Role response schema."""
    id: int
    is_system_role: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str

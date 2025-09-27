# app/services/user_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate, RoleCreate, RoleUpdate
from app.core.security import create_password_hash
from app.core.exceptions import ValidationError, NotFoundError

class UserService:
    """Service for user management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[User]:
        """Get list of users."""
        stmt = select(User).options(selectinload(User.roles))
        
        if not include_deleted:
            stmt = stmt.where(User.is_deleted == False)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        stmt = select(User).options(selectinload(User.roles)).where(
            and_(User.id == user_id, User.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        # Check if email exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValidationError("Email already exists")
        
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=create_password_hash(user_data.password),
            is_active=user_data.is_active
        )
        
        self.db.add(user)
        await self.db.flush()
        
        # Assign roles
        if user_data.role_ids:
            roles_stmt = select(Role).where(Role.id.in_(user_data.role_ids))
            roles_result = await self.db.execute(roles_stmt)
            roles = roles_result.scalars().all()
            user.roles.extend(roles)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Update fields
        if user_data.email is not None:
            # Check email uniqueness
            existing = await self.get_user_by_email(user_data.email)
            if existing and existing.id != user_id:
                raise ValidationError("Email already exists")
            user.email = user_data.email
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        # Update roles
        if user_data.role_ids is not None:
            user.roles.clear()
            if user_data.role_ids:
                roles_stmt = select(Role).where(Role.id.in_(user_data.role_ids))
                roles_result = await self.db.execute(roles_stmt)
                roles = roles_result.scalars().all()
                user.roles.extend(roles)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Soft delete user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_deleted = True
        user.is_active = False
        await self.db.commit()
        return True
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(User).where(
            and_(User.email == email, User.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

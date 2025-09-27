# app/models/user.py (FIXED VERSION)
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
import json
from .base import BaseModel


class User(BaseModel):
    """User model with flexible role-based access."""
    __tablename__ = "users"  # CONSISTENT TABLE NAME
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)  # FIXED: Added proper type
    
    @hybrid_property
    def permissions(self):
        """Get all permissions from all user roles."""
        # Simplified for now - return basic permissions for superuser
        if self.is_superuser:
            return ["admin.access", "users.read", "users.write", "products.read", "products.write", "sales.read", "analytics.read", "integrations.manage"]
        return []
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        if self.is_superuser:
            return True
        return permission in self.permissions


class Role(BaseModel):
    """Dynamic role model with configurable permissions."""
    __tablename__ = "role"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions_data = Column(Text, nullable=True)  # JSON array of permissions
    is_system_role = Column(Boolean, default=False, nullable=False)  # System vs custom roles
    
    @hybrid_property
    def permissions(self):
        """Get permissions as list."""
        if self.permissions_data:
            return json.loads(self.permissions_data)
        return []
    
    @permissions.setter
    def permissions(self, value):
        """Set permissions from list."""
        self.permissions_data = json.dumps(value) if value else None


class UserSession(BaseModel):
    """User session tracking."""
    __tablename__ = "user_session"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # FIXED: users not user
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=True)
    expires_at = Column(DateTime, nullable=False)  # FIXED: Proper DateTime type
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Relationships
    user = relationship("User", backref="sessions")
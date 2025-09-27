# app/models/user.py
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import json
from .base import BaseModel

# Association table for user roles (many-to-many) - commented out for now
# user_roles = Table(
#     'user_roles',
#     BaseModel.metadata,
#     Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
#     Column('role_id', Integer, ForeignKey('role.id'), primary_key=True)
# )


class User(BaseModel):
    """User model with flexible role-based access."""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    # last_login_at = Column(String(50), nullable=True)  # Column doesn't exist in DB yet
    
    # Relationships (simplified for now)
    # roles = relationship("Role", secondary=user_roles, back_populates="users")
    
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
    
    # Relationships (simplified for now)
    # users = relationship("User", secondary=user_roles, back_populates="roles")
    
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
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    refresh_token = Column(String(255), unique=True, nullable=True)
    expires_at = Column(String(50), nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Relationships (simplified for now)
    # user = relationship("User", backref="sessions")


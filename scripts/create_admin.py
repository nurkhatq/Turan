# scripts/create_admin.py
#!/usr/bin/env python3
"""Create initial admin user script."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import get_db_context
from app.models.user import User, Role
from app.core.security import create_password_hash
import json

async def create_admin_user():
    """Create initial admin user and roles."""
    async with get_db_context() as db:
        # Create admin role
        admin_role = Role(
            name="Администратор",
            description="Полный доступ к системе",
            permissions=json.dumps([
                "admin.access",
                "users.manage",
                "products.read",
                "products.write",
                "sales.read",
                "analytics.read",
                "integrations.manage"
            ]),
            is_system_role=True
        )
        db.add(admin_role)
        await db.flush()
        
        # Create admin user
        admin_user = User(
            email="admin@example.com",
            full_name="Системный администратор",
            hashed_password=create_password_hash("admin123"),
            is_superuser=True,
            is_active=True
        )
        admin_user.roles.append(admin_role)
        
        db.add(admin_user)
        await db.commit()
        
        print("✅ Admin user created:")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: admin123")
        print("   🚨 Please change the password after first login!")

async def main():
    """Main function."""
    try:
        await create_admin_user()
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
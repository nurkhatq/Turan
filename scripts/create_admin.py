# scripts/create_admin.py
#!/usr/bin/env python3
"""Create initial admin user script."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import get_db_context
from app.core.security import create_password_hash
from sqlalchemy import text

async def create_admin_user():
    """Create initial admin user using raw SQL."""
    async with get_db_context() as db:
        # Check if admin already exists
        result = await db.execute(text("SELECT id FROM users WHERE email = 'admin@example.com'"))
        existing_user = result.fetchone()
        
        if existing_user:
            print("⚠️  Admin user already exists")
            return
        
        # Create admin user using raw SQL
        hashed_password = create_password_hash("admin123")
        await db.execute(text("""
            INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at, is_deleted)
            VALUES ('admin@example.com', :password, 'System Administrator', true, true, NOW(), NOW(), false)
        """), {"password": hashed_password})
        
        await db.commit()
        
        print("✅ Admin user created:")
        print("   Email: admin@example.com")
        print("   Password: admin123")
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
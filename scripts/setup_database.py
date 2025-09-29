#!/usr/bin/env python3
"""Complete database setup script."""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

async def setup_database():
    """Complete database setup process."""
    
    print("🗄️  Setting up database...")
    
    try:
        # Step 1: Initialize database tables
        print("1️⃣  Initializing database...")
        
        # Set the correct database URL for Docker environment
        import os
        os.environ['DATABASE_URL'] = 'postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm_db'
        
        from app.core.database import init_db
        await init_db()
        print("✅ Database initialized")
        
        # Step 2: Create initial migration
        print("2️⃣  Creating initial migration...")
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", "-m", "Initial migration"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️  Migration creation failed, but continuing...")
            print(result.stderr)
        else:
            print("✅ Initial migration created")
        
        # Step 3: Run migrations
        print("3️⃣  Running migrations...")
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️  Migration failed:")
            print(result.stderr)
        else:
            print("✅ Migrations completed")
        
        # Step 4: Create admin user
        print("4️⃣  Creating admin user...")
        await create_admin_user()
        
        print("🎉 Database setup completed!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()

async def create_admin_user():
    """Create initial admin user."""
    try:
        from app.core.database import get_db_context
        from app.models.base import User
        from app.core.security import create_password_hash
        
        async with get_db_context() as db:
            # Check if admin already exists
            from sqlalchemy import select
            stmt = select(User).where(User.email == "admin@example.com")
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("⚠️  Admin user already exists")
                return
            
            # Create admin user
            admin_user = User(
                email="admin@example.com",
                full_name="System Administrator",
                hashed_password=create_password_hash("admin123"),
                is_superuser=True,
                is_active=True
            )
            
            db.add(admin_user)
            await db.commit()
            
            print("✅ Admin user created:")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: admin123")
            print("   🚨 Please change the password after first login!")
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")

if __name__ == "__main__":
    asyncio.run(setup_database())
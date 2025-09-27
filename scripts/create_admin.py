# scripts/create_admin.py
#!/usr/bin/env python3
"""Create initial admin user script with better error handling."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import get_db_context
from app.core.security import create_password_hash
from sqlalchemy import text

async def create_admin_user():
    """Create initial admin user using raw SQL with better error handling."""
    async with get_db_context() as db:
        try:
            # Check if users table exists
            table_check = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            
            table_exists = table_check.scalar()
            
            if not table_exists:
                print("⚠️  Users table does not exist. Creating tables first...")
                
                # Create basic users table if it doesn't exist
                await db.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT true NOT NULL,
                        is_superuser BOOLEAN DEFAULT false NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        is_deleted BOOLEAN DEFAULT false NOT NULL
                    );
                """))
                await db.commit()
                print("✅ Users table created")
            
            # Check if admin already exists
            result = await db.execute(text("SELECT id FROM users WHERE email = 'admin@example.com'"))
            existing_user = result.fetchone()
            
            if existing_user:
                print("⚠️  Admin user already exists")
                return True
            
            # Create admin user with shorter password (bcrypt limitation)
            try:
                # Use shorter password to avoid bcrypt 72-byte limit
                short_password = "admin123"
                hashed_password = create_password_hash(short_password)
                
                await db.execute(text("""
                    INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at, is_deleted)
                    VALUES (:email, :password, :full_name, :is_active, :is_superuser, NOW(), NOW(), :is_deleted)
                """), {
                    "email": "admin@example.com",
                    "password": hashed_password,
                    "full_name": "System Administrator",
                    "is_active": True,
                    "is_superuser": True,
                    "is_deleted": False
                })
                
                await db.commit()
                
                print("✅ Admin user created successfully:")
                print("   Email: admin@example.com")
                print("   Password: admin123")
                print("   🚨 Please change the password after first login!")
                return True
                
            except Exception as hash_error:
                print(f"❌ Password hashing error: {hash_error}")
                
                # Fallback: try with a simpler password
                try:
                    simple_password = "admin"
                    hashed_password = create_password_hash(simple_password)
                    
                    await db.execute(text("""
                        INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at, is_deleted)
                        VALUES (:email, :password, :full_name, :is_active, :is_superuser, NOW(), NOW(), :is_deleted)
                    """), {
                        "email": "admin@example.com",
                        "password": hashed_password,
                        "full_name": "System Administrator",
                        "is_active": True,
                        "is_superuser": True,
                        "is_deleted": False
                    })
                    
                    await db.commit()
                    
                    print("✅ Admin user created with fallback password:")
                    print("   Email: admin@example.com")
                    print("   Password: admin")
                    print("   🚨 SECURITY WARNING: Change this password immediately!")
                    return True
                    
                except Exception as fallback_error:
                    print(f"❌ Fallback creation also failed: {fallback_error}")
                    return False
            
        except Exception as e:
            print(f"❌ Failed to create admin user: {e}")
            await db.rollback()
            return False

async def main():
    """Main function."""
    try:
        success = await create_admin_user()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
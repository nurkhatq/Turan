#!/usr/bin/env python3
"""Debug script to test endpoints and identify issues."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

async def test_imports():
    """Test if all imports work correctly."""
    print("🔍 Testing imports...")
    
    try:
        print("  Testing base imports...")
        from app.models.base import Base, BaseModel
        print("  ✅ Base models imported successfully")
        
        print("  Testing user models...")
        from app.models.user import User, Role
        print("  ✅ User models imported successfully")
        
        print("  Testing system models...")
        from app.models.system import IntegrationConfig, SyncJob
        print("  ✅ System models imported successfully")
        
        print("  Testing MoySklad models...")
        from app.models.moysklad.products import Product
        from app.models.moysklad.counterparties import Counterparty
        from app.models.moysklad.inventory import Store, Stock
        print("  ✅ MoySklad models imported successfully")
        
        print("  Testing analytics models...")
        from app.models.analytics import ProductAnalytics
        print("  ✅ Analytics models imported successfully")
        
        print("  Testing all models import...")
        from app.models import Base
        print("  ✅ All models imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_connection():
    """Test database connection and table creation."""
    print("\n🔍 Testing database connection...")
    
    try:
        from app.core.database import engine, init_db
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("  ✅ Database connection successful")
        
        # Test table creation
        await init_db()
        print("  ✅ Database tables created/verified")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_redis_connection():
    """Test Redis connection."""
    print("\n🔍 Testing Redis connection...")
    
    try:
        from app.core.redis import redis_manager
        
        await redis_manager.connect()
        
        # Test set/get
        await redis_manager.set("test_key", "test_value", ttl=10)
        value = await redis_manager.get("test_key")
        
        if value == "test_value":
            print("  ✅ Redis connection and operations successful")
            await redis_manager.delete("test_key")
            return True
        else:
            print("  ❌ Redis operations failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Redis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_auth_service():
    """Test authentication service."""
    print("\n🔍 Testing authentication service...")
    
    try:
        from app.core.database import get_db_context
        from app.core.redis import redis_manager
        from app.services.auth_service import AuthService
        
        async with get_db_context() as db:
            auth_service = AuthService(db, redis_manager)
            
            # Test getting non-existent user
            user = await auth_service.get_user_by_email("nonexistent@example.com")
            
            if user is None:
                print("  ✅ Authentication service working correctly")
                return True
            else:
                print("  ⚠️  Authentication service returned unexpected result")
                return False
                
    except Exception as e:
        print(f"  ❌ Authentication service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_dependencies():
    """Test API dependencies."""
    print("\n🔍 Testing API dependencies...")
    
    try:
        from app.api.deps import require_products_read, get_current_user
        print("  ✅ API dependencies imported successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ API dependencies test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting endpoint debugging...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database_connection), 
        ("Redis", test_redis_connection),
        ("Auth Service", test_auth_service),
        ("API Dependencies", test_api_dependencies)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your endpoints should work now.")
        print("\n💡 If you're still getting 500 errors, check:")
        print("   1. Make sure all migrations are applied: alembic upgrade head")
        print("   2. Check if admin user exists: python scripts/create_admin.py")
        print("   3. Restart your FastAPI server")
    else:
        print("\n⚠️  Some tests failed. Fix the issues above before testing endpoints.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""Test MoySklad connection script."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.integrations.moysklad.client import MoySkladClient

async def test_connection():
    """Test MoySklad API connection."""
    print("🔍 Testing MoySklad API connection...")
    
    try:
        async with MoySkladClient() as client:
            result = await client.test_connection()
            
            if result["success"]:
                print(f"✅ {result['message']}")
                print(f"   Authentication method: {result.get('auth_method', 'unknown')}")
                if 'organizations_count' in result:
                    print(f"   Organizations accessible: {result['organizations_count']}")
            else:
                print(f"❌ {result['message']}")
                if 'details' in result:
                    print(f"   Details: {result['details']}")
                    
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    return result.get("success", False)

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
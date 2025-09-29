# scripts/init_db.py
#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import init_db
from app.core.config import Settings

async def main():
    """Initialize database tables."""
    settings = Settings()
    print(f"Initializing database: {settings.DATABASE_URL}")
    
    try:
        await init_db()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
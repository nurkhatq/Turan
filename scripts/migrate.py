# scripts/migrate.py
#!/usr/bin/env python3
"""Database migration script."""

import subprocess
import sys
from pathlib import Path

def run_migrations():
    """Run Alembic migrations."""
    try:
        # Run migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            print(result.stdout)
        else:
            print("❌ Database migrations failed")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()
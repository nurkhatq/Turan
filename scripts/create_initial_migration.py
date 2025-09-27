#!/usr/bin/env python3
"""Create initial database migration."""

import subprocess
import sys
import os
from pathlib import Path

def create_initial_migration():
    """Create the initial migration file."""
    
    project_root = Path(__file__).parent.parent
    
    try:
        print("🔄 Creating initial migration...")
        
        # Change to project directory
        os.chdir(project_root)
        
        # Create initial migration
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", "-m", "Initial migration"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Initial migration created successfully")
            print(result.stdout)
        else:
            print("❌ Failed to create migration")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        return False
    
    return True

def run_migrations():
    """Run the migrations."""
    
    try:
        print("🔄 Running migrations...")
        
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
            print(result.stdout)
        else:
            print("❌ Migration failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # First create initial migration, then run it
    if create_initial_migration():
        run_migrations()
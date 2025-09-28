#!/usr/bin/env python3
"""
Migration Helper Script for Windows/Docker Environment

This script helps run Alembic migrations when there are connection issues
from Windows host to Docker PostgreSQL container.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_docker_command(command: str, description: str) -> bool:
    """Run a Docker command and return success status."""
    print(f"🔄 {description}...")
    
    # Construct the full Docker command
    docker_cmd = [
        "docker", "run", "--rm", 
        "--network", "docker_crm_network",
        "-v", f"{os.getcwd()}/alembic/versions:/app/alembic/versions",
        "-e", "DATABASE_URL=postgresql+asyncpg://crm_user:crm_password@postgres:5432/crm_db",
        "docker-api:latest"
    ] + command.split()
    
    try:
        result = subprocess.run(docker_cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False


def check_docker_environment() -> bool:
    """Check if Docker environment is ready."""
    print("🔍 Checking Docker environment...")
    
    # Check if Docker is running
    try:
        result = subprocess.run(["docker", "ps"], check=True, capture_output=True)
        print("✅ Docker is running")
    except subprocess.CalledProcessError:
        print("❌ Docker is not running. Please start Docker first.")
        return False
    
    # Check if PostgreSQL container is running
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres", "--format", "{{.Names}}"],
            check=True, capture_output=True, text=True
        )
        if "postgres" not in result.stdout:
            print("❌ PostgreSQL container is not running. Please start it with:")
            print("   cd docker && docker-compose up -d postgres")
            return False
        print("✅ PostgreSQL container is running")
    except subprocess.CalledProcessError:
        print("❌ Could not check PostgreSQL container status")
        return False
    
    # Check if API image exists
    try:
        result = subprocess.run(
            ["docker", "images", "--filter", "reference=docker-api", "--format", "{{.Repository}}"],
            check=True, capture_output=True, text=True
        )
        if "docker-api" not in result.stdout:
            print("❌ API Docker image not found. Please build it with:")
            print("   cd docker && docker-compose build api")
            return False
        print("✅ API Docker image is available")
    except subprocess.CalledProcessError:
        print("❌ Could not check API image status")
        return False
    
    return True


def main():
    """Main function to handle migration commands."""
    if len(sys.argv) < 2:
        print("🔧 Alembic Migration Helper for Windows/Docker")
        print("\nUsage:")
        print("  python migrate.py revision --autogenerate -m \"Migration message\"")
        print("  python migrate.py upgrade head")
        print("  python migrate.py downgrade -1")
        print("  python migrate.py current")
        print("  python migrate.py history")
        print("\nThis script runs Alembic commands inside Docker to avoid Windows connection issues.")
        return
    
    # Check Docker environment
    if not check_docker_environment():
        print("\n💡 To fix the environment:")
        print("1. Start Docker Desktop")
        print("2. cd docker && docker-compose up -d postgres")
        print("3. cd docker && docker-compose build api")
        sys.exit(1)
    
    # Extract alembic command
    alembic_args = " ".join(sys.argv[1:])
    command = f"alembic {alembic_args}"
    
    # Map common commands to descriptions
    if "revision" in alembic_args and "--autogenerate" in alembic_args:
        description = "Generating new migration"
    elif "upgrade" in alembic_args:
        description = "Applying migrations"
    elif "downgrade" in alembic_args:
        description = "Rolling back migrations"
    elif "current" in alembic_args:
        description = "Checking current migration version"
    elif "history" in alembic_args:
        description = "Showing migration history"
    else:
        description = "Running Alembic command"
    
    # Run the command
    success = run_docker_command(command, description)
    
    if not success:
        print("\n💡 Common troubleshooting:")
        print("- Make sure PostgreSQL container is running and healthy")
        print("- Check if the API image is built and up to date")
        print("- Verify the database connection parameters")
        sys.exit(1)
    
    print(f"\n✅ Migration operation completed successfully!")


if __name__ == "__main__":
    main()

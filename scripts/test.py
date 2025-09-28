#!/usr/bin/env python3
"""Windows-compatible Docker status checker."""

import subprocess
import sys
import time
import socket

def run_command(cmd, shell=True):
    """Run command and return result."""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker_containers():
    """Check Docker container status."""
    print("🔍 Checking Docker containers...")
    
    success, stdout, stderr = run_command("docker ps -a")
    if success:
        print("✅ Docker is running")
        print(stdout)
    else:
        print("❌ Docker is not running or accessible")
        print(f"Error: {stderr}")
        return False
    
    return True

def check_postgres_container():
    """Check PostgreSQL container specifically."""
    print("\n🐘 Checking PostgreSQL container...")
    
    # Check if postgres container exists and is running
    success, stdout, stderr = run_command('docker ps -q -f name=postgres')
    if not success or not stdout.strip():
        print("❌ PostgreSQL container not found or not running")
        return False
    
    container_id = stdout.strip()
    print(f"✅ PostgreSQL container found: {container_id}")
    
    # Test database connection
    success, stdout, stderr = run_command(f'docker exec {container_id} psql -U crm_user -d crm_db -c "SELECT 1"')
    if success:
        print("✅ PostgreSQL database is accessible")
        return True
    else:
        print("❌ PostgreSQL database is not accessible")
        print(f"Error: {stderr}")
        return False

def check_redis_container():
    """Check Redis container."""
    print("\n🔴 Checking Redis container...")
    
    success, stdout, stderr = run_command('docker ps -q -f name=redis')
    if not success or not stdout.strip():
        print("❌ Redis container not found or not running")
        return False
    
    container_id = stdout.strip()
    print(f"✅ Redis container found: {container_id}")
    
    # Test Redis connection
    success, stdout, stderr = run_command(f'docker exec {container_id} redis-cli ping')
    if success and "PONG" in stdout:
        print("✅ Redis is accessible")
        return True
    else:
        print("❌ Redis is not accessible")
        return False

def check_port_connectivity():
    """Check if ports are accessible from host."""
    print("\n🌐 Checking port connectivity...")
    
    ports = [
        (5432, "PostgreSQL"),
        (6379, "Redis"),
        (8000, "API (if running)")
    ]
    
    for port, service in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"✅ {service} port {port} is accessible")
            else:
                print(f"❌ {service} port {port} is not accessible")
        except Exception as e:
            print(f"❌ Error checking {service} port {port}: {e}")

def fix_suggestions():
    """Provide suggestions to fix Docker issues."""
    print("\n💡 Fix suggestions:")
    print("1. Restart Docker Desktop")
    print("2. Stop and start containers:")
    print("   docker-compose -f docker/docker-compose.yml down")
    print("   docker-compose -f docker/docker-compose.yml up -d postgres redis")
    print("3. Wait 30 seconds after starting containers")
    print("4. Check Docker Desktop resource allocation (Memory: 4GB+, Disk: 20GB+)")
    print("5. On Windows, try switching Docker Desktop to Windows containers and back to Linux containers")

def main():
    """Main function."""
    print("🚀 Docker Status Checker for Windows\n")
    
    issues = []
    
    if not check_docker_containers():
        issues.append("Docker not running")
    
    if not check_postgres_container():
        issues.append("PostgreSQL not accessible")
    
    if not check_redis_container():
        issues.append("Redis not accessible")
    
    check_port_connectivity()
    
    if issues:
        print(f"\n❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   - {issue}")
        fix_suggestions()
        return False
    else:
        print("\n✅ All Docker services are running correctly!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
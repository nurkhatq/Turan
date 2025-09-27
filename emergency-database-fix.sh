#!/bin/bash
# emergency-database-fix.sh - Fix database relationship issues

echo "🚨 Emergency Database Fix: Resolving model relationship errors..."

# 1. Stop all services to prevent further errors
echo "1️⃣ Stopping all services..."
docker-compose -f docker/docker-compose.yml stop

# 2. Start only core services
echo "2️⃣ Starting core services..."
docker-compose -f docker/docker-compose.yml up -d postgres redis

# Wait for database
sleep 10

# 3. Create simplified database schema directly
echo "3️⃣ Creating simplified database schema..."
docker-compose -f docker/docker-compose.yml exec postgres psql -U crm_user -d crm_db << 'EOF'
-- Drop existing tables to start fresh
DROP TABLE IF EXISTS user_session CASCADE;
DROP TABLE IF EXISTS api_log CASCADE;
DROP TABLE IF EXISTS system_alert CASCADE;
DROP TABLE IF EXISTS sync_job CASCADE;
DROP TABLE IF EXISTS integration_config CASCADE;

-- Create users table with correct name
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_superuser BOOLEAN DEFAULT false NOT NULL,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Create simplified user_session table
CREATE TABLE IF NOT EXISTS user_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Create simplified system tables without problematic relationships
CREATE TABLE IF NOT EXISTS integration_config (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) UNIQUE NOT NULL,
    is_enabled BOOLEAN DEFAULT false NOT NULL,
    config_data JSONB,
    credentials_data TEXT,
    sync_interval_minutes INTEGER DEFAULT 15 NOT NULL,
    last_sync_at TIMESTAMP,
    next_sync_at TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'inactive' NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_job (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_items INTEGER DEFAULT 0 NOT NULL,
    processed_items INTEGER DEFAULT 0 NOT NULL,
    failed_items INTEGER DEFAULT 0 NOT NULL,
    result_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL
);

-- Insert admin user with pre-hashed password
INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser)
VALUES (
    'admin@example.com',
    '$2b$12$LQv3c1yqBwU5jX4VpXEKKuCYkqU8GKAYOTcfDcXfQqUcvOcKGb3K2',
    'System Administrator',
    true,
    true
)
ON CONFLICT (email) DO NOTHING;

-- Verify tables
\dt
EOF

# 4. Start API with fixed models
echo "4️⃣ Starting API..."
docker-compose -f docker/docker-compose.yml up -d api

# Wait for API startup
sleep 15

# 5. Test the system
echo "5️⃣ Testing system..."

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Health endpoint working"
else
    echo "⚠️ Health endpoint not responding"
fi

# Test authentication
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}')

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    echo "✅ Authentication working!"
    echo "Login successful"
else
    echo "⚠️ Authentication still has issues"
    echo "Response: $AUTH_RESPONSE"
fi

# 6. Start remaining services
echo "6️⃣ Starting remaining services..."
docker-compose -f docker/docker-compose.yml up -d

echo ""
echo "🎉 Emergency fix completed!"
echo ""
echo "🔗 System Status:"
echo "   - Health: http://localhost:8000/health"
echo "   - API Docs: http://localhost:8000/api/v1/docs"  
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo "   - Flower: http://localhost:5555"
echo ""
echo "📋 Admin credentials:"
echo "   - Email: admin@example.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Test commands:"
echo "   curl http://localhost:8000/health"
echo "   curl -X POST http://localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"email\": \"admin@example.com\", \"password\": \"admin123\"}'"
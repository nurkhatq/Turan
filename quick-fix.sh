#!/bin/bash
# quick-fix.sh - Fix common CRM system issues

echo "🔧 Starting CRM System Quick Fix..."

# Stop all services first
echo "1️⃣ Stopping existing services..."
docker-compose -f docker/docker-compose.yml down

# Clean up any problematic containers
echo "2️⃣ Cleaning up containers..."
docker system prune -f

# Rebuild containers to pick up code changes
echo "3️⃣ Rebuilding containers..."
docker-compose -f docker/docker-compose.yml build --no-cache

# Start services in correct order
echo "4️⃣ Starting core services..."
docker-compose -f docker/docker-compose.yml up -d postgres redis

# Wait for services to be ready
echo "5️⃣ Waiting for services to initialize..."
sleep 15

# Start API service
echo "6️⃣ Starting API service..."
docker-compose -f docker/docker-compose.yml up -d api

# Wait for API to be ready
sleep 10

# Run database migrations
echo "7️⃣ Running database migrations..."
docker-compose -f docker/docker-compose.yml exec api alembic upgrade head

# Create admin user
echo "8️⃣ Creating admin user..."
docker-compose -f docker/docker-compose.yml exec api python scripts/create_admin.py

# Start remaining services
echo "9️⃣ Starting remaining services..."
docker-compose -f docker/docker-compose.yml up -d celery_worker celery_beat

# Start monitoring (optional)
echo "🔟 Starting monitoring services..."
docker-compose -f docker/docker-compose.yml up -d nginx grafana prometheus

echo ""
echo "✅ Quick fix completed!"
echo ""
echo "🔗 Services available at:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/v1/docs"
echo "   - Health Check: http://localhost:8000/health"
echo "   - Metrics: http://localhost:8000/metrics"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "📋 Admin credentials:"
echo "   - Email: admin@example.com"
echo "   - Password: admin123"
echo ""
echo "🧪 Test the system:"
echo "   curl http://localhost:8000/health"
echo ""
echo "📊 Check logs:"
echo "   docker-compose -f docker/docker-compose.yml logs -f api"
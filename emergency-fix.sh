#!/bin/bash
# emergency-fix.sh - Fix the psutil dependency issue

echo "🚨 Emergency Fix: Resolving psutil dependency issue..."

# Stop the failing API container
echo "1️⃣ Stopping API container..."
docker-compose -f docker/docker-compose.yml stop api

# Option 1: Add psutil to requirements.txt (recommended)
echo "2️⃣ Adding psutil to requirements.txt..."
if ! grep -q "psutil" requirements.txt; then
    echo "psutil==5.9.6" >> requirements.txt
    echo "✅ Added psutil to requirements.txt"
else
    echo "✅ psutil already in requirements.txt"
fi

# Rebuild only the API container
echo "3️⃣ Rebuilding API container..."
docker-compose -f docker/docker-compose.yml build --no-cache api

# Start API container
echo "4️⃣ Starting API container..."
docker-compose -f docker/docker-compose.yml up -d api

# Wait for API to be ready
echo "5️⃣ Waiting for API to start..."
sleep 15

# Check if API is running
echo "6️⃣ Checking API status..."
if docker-compose -f docker/docker-compose.yml ps api | grep -q "Up"; then
    echo "✅ API container is running!"
    
    # Run migrations
    echo "7️⃣ Running database migrations..."
    docker-compose -f docker/docker-compose.yml exec api alembic upgrade head
    
    # Create admin user
    echo "8️⃣ Creating admin user..."
    docker-compose -f docker/docker-compose.yml exec api python scripts/create_admin.py
    
    # Test the health endpoint
    echo "9️⃣ Testing health endpoint..."
    sleep 5
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Health endpoint is working!"
    else
        echo "⚠️ Health endpoint not responding yet, give it a few more seconds..."
    fi
    
    echo ""
    echo "🎉 Emergency fix completed!"
    echo "🔗 Try these endpoints:"
    echo "   - Health: http://localhost:8000/health"
    echo "   - Metrics: http://localhost:8000/metrics"
    echo "   - API Docs: http://localhost:8000/api/v1/docs"
    echo ""
    echo "📋 Admin credentials:"
    echo "   - Email: admin@example.com"
    echo "   - Password: admin123"
    
else
    echo "❌ API container failed to start. Check logs:"
    echo "   docker-compose -f docker/docker-compose.yml logs api"
fi
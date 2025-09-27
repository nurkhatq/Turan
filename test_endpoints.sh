# Complete API Testing Guide
# =========================

# First, let's set some variables for easier testing
export API_BASE="http://localhost:8000/api/v1"
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="admin123"

# 1. HEALTH CHECK
# ===============
echo "🔍 Testing Health Check..."
curl -X GET "http://localhost:8000/health" \
  -H "accept: application/json" | jq

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0"
# }

# 2. AUTHENTICATION
# =================
echo "🔐 Testing Authentication..."

# Login and get access token
echo "Login as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$ADMIN_EMAIL'",
    "password": "'$ADMIN_PASSWORD'"
  }')

echo "Login response:"
echo $LOGIN_RESPONSE | jq

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Access Token: $ACCESS_TOKEN"

# Test authenticated endpoint
echo "Testing authenticated endpoint..."
curl -X GET "$API_BASE/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# 3. MOYSKLAD INTEGRATION TESTING
# ===============================
echo "🔗 Testing MoySklad Integration..."

# First, configure MoySklad integration (replace with your actual token)
echo "Configuring MoySklad integration..."
curl -X PUT "$API_BASE/admin/integrations/moysklad" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_enabled": true,
    "sync_interval_minutes": 15,
    "credentials_data": {
      "token": "YOUR_ACTUAL_MOYSKLAD_TOKEN_HERE"
    }
  }' | jq

# Test MoySklad connection
echo "Testing MoySklad connection..."
curl -X POST "$API_BASE/admin/integrations/test?service_name=moysklad" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Expected response if token is valid:
# {
#   "success": true,
#   "message": "Connection successful. Access to X organizations.",
#   "organizations_count": 1,
#   "auth_method": "token"
# }

# 4. START MOYSKLAD SYNCHRONIZATION
# =================================
echo "🔄 Starting MoySklad Synchronization..."

# Start full sync
echo "Starting full MoySklad synchronization..."
SYNC_RESPONSE=$(curl -s -X POST "$API_BASE/admin/sync/start" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "moysklad",
    "job_type": "full_sync",
    "force_full_sync": true
  }')

echo "Sync job started:"
echo $SYNC_RESPONSE | jq

# Extract job ID
JOB_ID=$(echo $SYNC_RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# Check sync job status
echo "Checking sync job status..."
curl -X GET "$API_BASE/admin/sync/jobs?service_name=moysklad" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# 5. CHECK SYNCHRONIZED DATA
# ==========================
echo "📊 Checking Synchronized Data..."

# Wait a bit for sync to process (adjust timing as needed)
echo "Waiting 30 seconds for sync to process..."
sleep 30

# Check products
echo "Fetching products..."
curl -X GET "$API_BASE/products/?page=1&limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Check product folders/categories
echo "Fetching product folders..."
curl -X GET "$API_BASE/products/folders/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Check counterparties (customers/suppliers)
echo "Fetching counterparties..."
curl -X GET "$API_BASE/counterparties/?page=1&limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Check inventory/stock
echo "Fetching inventory..."
curl -X GET "$API_BASE/inventory/stock?page=1&limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Check stores/warehouses
echo "Fetching stores..."
curl -X GET "$API_BASE/inventory/stores" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# 6. ANALYTICS AND DASHBOARD
# ==========================
echo "📈 Testing Analytics..."

# Get dashboard metrics
echo "Fetching dashboard metrics..."
curl -X GET "$API_BASE/analytics/dashboard" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Get sales report (last 30 days)
echo "Fetching sales report..."
START_DATE=$(date -d "30 days ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)

curl -X GET "$API_BASE/analytics/sales/report?period_type=monthly&start_date=$START_DATE&end_date=$END_DATE" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Get inventory report
echo "Fetching inventory report..."
curl -X GET "$API_BASE/analytics/inventory/report" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# 7. SEARCH AND FILTERING
# =======================
echo "🔍 Testing Search and Filtering..."

# Search products by name
echo "Searching products..."
curl -X GET "$API_BASE/products/?search=test&page=1&limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Filter products by price range
echo "Filtering products by price..."
curl -X GET "$API_BASE/products/?min_price=100&max_price=1000&page=1&limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Filter stock by store
echo "Filtering stock by store..."
# First get a store ID, then use it
STORE_ID=$(curl -s -X GET "$API_BASE/inventory/stores" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.[0].id // 1')

curl -X GET "$API_BASE/inventory/stock?store_id=$STORE_ID&page=1&limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# 8. USER MANAGEMENT (ADMIN)
# ==========================
echo "👥 Testing User Management..."

# Get all users
echo "Fetching all users..."
curl -X GET "$API_BASE/admin/users?page=1&limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Create a new user
echo "Creating new user..."
curl -X POST "$API_BASE/admin/users" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpassword123",
    "is_active": true,
    "role_ids": []
  }' | jq

# 9. SYSTEM MONITORING
# ====================
echo "🖥️ Testing System Monitoring..."

# Get system health
echo "Checking system health..."
curl -X GET "$API_BASE/admin/health" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Get system alerts
echo "Fetching system alerts..."
curl -X GET "$API_BASE/admin/alerts" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# Get integration configurations
echo "Fetching integration configurations..."
curl -X GET "$API_BASE/admin/integrations" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# 10. TEST SPECIFIC PRODUCT
# =========================
echo "🎯 Testing Specific Product..."

# Get first product ID and fetch its details
PRODUCT_ID=$(curl -s -X GET "$API_BASE/products/?page=1&limit=1" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.items[0].id // 1')

echo "Fetching product ID: $PRODUCT_ID"
curl -X GET "$API_BASE/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "accept: application/json" | jq

# 11. CELERY MONITORING
# =====================
echo "⚙️ Testing Celery Tasks..."

# Check if Flower is running (Celery monitoring)
echo "Checking Celery Flower status..."
curl -s "http://localhost:5555/api/workers" | jq

# Manual task execution test
echo "Testing manual task execution..."
curl -X POST "$API_BASE/admin/sync/start" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "moysklad",
    "job_type": "incremental_sync"
  }' | jq

# 12. ERROR HANDLING TESTS
# ========================
echo "❌ Testing Error Handling..."

# Test with invalid token
echo "Testing with invalid token..."
curl -X GET "$API_BASE/auth/me" \
  -H "Authorization: Bearer invalid_token" \
  -H "accept: application/json" | jq

# Test with missing required fields
echo "Testing with invalid login..."
curl -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "wrong@example.com",
    "password": "wrongpassword"
  }' | jq

# Test rate limiting (make rapid requests)
echo "Testing rate limiting..."
for i in {1..5}; do
  curl -s -X GET "http://localhost:8000/health" > /dev/null
  echo "Request $i sent"
done

echo "🎉 API Testing Complete!"
echo ""
echo "Summary of what to check:"
echo "========================"
echo "1. ✅ Health check should return status: healthy"
echo "2. ✅ Authentication should return access_token"
echo "3. ✅ MoySklad connection test should show success: true"
echo "4. ✅ Sync jobs should be created and processed"
echo "5. ✅ Products, stores, counterparties should be fetched from MoySklad"
echo "6. ✅ Data should be stored in your database"
echo "7. ✅ Analytics should show basic metrics"
echo "8. ✅ Search and filtering should work"
echo "9. ✅ Admin functions should be accessible"
echo "10. ✅ System monitoring should show healthy status"

# BONUS: Database Verification
# ============================
echo ""
echo "🗄️ Database Verification (run these in your database):"
echo "======================================================"
echo "-- Check if products were synced:"
echo "SELECT COUNT(*) as product_count FROM product;"
echo ""
echo "-- Check if counterparties were synced:"
echo "SELECT COUNT(*) as counterparty_count FROM counterparty;"
echo ""
echo "-- Check sync job history:"
echo "SELECT * FROM sync_job ORDER BY created_at DESC LIMIT 5;"
echo ""
echo "-- Check latest products:"
echo "SELECT id, name, external_id, last_sync_at FROM product ORDER BY created_at DESC LIMIT 5;"
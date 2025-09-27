# test_moysklad_specific.sh
#!/bin/bash
# Specific MoySklad Integration Testing Script

echo "🔗 MoySklad Integration Test Script"
echo "==================================="

# Set your actual MoySklad token here
MOYSKLAD_TOKEN="105d4f38eb9a02400c3a6428ea71640babe37e98"
API_BASE="http://localhost:8000/api/v1"

# Login and get token
echo "🔐 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" = "null" ]; then
    echo "❌ Login failed!"
    exit 1
fi

echo "✅ Login successful"

# Configure MoySklad
echo "⚙️ Configuring MoySklad integration..."
curl -s -X PUT "$API_BASE/admin/integrations/moysklad" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_enabled": true,
    "sync_interval_minutes": 15,
    "credentials_data": {
      "token": "'$MOYSKLAD_TOKEN'"
    }
  }' > /dev/null

# Test connection
echo "🔍 Testing MoySklad connection..."
CONNECTION_TEST=$(curl -s -X POST "$API_BASE/admin/integrations/test?service_name=moysklad" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Connection test result:"
echo $CONNECTION_TEST | jq

if [ "$(echo $CONNECTION_TEST | jq -r '.success')" = "true" ]; then
    echo "✅ MoySklad connection successful!"
    
    # Start sync
    echo "🔄 Starting data synchronization..."
    SYNC_RESPONSE=$(curl -s -X POST "$API_BASE/admin/sync/start" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "service_name": "moysklad",
        "job_type": "full_sync",
        "force_full_sync": true
      }')
    
    echo "Sync started:"
    echo $SYNC_RESPONSE | jq
    
    # Wait and check results
    echo "⏳ Waiting 60 seconds for sync to complete..."
    sleep 60
    
    # Check sync status
    echo "📊 Checking sync results..."
    curl -s -X GET "$API_BASE/admin/sync/jobs?service_name=moysklad" \
      -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.[0]'
    
    # Check synced data
    echo "📦 Checking synced products..."
    PRODUCTS=$(curl -s -X GET "$API_BASE/products/?page=1&limit=5" \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    PRODUCT_COUNT=$(echo $PRODUCTS | jq '.total')
    echo "Total products synced: $PRODUCT_COUNT"
    
    if [ "$PRODUCT_COUNT" -gt "0" ]; then
        echo "✅ Products successfully synced!"
        echo "Sample products:"
        echo $PRODUCTS | jq '.items[0:3] | .[] | {id, name, external_id, last_sync_at}'
    else
        echo "⚠️ No products found. Check your MoySklad account or sync logs."
    fi
    
    # Check counterparties
    echo "👥 Checking synced counterparties..."
    COUNTERPARTIES=$(curl -s -X GET "$API_BASE/counterparties/?page=1&limit=5" \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    CP_COUNT=$(echo $COUNTERPARTIES | jq '.total // 0')
    echo "Total counterparties synced: $CP_COUNT"
    
    # Check stores
    echo "🏪 Checking synced stores..."
    STORES=$(curl -s -X GET "$API_BASE/inventory/stores" \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    STORE_COUNT=$(echo $STORES | jq 'length')
    echo "Total stores synced: $STORE_COUNT"
    
    if [ "$STORE_COUNT" -gt "0" ]; then
        echo "Sample stores:"
        echo $STORES | jq '.[0:2] | .[] | {id, name, external_id}'
    fi
    
else
    echo "❌ MoySklad connection failed!"
    echo "Please check your token and try again."
fi
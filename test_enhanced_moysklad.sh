#!/bin/bash
# test_enhanced_moysklad.sh
# Test script for enhanced MoySklad integration

echo "🚀 Testing Enhanced MoySklad Integration"
echo "========================================"

# Configuration
API_BASE="http://localhost:8000/api/v1"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin123"
MOYSKLAD_TOKEN="105d4f38eb9a02400c3a6428ea71640babe37e98"  # Replace with your token

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Function to test API endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET \
            "$API_BASE/$endpoint" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -H "accept: application/json")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            "$API_BASE/$endpoint" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract response body (all except last line)
    body=$(echo "$response" | head -n-1)
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        print_status 0 "$description (Status: $status_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 0
    else
        print_status 1 "$description (Status: $status_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 1
    fi
}

# Step 1: Login
echo -e "\n${YELLOW}Step 1: Authentication${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
    print_status 0 "Login successful"
else
    print_status 1 "Login failed"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

# Step 2: Configure MoySklad
echo -e "\n${YELLOW}Step 2: Configure MoySklad Integration${NC}"
CONFIG_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$API_BASE/admin/integrations/moysklad" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"is_enabled\": true,
        \"sync_interval_minutes\": 15,
        \"credentials_data\": {
            \"token\": \"$MOYSKLAD_TOKEN\"
        }
    }")

status_code=$(echo "$CONFIG_RESPONSE" | tail -n1)
if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
    print_status 0 "MoySklad configured"
else
    print_status 1 "Failed to configure MoySklad"
fi

# Step 3: Test Connection
echo -e "\n${YELLOW}Step 3: Test MoySklad Connection${NC}"
CONNECTION_TEST=$(curl -s -X POST "$API_BASE/admin/integrations/test?service_name=moysklad" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$(echo $CONNECTION_TEST | jq -r '.success')" = "true" ]; then
    print_status 0 "MoySklad connection successful"
    echo "Organizations found: $(echo $CONNECTION_TEST | jq -r '.organizations_count')"
else
    print_status 1 "MoySklad connection failed"
    echo "$CONNECTION_TEST" | jq
fi

# Step 4: Run Enhanced Full Sync
echo -e "\n${YELLOW}Step 4: Starting Enhanced Full Synchronization${NC}"
echo "This will sync:"
echo "  - Organizations & Employees"
echo "  - Projects & Contracts"
echo "  - Currencies & Countries"
echo "  - Products, Services & Stock"
echo "  - Counterparties & Stores"

SYNC_RESPONSE=$(curl -s -X POST "$API_BASE/admin/sync/start" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "service_name": "moysklad",
        "job_type": "enhanced_full_sync",
        "force_full_sync": true,
        "options": {
            "sync_organizations": true,
            "sync_employees": true,
            "sync_projects": true,
            "sync_contracts": true,
            "sync_currencies": true,
            "sync_countries": true,
            "resolve_foreign_keys": true
        }
    }')

JOB_ID=$(echo $SYNC_RESPONSE | jq -r '.job_id')
if [ "$JOB_ID" != "null" ] && [ -n "$JOB_ID" ]; then
    print_status 0 "Sync job started (ID: $JOB_ID)"
else
    print_status 1 "Failed to start sync"
    echo "$SYNC_RESPONSE" | jq
fi

# Step 5: Wait for sync to complete
echo -e "\n${YELLOW}Step 5: Waiting for sync to complete...${NC}"
echo "This may take several minutes depending on data volume"

for i in {1..30}; do
    sleep 10
    echo -n "."
    
    JOB_STATUS=$(curl -s -X GET "$API_BASE/admin/sync/jobs/$JOB_ID" \
        -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.status')
    
    if [ "$JOB_STATUS" = "completed" ]; then
        echo ""
        print_status 0 "Sync completed successfully!"
        break
    elif [ "$JOB_STATUS" = "failed" ]; then
        echo ""
        print_status 1 "Sync failed!"
        break
    fi
done

# Step 6: Test new endpoints
echo -e "\n${YELLOW}Step 6: Testing New Endpoints${NC}"

# Test Organizations endpoint
test_endpoint "GET" "organizations" "Fetching organizations"

# Test Employees endpoint
test_endpoint "GET" "employees" "Fetching employees"

# Test Projects endpoint  
test_endpoint "GET" "projects" "Fetching projects"

# Test Contracts endpoint
test_endpoint "GET" "contracts" "Fetching contracts"

# Test Currencies endpoint
test_endpoint "GET" "currencies" "Fetching currencies"

# Test Countries endpoint
test_endpoint "GET" "countries" "Fetching countries"

# Step 7: Verify data counts
echo -e "\n${YELLOW}Step 7: Data Statistics${NC}"
STATS=$(curl -s -X GET "$API_BASE/admin/sync/statistics" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Sync Statistics:"
echo "$STATS" | jq

# Step 8: Test foreign key resolution
echo -e "\n${YELLOW}Step 8: Verify Foreign Key Relationships${NC}"

# Get a contract with resolved relationships
CONTRACT=$(curl -s -X GET "$API_BASE/contracts?expand=counterparty,organization,project&limit=1" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$(echo $CONTRACT | jq '.items | length')" -gt 0 ]; then
    print_status 0 "Foreign key relationships resolved"
    echo "Sample contract with relationships:"
    echo "$CONTRACT" | jq '.items[0] | {
        name: .name,
        counterparty: .counterparty.name,
        organization: .organization.name,
        project: .project.name
    }'
else
    print_status 1 "No contracts found to verify relationships"
fi

# Step 9: Test Reports
echo -e "\n${YELLOW}Step 9: Testing Report Endpoints${NC}"

# Test sales dashboard
test_endpoint "GET" "reports/dashboard/sales" "Sales dashboard"

# Test profit report
test_endpoint "GET" "reports/profit/by-product?date_from=2024-01-01&date_to=2024-12-31" "Profit by product report"

# Final Summary
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${GREEN}Enhanced MoySklad Integration Test Complete!${NC}"
echo -e "${YELLOW}========================================${NC}"

echo -e "\nNext Steps:"
echo "1. Check the API documentation at http://localhost:8000/api/v1/docs"
echo "2. Verify data in the database"
echo "3. Set up periodic sync schedules"
echo "4. Configure webhooks for real-time updates"
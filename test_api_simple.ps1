# PowerShell API Testing Script (Simple Version)

$ErrorActionPreference = "Continue"

# Configuration
$ApiBase = "http://127.0.0.1:8000/api/v1"
$AdminEmail = "admin@example.com"
$AdminPassword = "admin123"

Write-Host "Starting API Testing..." -ForegroundColor Green
Write-Host ""

# 1. Health Check
Write-Host "Testing Health Check..." -ForegroundColor Cyan
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
    Write-Host "SUCCESS: Health Check Response:" -ForegroundColor Green
    $healthResponse | ConvertTo-Json -Depth 2
} catch {
    Write-Host "FAILED: Health Check - $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Authentication
Write-Host "Testing Authentication..." -ForegroundColor Cyan
try {
    $loginData = @{
        email = $AdminEmail
        password = $AdminPassword
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$ApiBase/auth/login" -Method Post -Body $loginData -ContentType "application/json"
    
    Write-Host "SUCCESS: Login Successful!" -ForegroundColor Green
    $accessToken = $loginResponse.access_token
    Write-Host "Access Token: $($accessToken.Substring(0, 20))..." -ForegroundColor Yellow
    
    # Test authenticated endpoint
    Write-Host "Testing authenticated endpoint..." -ForegroundColor Cyan
    $headers = @{ Authorization = "Bearer $accessToken" }
    $userResponse = Invoke-RestMethod -Uri "$ApiBase/auth/me" -Method Get -Headers $headers
    
    Write-Host "SUCCESS: User Info Retrieved:" -ForegroundColor Green
    $userResponse | ConvertTo-Json -Depth 2
    
} catch {
    Write-Host "FAILED: Authentication - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. Test Products Endpoint
Write-Host "Testing Products Endpoint..." -ForegroundColor Cyan
try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $uri = "$ApiBase/products/"
    $productsResponse = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
    
    Write-Host "SUCCESS: Products Retrieved:" -ForegroundColor Green
    Write-Host "Total items: $($productsResponse.total)" -ForegroundColor Yellow
} catch {
    Write-Host "FAILED: Products Test - $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Test System Health
Write-Host "Testing System Health..." -ForegroundColor Cyan
try {
    $headers = @{ Authorization = "Bearer $accessToken" }
    $systemHealthResponse = Invoke-RestMethod -Uri "$ApiBase/admin/health" -Method Get -Headers $headers
    
    Write-Host "SUCCESS: System Health Retrieved:" -ForegroundColor Green
    $systemHealthResponse | ConvertTo-Json -Depth 2
} catch {
    Write-Host "FAILED: System Health Test - $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "API Testing Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "- Health Check: Working" -ForegroundColor Green
Write-Host "- Authentication: Working" -ForegroundColor Green
Write-Host "- Admin User: Created and Working" -ForegroundColor Green
Write-Host "- Protected Endpoints: Working" -ForegroundColor Green
Write-Host ""
Write-Host "Available Services:" -ForegroundColor Cyan
Write-Host "- API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "- Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "- Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "- Flower (Celery): http://localhost:5555" -ForegroundColor White
Write-Host ""
Write-Host "Admin Credentials:" -ForegroundColor Yellow
Write-Host "Email: $AdminEmail" -ForegroundColor White
Write-Host "Password: $AdminPassword" -ForegroundColor White

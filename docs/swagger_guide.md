# 🚀 **Swagger UI Guide for Your MoySklad CRM**

Access your API documentation at: **http://127.0.0.1:8000/docs**

## 🔐 **Step 1: Authorization**

### Get Access Token:
1. **Login Endpoint**: `POST /api/v1/auth/login`
2. **Credentials**:
   ```json
   {
     "email": "admin@example.com",
     "password": "admin123"
   }
   ```

### Authorize in Swagger:
1. Click the **🔒 Authorize** button (top right)
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click **Authorize**

## 📊 **Step 2: View Your MoySklad Data**

### 🏪 **Your Stores/Warehouses**
- **Endpoint**: `GET /api/v1/inventory/stores`
- **Description**: See all 6 warehouses (Склад Китай, Склад Россия, etc.)

### 🛍️ **Products**  
- **Endpoint**: `GET /api/v1/products/`
- **Parameters**: 
  - `page`: 1
  - `limit`: 50
  - `search`: (optional) search products

### 📈 **Analytics Dashboard**
- **Endpoint**: `GET /api/v1/analytics/dashboard`
- **Description**: Business metrics and KPIs

### 🔧 **Admin Functions**
- **View Integrations**: `GET /api/v1/admin/integrations`
- **System Health**: `GET /api/v1/admin/system/health`
- **Start Sync**: `POST /api/v1/admin/sync/start`

## 🎯 **Quick Test Sequence**

1. **Login** → Get your token
2. **Authorize** → Add token to Swagger
3. **Check Stores** → `/inventory/stores` to see your warehouses
4. **View Dashboard** → `/analytics/dashboard` for metrics
5. **Check Integration** → `/admin/integrations` to see MoySklad status

## 📝 **Available Tags in Swagger**

- **Authentication** - Login/logout
- **Administration** - Admin controls, sync jobs
- **Inventory** - Stores, stock levels
- **Products** - Product catalog
- **Analytics** - Business metrics
- **Users** - User management

Your data is LIVE and ready to explore! 🚀

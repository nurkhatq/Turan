# 🚀 Complete Setup Guide - Business CRM System

## 📋 Prerequisites

- Docker & Docker Compose installed
- Node.js 20+ (for local development)
- PostgreSQL 15+ (if running locally)
- Redis 7+ (if running locally)

## 🏗️ Project Structure

```
business-crm-system/
├── app/                    # Backend (FastAPI)
├── frontend/               # Frontend (Next.js) - NEW!
├── docker/                 # Docker configs
├── alembic/               # Database migrations
├── tests/                 # Backend tests
├── scripts/               # Setup scripts
├── docker-compose.yml     # UPDATED with frontend
└── README.md
```

## 🎯 Quick Start (Recommended)

### Step 1: Update Docker Compose

Add the frontend service to your `docker/docker-compose.yml`:

```yaml
services:
  # ... existing services (postgres, redis, api, etc.) ...

  # Next.js Frontend (ADD THIS)
  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
      - NEXT_PUBLIC_APP_NAME=Business CRM System
    ports:
      - "3000:3000"
    depends_on:
      - api
    networks:
      - crm_network
    volumes:
      - ../frontend:/app
      - /app/node_modules
      - /app/.next
    restart: unless-stopped
```

### Step 2: Create Frontend Directory

```bash
# From project root
mkdir frontend
cd frontend
```

### Step 3: Copy All Frontend Files

Copy all the files I provided into the `frontend/` directory:

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/login/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── products/page.tsx
│   │   │   ├── inventory/stock/page.tsx
│   │   │   ├── analytics/dashboard/page.tsx
│   │   │   ├── organizations/page.tsx
│   │   │   └── admin/integrations/page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   └── input-badge.tsx
│   │   └── providers.tsx
│   ├── lib/
│   │   ├── api/client.ts
│   │   ├── hooks/use-api.ts
│   │   ├── store/auth.ts
│   │   ├── types/api.ts
│   │   └── utils.ts
│   └── styles/
│       └── globals.css
├── public/
├── .env.local
├── .dockerignore
├── .eslintrc.json
├── .gitignore
├── Dockerfile
├── next.config.js
├── package.json
├── postcss.config.js
├── tailwind.config.ts
├── tsconfig.json
└── README.md
```

### Step 4: Install Dependencies (Local Dev)

```bash
cd frontend
npm install
```

### Step 5: Start Everything with Docker

```bash
# From project root
docker-compose -f docker/docker-compose.yml up --build
```

This will start:
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ FastAPI Backend (port 8000)
- ✅ Celery Workers
- ✅ Next.js Frontend (port 3000) 🆕

### Step 6: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

**Default Login:**
- Email: `admin@example.com`
- Password: `admin123`

## 🔧 Development Workflow

### Option 1: Full Docker (Recommended for Quick Start)

```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f frontend
docker-compose logs -f api

# Stop all
docker-compose down
```

### Option 2: Mixed (Frontend Local, Backend Docker)

```bash
# Start backend services
docker-compose up postgres redis api celery_worker celery_beat

# In another terminal, start frontend locally
cd frontend
npm run dev
```

Update `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Option 3: Full Local Development

#### Backend:
```bash
# Setup Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create admin user
python scripts/create_admin.py

# Start server
uvicorn app.main:app --reload
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## 🗄️ Database Setup

### Initialize Database

```bash
# Using Docker
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/create_admin.py

# Or locally
cd /path/to/project
alembic upgrade head
python scripts/create_admin.py
```

### Run Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Your message"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🔌 MoySklad Integration

### Step 1: Get API Credentials

1. Login to МойСклад
2. Go to Settings → API → Tokens
3. Create new token or use username/password

### Step 2: Configure Integration

Navigate to: http://localhost:3000/admin/integrations

1. Click "Включить" (Enable) for MoySklad
2. Enter your credentials
3. Click "Проверить соединение" (Test Connection)
4. Click "Полная синхронизация" (Full Sync)

### Step 3: Monitor Sync

Watch the sync progress in the admin panel. First sync may take several minutes depending on your data volume.

## 📊 Accessing Different Modules

### Dashboard
- URL: http://localhost:3000/dashboard
- Shows: Revenue, orders, top products, alerts

### Products
- URL: http://localhost:3000/products
- Shows: Product catalog with search and filters

### Inventory
- URL: http://localhost:3000/inventory/stock
- Shows: Stock levels, warehouse selection

### Analytics
- URL: http://localhost:3000/analytics/dashboard
- Shows: Sales, orders, and money dashboards

### Organizations
- URL: http://localhost:3000/organizations
- Shows: Companies, employees, projects, contracts

### Admin
- URL: http://localhost:3000/admin/integrations
- Shows: System health, integrations, sync controls

## 🐛 Troubleshooting

### Frontend won't start

```bash
# Check logs
docker-compose logs frontend

# Rebuild
docker-compose build frontend
docker-compose up frontend

# Or locally
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Backend connection error

Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`:
- Docker: `http://api:8000`
- Local: `http://localhost:8000`

### Database connection error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

### Can't login

```bash
# Recreate admin user
docker-compose exec api python scripts/create_admin.py
```

### Port conflicts

If ports 3000, 8000, 5432, or 6379 are in use:

```bash
# Check what's using ports
# Linux/Mac
lsof -i :3000
lsof -i :8000

# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Change ports in docker-compose.yml
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # Backend
```

## 🔐 Security Notes

### Development
- Default credentials are for development only
- JWT secrets are basic examples
- CORS is open for development

### Production
- Change all secrets and passwords
- Configure proper CORS origins
- Use HTTPS
- Set secure JWT secrets
- Enable authentication properly
- Use environment-specific configs

## 📦 Production Deployment

### Docker Production Build

```bash
# Build production images
docker-compose -f docker/docker-compose.prod.yml build

# Start production
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Environment Variables

Create `.env.production`:

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/crm_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-production-key
MOYSKLAD_TOKEN=your-moysklad-token

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=Your Company CRM
```

## 🎨 Customization

### Branding

**Frontend:**
- Edit `frontend/src/app/layout.tsx` - Change title
- Edit `frontend/tailwind.config.ts` - Change colors
- Edit `frontend/src/styles/globals.css` - Change theme

**Backend:**
- Edit `app/core/config.py` - Change app name

### Adding New Pages

1. Create file in `frontend/src/app/(dashboard)/your-page/page.tsx`
2. Add route to navigation in `frontend/src/app/(dashboard)/layout.tsx`
3. Create API endpoint in backend if needed
4. Add API hook in `frontend/src/lib/hooks/use-api.ts`

## 📚 Additional Resources

- **Backend Docs:** `/docs/PROJECT_README.md`
- **Frontend Docs:** `/frontend/README.md`
- **API Docs:** http://localhost:8000/docs
- **MoySklad API:** https://dev.moysklad.ru/doc/api/remap/1.2/

## 🆘 Getting Help

1. Check logs: `docker-compose logs [service]`
2. Verify all services running: `docker-compose ps`
3. Check API health: http://localhost:8000/health
4. Review error messages carefully
5. Ensure all environment variables are set

## ✅ Verification Checklist

After setup, verify:

- [ ] PostgreSQL is running (port 5432)
- [ ] Redis is running (port 6379)
- [ ] Backend API is accessible (http://localhost:8000)
- [ ] API docs load (http://localhost:8000/docs)
- [ ] Frontend loads (http://localhost:3000)
- [ ] Can login with admin credentials
- [ ] Dashboard shows (may be empty initially)
- [ ] Can access all menu items
- [ ] MoySklad integration is configurable
- [ ] Can run sync successfully

## 🎉 You're All Set!

Your Business CRM System is now running with:
- ✅ Modern Next.js frontend
- ✅ FastAPI backend
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Celery task queue
- ✅ MoySklad integration
- ✅ Full Docker support

Happy coding! 🚀
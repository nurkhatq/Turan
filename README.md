# Business CRM System

Comprehensive backend architecture for a scalable business CRM system with MoySklad integration, designed for Russian-speaking businesses.

## Features

### Core Functionality
- 🔐 **JWT-based Authentication** with role-based access control
- 📊 **Advanced Analytics** with real-time business insights
- 🔄 **MoySklad Integration** with automatic data synchronization
- 📦 **Inventory Management** with stock tracking and alerts
- 👥 **Customer Management** with segmentation and analytics
- 💰 **Sales Analytics** with profit calculations and trends
- 🔔 **Real-time Notifications** and alerts system
- 📈 **Dashboard** with key business metrics

### Technical Features
- ⚡ **FastAPI** with async/await support
- 🗄️ **PostgreSQL** with SQLAlchemy ORM
- 🚀 **Redis** for caching and message queuing
- 🔄 **Celery** for background tasks
- 🐳 **Docker** for containerization
- 📊 **Prometheus + Grafana** for monitoring
- 🧪 **Comprehensive testing** with pytest
- 🔍 **Structured logging** with request tracing

### Integration Support
- ✅ **MoySklad** (implemented)
- 🔜 **Kaspi** (planned)
- 🔜 **Bitrix24** (planned)
- 🔌 **Plugin architecture** for easy extensions

## Quick Start

### Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd business-crm-backend
```

2. **Copy environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start development environment**
```bash
make setup
```

This will:
- Start PostgreSQL, Redis, and all services
- Run database migrations
- Initialize database tables
- Create admin user

4. **Access the system**
- API Documentation: http://localhost:8000/api/v1/docs
- Admin Login: admin@example.com / admin123
- Flower (Celery monitoring): http://localhost:5555
- Grafana Dashboard: http://localhost:3000 (admin/admin)

### Production Deployment

1. **Configure production environment**
```bash
cp .env.example .env.prod
# Edit .env.prod with production values
```

2. **Deploy with Docker Compose**
```bash
make prod-setup
```

## API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user info

### Product Management
- `GET /api/v1/products/` - List products with filters
- `GET /api/v1/products/{id}` - Get product details
- `GET /api/v1/products/folders/` - Get product categories

### Inventory Management
- `GET /api/v1/inventory/stock` - Get stock levels
- `GET /api/v1/inventory/stores` - Get warehouses

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/sales/report` - Sales reports
- `GET /api/v1/analytics/inventory/report` - Inventory reports

### Administration
- `GET /api/v1/admin/users` - User management
- `GET /api/v1/admin/integrations` - Integration config
- `POST /api/v1/admin/sync/start` - Start sync jobs
- `GET /api/v1/admin/health` - System health

## Architecture

### Database Schema
```
Users & Roles
├── users (email, roles, permissions)
├── roles (dynamic role definitions)
└── user_sessions (JWT session tracking)

MoySklad Entities
├── products (with variants and pricing)
├── services (service catalog)
├── counterparties (customers/suppliers)
├── stores (warehouses)
├── stock (inventory levels)
├── sales_documents (orders, invoices)
└── purchase_documents (supplies, orders)

Analytics & System
├── product_analytics (calculated metrics)
├── customer_analytics (segmentation)
├── sales_analytics (business metrics)
├── sync_jobs (integration tracking)
├── api_logs (request logging)
└── system_alerts (notifications)
```

### Service Architecture
```
API Layer (FastAPI)
├── Authentication & Authorization
├── Request/Response Validation
├── Rate Limiting
└── API Documentation

Business Logic Layer
├── User Management Service
├── Analytics Service
├── Integration Services
└── Notification Service

Data Layer
├── SQLAlchemy Models
├── Database Migrations
├── Redis Caching
└── Background Tasks (Celery)

Integration Layer
├── MoySklad Client
├── Data Mapping Service
├── Sync Service
└── Webhook Handlers
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `SECRET_KEY` | Application secret key | Required |
| `JWT_SECRET_KEY` | JWT signing key | Required |
| `MOYSKLAD_USERNAME` | MoySklad username | Optional |
| `MOYSKLAD_PASSWORD` | MoySklad password | Optional |
| `MOYSKLAD_TOKEN` | MoySklad API token | Optional |
| `MOYSKLAD_SYNC_INTERVAL_MINUTES` | Sync interval | 15 |

### MoySklad Integration Setup

1. **Get API credentials** from MoySklad admin panel
2. **Configure integration** in admin panel:
   ```json
   {
     "username": "your-username",
     "password": "your-password",
     "token": "your-api-token"
   }
   ```
3. **Start synchronization** from admin panel
4. **Monitor sync jobs** in admin dashboard

## Security

### Authentication
- JWT tokens with configurable expiration
- Refresh token rotation
- Session tracking and invalidation
- Password hashing with bcrypt

### Authorization
- Role-based access control (RBAC)
- Dynamic permission system
- Configurable user roles
- API endpoint protection

### Data Security
- SQL injection protection
- Input validation and sanitization
- Encrypted credential storage
- CORS configuration
- Rate limiting

## Monitoring & Observability

### Metrics Collection
- Prometheus metrics for all endpoints
- Custom business metrics
- System resource monitoring
- Database performance metrics

### Logging
- Structured JSON logging
- Request/response tracing
- Error tracking and alerting
- Performance monitoring

### Health Checks
- Application health endpoint
- Service dependency checks
- Database connectivity
- Redis availability

## Development

### Code Quality
```bash
make lint      # Run linting
make format    # Format code
make test      # Run tests
```

### Database Management
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
make migrate   # Run migrations
```

### Testing
```bash
pytest tests/ -v --cov=app
pytest tests/test_auth.py -v
```

## Performance

### Optimization Features
- Async/await throughout the codebase
- Database connection pooling
- Redis caching for frequent queries
- Efficient database queries with proper indexing
- Background task processing
- Response compression

### Scalability
- Horizontal scaling support
- Microservice-ready architecture
- Load balancer compatible
- Stateless application design
- Configurable worker processes

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres
```

**Redis Connection Error**
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis
```

**Celery Tasks Not Processing**
```bash
# Check Celery worker status
docker-compose logs celery_worker

# Monitor tasks in Flower
# Visit http://localhost:5555
```

**MoySklad Sync Issues**
```bash
# Check sync job logs
docker-compose logs api | grep sync

# Test MoySklad connection
curl -X POST http://localhost:8000/api/v1/admin/integrations/test
```
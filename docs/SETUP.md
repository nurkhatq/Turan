# Business CRM Backend Setup

This is a FastAPI-based Business CRM system with MoySklad integration.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here

# MoySklad Integration (optional)
MOYSKLAD_TOKEN=your-moysklad-token-here
```

### 3. Set up Database

Make sure PostgreSQL is running and create the database:

```sql
CREATE DATABASE crm_db;
CREATE USER crm_user WITH PASSWORD 'crm_password';
GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Application

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Available Endpoints

- **Root**: `GET /` - Welcome message
- **Health Check**: `GET /health` - Application health status
- **API Documentation**: `GET /docs` - Interactive API documentation
- **API Routes**: `GET /api/v1/*` - All API endpoints

## Features

- ✅ FastAPI with Pydantic v2
- ✅ PostgreSQL with SQLAlchemy 2.0
- ✅ Redis for caching and sessions
- ✅ Celery for background tasks
- ✅ JWT authentication
- ✅ MoySklad integration
- ✅ Database migrations with Alembic
- ✅ CORS support
- ✅ Health checks

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Configuration

All configuration is handled through environment variables. See `app/core/config.py` for all available options.

## Troubleshooting

1. **Database Connection Issues**: Ensure PostgreSQL is running and the connection string is correct
2. **Redis Connection Issues**: Ensure Redis is running on the specified port
3. **Import Errors**: Make sure all dependencies are installed and the Python path is correct
4. **Pydantic Errors**: Ensure you're using Pydantic v2 compatible code


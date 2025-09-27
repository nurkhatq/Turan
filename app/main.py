# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging

from app.core.config import Settings
from app.core.database import init_db, close_db
from app.core.redis import redis_manager
from app.core.monitoring import setup_prometheus_metrics
from app.core.logging import setup_logging
from app.core.exceptions import create_http_exception

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Initialize Redis
        await redis_manager.connect()
        logger.info("Redis connected")
        
        logger.info("Application startup completed")
        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    finally:
        # Shutdown
        await close_db()
        await redis_manager.disconnect()
        logger.info("Application shutdown completed")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Comprehensive Business CRM System with MoySklad Integration",
    lifespan=lifespan
)

# Setup Prometheus metrics (must be done after app creation)
setup_prometheus_metrics(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return create_http_exception(exc.status_code, str(exc.detail))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return create_http_exception(422, "Validation error", {"errors": exc.errors()})

# Basic routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION
    }

# Try to include API router if available
try:
    from app.api.v1 import api_router
    app.include_router(api_router, prefix="/api/v1")
except ImportError as e:
    logging.warning(f"Could not load API router: {e}")
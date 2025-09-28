# app/main.py (FIXED VERSION WITH BETTER ERROR HANDLING)
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging
import traceback
import json

from app.core.config import Settings
from app.core.database import init_db, close_db
from app.core.redis import redis_manager
from app.core.monitoring import setup_prometheus_metrics
from app.core.logging import setup_logging

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting application initialization...")
        
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("✅ Database initialized")
        
        # Initialize Redis
        logger.info("Connecting to Redis...")
        await redis_manager.connect()
        logger.info("✅ Redis connected")
        
        logger.info("🚀 Application startup completed successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        try:
            await close_db()
            await redis_manager.disconnect()
            logger.info("✅ Application shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Comprehensive Business CRM System with MoySklad Integration",
    lifespan=lifespan,
    debug=settings.DEBUG
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

# Exception handlers with better error details
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with detailed error info."""
    logger = logging.getLogger(__name__)
    logger.warning(f"HTTP {exc.status_code} error on {request.method} {request.url}: {exc.detail}")
    
    return Response(
        content=json.dumps({
            "error": True,
            "status_code": exc.status_code,
            "message": str(exc.detail),
            "path": str(request.url.path)
        }),
        status_code=exc.status_code,
        media_type="application/json"
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed field info."""
    logger = logging.getLogger(__name__)
    logger.warning(f"Validation error on {request.method} {request.url}: {exc.errors()}")
    
    return Response(
        content=json.dumps({
            "error": True,
            "status_code": 422,
            "message": "Validation error",
            "details": exc.errors(),
            "path": str(request.url.path)
        }),
        status_code=422,
        media_type="application/json"
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with full error details in debug mode."""
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}")
    logger.error(traceback.format_exc())
    
    error_detail = {
        "error": True,
        "status_code": 500,
        "message": "Internal server error",
        "path": str(request.url.path)
    }
    
    # Add detailed error info in debug mode
    if settings.DEBUG:
        error_detail.update({
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc().split('\n')
        })
    
    return Response(
        content=json.dumps(error_detail),
        status_code=500,
        media_type="application/json"
    )

# Basic routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "status": "running",
        "debug_mode": settings.DEBUG
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with component status."""
    logger = logging.getLogger(__name__)
    
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2024-01-01T00:00:00Z",  # Will be replaced with actual timestamp
        "components": {}
    }
    
    # Test database
    try:
        from app.core.database import engine
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Test Redis
    try:
        await redis_manager.redis.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["components"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    return health_status

# Try to include API router with better error handling
try:
    from app.api.v1 import api_router
    app.include_router(api_router, prefix="/api/v1")
    logging.getLogger(__name__).info("✅ API router loaded successfully")
except ImportError as e:
    logging.getLogger(__name__).error(f"❌ Could not load API router: {e}")
    logging.getLogger(__name__).error(traceback.format_exc())
except Exception as e:
    logging.getLogger(__name__).error(f"❌ Unexpected error loading API router: {e}")
    logging.getLogger(__name__).error(traceback.format_exc())
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import Settings
from app.core.database import init_db, close_db
from app.core.redis import redis_manager

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logging.basicConfig(level=logging.INFO)
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
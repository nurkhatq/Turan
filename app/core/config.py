# app/core/config.py
from typing import Optional, List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application
    APP_NAME: str = "Business CRM System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/crm_db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - Fixed for Pydantic v2
    ALLOWED_HOSTS: Union[str, List[str]] = ["*"]
    CORS_ORIGINS: Union[str, List[str]] = ["*"]
    
    # MoySklad Integration
    MOYSKLAD_BASE_URL: str = "https://api.moysklad.ru/api/remap/1.2"
    MOYSKLAD_USERNAME: Optional[str] = None
    MOYSKLAD_PASSWORD: Optional[str] = None
    MOYSKLAD_TOKEN: Optional[str] = None
    MOYSKLAD_SYNC_INTERVAL_MINUTES: int = 15
    MOYSKLAD_WEBHOOK_SECRET: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    PROMETHEUS_METRICS_PATH: str = "/metrics"
    HEALTH_CHECK_PATH: str = "/health"
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    @field_validator('ALLOWED_HOSTS', 'CORS_ORIGINS', mode='before')
    @classmethod
    def parse_list_fields(cls, v):
        """Parse comma-separated strings or JSON arrays into lists."""
        if v is None or v == "":
            return ["*"]
        
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            # Try to parse as JSON first
            try:
                import json
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                # If not JSON, split by comma
                return [item.strip() for item in v.split(',') if item.strip()]
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra environment variables
    }
# app/api/middleware.py
import time
import logging
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_context
from app.core.redis import redis_manager
from app.core.config import Settings
from app.models.system import ApiLog

settings = Settings()
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging API requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Extract request info
        method = request.method
        url = str(request.url)
        user_agent = request.headers.get("user-agent")
        ip_address = self._get_client_ip(request)
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            error_message = None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            status_code = 500
            error_message = str(e)
            response = JSONResponse(
                status_code=500,
                content={"message": "Internal server error"}
            )
        
        # Calculate response time
        process_time = int((time.time() - start_time) * 1000)
        
        # Log to database (async)
        try:
            async with get_db_context() as db:
                api_log = ApiLog(
                    method=method,
                    endpoint=url,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status_code=status_code,
                    response_time_ms=process_time,
                    error_message=error_message
                )
                db.add(api_log)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")
        
        # Add response time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if await self._is_rate_limited(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "message": "Rate limit exceeded",
                    "limit": settings.RATE_LIMIT_PER_MINUTE
                }
            )
        
        return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from token (simplified)
        auth_header = request.headers.get("authorization")
        if auth_header:
            return f"user:{auth_header[:20]}"  # Use part of token as ID
        
        # Fall back to IP address
        return f"ip:{request.client.host}" if request.client else "unknown"
    
    async def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        try:
            key = f"rate_limit:{client_id}"
            current = await redis_manager.incr(key)
            
            if current == 1:
                # Set expiration for new key
                await redis_manager.expire(key, 60)  # 1 minute
            
            return current > settings.RATE_LIMIT_PER_MINUTE
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return False  # Allow request if Redis fails

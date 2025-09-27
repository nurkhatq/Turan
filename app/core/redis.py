# app/core/redis.py
import aioredis
import json
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import logging

from .config import Settings

settings = Settings()
logger = logging.getLogger(__name__)


class RedisManager:
    """Redis connection and utility manager."""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False
            )
            # Test connection
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: str = "json"
    ) -> bool:
        """Set value in Redis with optional TTL."""
        try:
            if serialize == "json":
                serialized_value = json.dumps(value, default=str)
            elif serialize == "pickle":
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = str(value)
            
            if ttl:
                await self.redis.setex(key, ttl, serialized_value)
            else:
                await self.redis.set(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Failed to set Redis key {key}: {e}")
            return False
    
    async def get(
        self, 
        key: str, 
        default: Any = None,
        deserialize: str = "json"
    ) -> Any:
        """Get value from Redis."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            
            if deserialize == "json":
                return json.loads(value)
            elif deserialize == "pickle":
                return pickle.loads(value)
            else:
                return value.decode() if isinstance(value, bytes) else value
        except Exception as e:
            logger.error(f"Failed to get Redis key {key}: {e}")
            return default
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis."""
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Failed to delete Redis keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check Redis key existence {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Failed to set expire for Redis key {key}: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment Redis key {key}: {e}")
            return 0
    
    async def cache_with_ttl(
        self, 
        key: str, 
        callback, 
        ttl: Optional[int] = None,
        *args, 
        **kwargs
    ) -> Any:
        """Cache result of callback function."""
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Execute callback and cache result
        result = await callback(*args, **kwargs) if callable(callback) else callback
        await self.set(key, result, ttl or settings.REDIS_CACHE_TTL)
        return result


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> RedisManager:
    """Get Redis manager instance."""
    return redis_manager

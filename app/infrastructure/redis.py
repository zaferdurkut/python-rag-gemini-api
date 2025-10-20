import redis
from typing import Optional, Any
from app.core.config import settings
import json


class RedisService:
    """Redis service for caching and session management."""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        return self.redis_client.get(key)
    
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in Redis."""
        return self.redis_client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        return bool(self.redis_client.delete(key))
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        return bool(self.redis_client.exists(key))
    
    async def set_json(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set JSON value in Redis."""
        json_value = json.dumps(value)
        return await self.set(key, json_value, expire)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from Redis."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in Redis."""
        return self.redis_client.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key."""
        return bool(self.redis_client.expire(key, seconds))


# Global Redis service instance
redis_service = RedisService()

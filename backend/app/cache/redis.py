"""Redis cache client wrapper for async operations"""

import json
import redis.asyncio as aioredis
from typing import Any, Optional
from app.utils.logger import logger
from app.config import settings


class RedisCache:
    """Async Redis cache wrapper with JSON serialization"""

    def __init__(self, redis_url: str = None):
        """Initialize Redis cache client

        Args:
            redis_url: Redis connection URL (default from settings)
        """
        self.redis_url = redis_url or getattr(
            settings, "REDIS_URL", "redis://localhost:6379/0"
        )
        self.client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis server"""
        try:
            self.client = await aioredis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            await self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.warning(
                f"Failed to connect to Redis: {e}. Cache operations will be disabled."
            )
            self.client = None

    async def disconnect(self) -> None:
        """Close Redis connection"""
        try:
            if self.client:
                await self.client.close()
                logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve and deserialize value from cache

        Args:
            key: Cache key

        Returns:
            Deserialized value or None if not found
        """
        try:
            if not self.client:
                return None

            value = await self.client.get(key)
            if value is None:
                return None

            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning(f"Failed to deserialize cached value for key {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Store serialized value in cache with optional TTL

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (None for no expiration)

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                return False

            serialized = json.dumps(value)
            if ttl:
                await self.client.setex(key, ttl, serialized)
            else:
                await self.client.set(key, serialized)

            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove key from cache

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            if not self.client:
                return False

            result = await self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern

        Args:
            pattern: Pattern to match keys (e.g., "user_segment:*")

        Returns:
            Number of keys deleted
        """
        try:
            if not self.client:
                return 0

            # Find all keys matching pattern
            cursor = 0
            count = 0

            while True:
                cursor, keys = await self.client.scan(cursor, match=pattern)
                if keys:
                    count += await self.client.delete(*keys)
                if cursor == 0:
                    break

            return count
        except Exception as e:
            logger.warning(f"Cache clear_pattern failed for pattern {pattern}: {e}")
            return 0


# Global cache instance
cache = RedisCache()

"""Redis client module."""

from typing import Optional

import redis.asyncio as redis
from earnbase_common.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis client wrapper."""

    def __init__(self) -> None:
        """Initialize Redis client."""
        self._client: Optional[redis.Redis] = None
        self._prefix: str = ""
        self._ttl: int = 3600

    @classmethod
    async def connect(
        cls,
        url: str,
        db: int = 0,
        prefix: str = "",
        ttl: int = 3600,
    ) -> "RedisClient":
        """Connect to Redis."""
        logger.info("connecting_to_redis", url=url, db=db)

        instance = cls()
        try:
            instance._client = redis.from_url(url, db=db, decode_responses=True)
            instance._prefix = prefix
            instance._ttl = ttl

            # Test connection
            await instance._client.ping()
            logger.info("redis_connected")

            return instance

        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("redis_disconnected")

    def _get_key(self, key: str) -> str:
        """Get prefixed key."""
        return f"{self._prefix}:{key}" if self._prefix else key

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")

        try:
            value = await self._client.get(self._get_key(key))
            return value

        except Exception as e:
            logger.error("redis_get_failed", key=key, error=str(e))
            raise

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None,
    ) -> None:
        """Set value in Redis."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")

        try:
            await self._client.set(
                self._get_key(key),
                value,
                ex=expire or self._ttl,
            )

        except Exception as e:
            logger.error("redis_set_failed", key=key, error=str(e))
            raise

    async def delete(self, key: str) -> None:
        """Delete key from Redis."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")

        try:
            await self._client.delete(self._get_key(key))

        except Exception as e:
            logger.error("redis_delete_failed", key=key, error=str(e))
            raise

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")

        try:
            return bool(await self._client.exists(self._get_key(key)))

        except Exception as e:
            logger.error("redis_exists_failed", key=key, error=str(e))
            raise

    async def expire(self, key: str, seconds: int) -> None:
        """Set key expiration."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")

        try:
            await self._client.expire(self._get_key(key), seconds)

        except Exception as e:
            logger.error("redis_expire_failed", key=key, error=str(e))
            raise

    async def ttl(self, key: str) -> int:
        """Get key TTL."""
        if not self._client:
            raise RuntimeError("Redis client not initialized")

        try:
            return await self._client.ttl(self._get_key(key))

        except Exception as e:
            logger.error("redis_ttl_failed", key=key, error=str(e))
            raise

"""Redis client module."""

import json
from typing import Any, Optional
import aioredis

from earnbase_common.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis client."""

    def __init__(self):
        """Initialize client."""
        self._client: Optional[aioredis.Redis] = None

    async def connect(
        self,
        url: str,
        db: int = 0,
        prefix: str = "",
        ttl: int = 3600,
    ) -> None:
        """Connect to Redis."""
        try:
            self._client = await aioredis.from_url(
                url,
                db=db,
                encoding="utf-8",
                decode_responses=True,
            )
            self._prefix = prefix
            self._ttl = ttl

            # Test connection
            await self._client.ping()

            logger.info(
                "redis_connected",
                url=url,
                database=db,
                prefix=prefix,
            )
        except Exception as e:
            logger.error(
                "redis_connection_failed",
                error=str(e),
                url=url,
                database=db,
            )
            raise

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            logger.info("redis_disconnected")

    def _get_key(self, key: str) -> str:
        """Get prefixed key."""
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        if not self._client:
            raise RuntimeError("Redis connection not initialized")

        try:
            value = await self._client.get(self._get_key(key))
            return json.loads(value) if value else None
        except Exception as e:
            logger.error("redis_get_failed", error=str(e), key=key)
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in Redis."""
        if not self._client:
            raise RuntimeError("Redis connection not initialized")

        try:
            await self._client.set(
                self._get_key(key),
                json.dumps(value),
                ex=ttl or self._ttl,
            )
            return True
        except Exception as e:
            logger.error("redis_set_failed", error=str(e), key=key)
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        if not self._client:
            raise RuntimeError("Redis connection not initialized")

        try:
            await self._client.delete(self._get_key(key))
            return True
        except Exception as e:
            logger.error("redis_delete_failed", error=str(e), key=key)
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self._client:
            raise RuntimeError("Redis connection not initialized")

        try:
            return bool(await self._client.exists(self._get_key(key)))
        except Exception as e:
            logger.error("redis_exists_failed", error=str(e), key=key)
            return False


# Global Redis instance
redis_client = RedisClient()

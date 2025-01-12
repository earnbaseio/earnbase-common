"""Base container module."""

from dependency_injector import containers, providers
from earnbase_common.config import BaseSettings
from earnbase_common.database.mongodb import MongoDB
from earnbase_common.logging import get_logger
from earnbase_common.metrics.metrics import MetricsManager
from earnbase_common.redis.client import RedisClient

logger = get_logger(__name__)


class BaseContainer(containers.DeclarativeContainer):
    """Base container with common providers."""

    # Configuration
    config = providers.Singleton(BaseSettings)

    # Common providers
    mongodb = providers.Singleton(
        MongoDB,
    )

    redis = providers.Singleton(RedisClient)

    metrics = providers.Singleton(
        MetricsManager,
        enabled=config.provided.METRICS_ENABLED,
    )

    async def init_resources(self) -> None:
        """Initialize container resources."""
        logger.info("initializing_resources")

        # Initialize MongoDB
        mongodb = self.mongodb()
        if not mongodb:
            raise RuntimeError("Failed to initialize MongoDB client")

        config = self.config()
        mongodb_url = getattr(config, "MONGODB_URL", "mongodb://localhost:27017")
        mongodb_db = getattr(config, "MONGODB_DB_NAME", "earnbase")

        await mongodb.connect(
            url=mongodb_url,
            db_name=mongodb_db,
            min_pool_size=getattr(config, "MONGODB_MIN_POOL_SIZE", 10),
            max_pool_size=getattr(config, "MONGODB_MAX_POOL_SIZE", 100),
        )

        # Initialize Redis if configured
        redis_url = getattr(config, "REDIS_URL", None)
        if redis_url:
            redis = self.redis()
            if not redis:
                raise RuntimeError("Failed to initialize Redis client")

            await redis.connect(
                url=redis_url,
                db=getattr(config, "REDIS_DB", 0),
                prefix=getattr(config, "REDIS_PREFIX", ""),
                ttl=getattr(config, "REDIS_TTL", 3600),
            )

        logger.info("resources_initialized")

    async def shutdown_resources(self) -> None:
        """Shutdown container resources."""
        logger.info("shutting_down_resources")

        # Shutdown MongoDB
        mongodb = self.mongodb()
        if mongodb and mongodb.client:
            await mongodb.close()

        # Shutdown Redis if configured
        config = self.config()
        redis_url = getattr(config, "REDIS_URL", None)
        if redis_url:
            redis = self.redis()
            if redis and redis._client:
                await redis._client.close()

        logger.info("resources_shutdown")

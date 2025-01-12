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
    mongodb = providers.Resource(
        MongoDB.connect,
        url=config.provided.MONGODB_URL,
        db_name=config.provided.MONGODB_DB_NAME,
        min_pool_size=config.provided.MONGODB_MIN_POOL_SIZE,
        max_pool_size=config.provided.MONGODB_MAX_POOL_SIZE,
    )

    redis = providers.Resource(
        RedisClient.connect,
        url=config.provided.REDIS_URL,
        db=config.provided.REDIS_DB,
        prefix=config.provided.REDIS_PREFIX,
        ttl=config.provided.REDIS_TTL,
    )

    metrics = providers.Singleton(
        MetricsManager,
        enabled=config.provided.METRICS_ENABLED,
    )

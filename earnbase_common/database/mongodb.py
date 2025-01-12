"""MongoDB database module."""

from typing import Any, Dict, List, Optional

from earnbase_common.logging import get_logger
from earnbase_common.retry import RetryConfig, with_retry
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, PyMongoError, ServerSelectionTimeoutError

logger = get_logger(__name__)

# Default retry config for MongoDB operations
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    max_delay=5.0,
    min_delay=1.0,
    exceptions=(ConnectionFailure, ServerSelectionTimeoutError),
)


class MongoDB:
    """MongoDB database connection manager."""

    def __init__(self):
        """Initialize MongoDB connection manager."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._retry_config = DEFAULT_RETRY_CONFIG

    async def connect(
        self,
        url: str,
        db_name: str,
        min_pool_size: int = 10,
        max_pool_size: int = 100,
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        """Connect to MongoDB."""
        if retry_config:
            self._retry_config = retry_config

        if not self.client:

            async def _connect():
                try:
                    self.client = AsyncIOMotorClient(
                        url,
                        minPoolSize=min_pool_size,
                        maxPoolSize=max_pool_size,
                    )
                    self.db = self.client[db_name]
                    # Verify connection
                    await self.client.admin.command("ping")
                    logger.info(
                        "mongodb_connected",
                        url=url,
                        database=db_name,
                        min_pool_size=min_pool_size,
                        max_pool_size=max_pool_size,
                    )
                except PyMongoError as e:
                    self.client = None
                    self.db = None
                    logger.error(
                        "mongodb_connection_failed",
                        error=str(e),
                        url=url,
                        database=db_name,
                    )
                    raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

            await with_retry("mongodb_connect", self._retry_config, _connect())

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("mongodb_disconnected")

    async def ping(self) -> bool:
        """Check MongoDB connection."""
        if not self.client:
            return False
        try:
            await with_retry(
                "mongodb_ping", self._retry_config, self.client.admin.command("ping")
            )
            return True
        except PyMongoError:
            return False

    async def find_one(
        self, collection: str, query: Dict[str, Any], projection: Dict[str, Any] = {}
    ) -> Optional[Dict[str, Any]]:
        """Find one document in collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")

        return await with_retry(
            "mongodb_find_one",
            self._retry_config,
            self.db[collection].find_one(query, projection),
        )

    async def find_many(
        self,
        collection: str,
        query: Dict[str, Any],
        projection: Dict[str, Any] = {},
        sort: List[tuple] = [],
        skip: int = 0,
        limit: int = 0,
    ) -> List[Dict[str, Any]]:
        """Find multiple documents in collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")

        async def _find_many():
            if self.db is None:
                raise ConnectionError("MongoDB connection not initialized")
            cursor = self.db[collection].find(query, projection)
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return await cursor.to_list(length=None)

        return await with_retry("mongodb_find_many", self._retry_config, _find_many())

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert one document into collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        result = await with_retry(
            "mongodb_insert_one",
            self._retry_config,
            self.db[collection].insert_one(document),
        )
        return str(result.inserted_id)

    async def insert_many(
        self, collection: str, documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Insert multiple documents into collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        result = await with_retry(
            "mongodb_insert_many",
            self._retry_config,
            self.db[collection].insert_many(documents),
        )
        return [str(id) for id in result.inserted_ids]

    async def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> int:
        """Update one document in collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        result = await with_retry(
            "mongodb_update_one",
            self._retry_config,
            self.db[collection].update_one(query, update, upsert=upsert),
        )
        return result.modified_count

    async def update_many(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> int:
        """Update multiple documents in collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        result = await with_retry(
            "mongodb_update_many",
            self._retry_config,
            self.db[collection].update_many(query, update, upsert=upsert),
        )
        return result.modified_count

    async def delete_one(self, collection: str, query: Dict[str, Any]) -> int:
        """Delete one document from collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        result = await with_retry(
            "mongodb_delete_one",
            self._retry_config,
            self.db[collection].delete_one(query),
        )
        return result.deleted_count

    async def delete_many(self, collection: str, query: Dict[str, Any]) -> int:
        """Delete multiple documents from collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        result = await with_retry(
            "mongodb_delete_many",
            self._retry_config,
            self.db[collection].delete_many(query),
        )
        return result.deleted_count

    async def count_documents(self, collection: str, query: Dict[str, Any]) -> int:
        """Count documents in collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        return await with_retry(
            "mongodb_count_documents",
            self._retry_config,
            self.db[collection].count_documents(query),
        )

    async def create_index(
        self,
        collection: str,
        keys: List[tuple],
        unique: bool = False,
        sparse: bool = False,
        background: bool = True,
    ) -> str:
        """Create index on collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        return await with_retry(
            "mongodb_create_index",
            self._retry_config,
            self.db[collection].create_index(
                keys, unique=unique, sparse=sparse, background=background
            ),
        )

    async def drop_index(self, collection: str, index_name: str) -> None:
        """Drop index from collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        await with_retry(
            "mongodb_drop_index",
            self._retry_config,
            self.db[collection].drop_index(index_name),
        )

    async def list_indexes(self, collection: str) -> List[Dict[str, Any]]:
        """List indexes for collection."""
        if self.db is None:
            raise ConnectionError("MongoDB connection not initialized")
        return await with_retry(
            "mongodb_list_indexes",
            self._retry_config,
            self.db[collection].list_indexes().to_list(None),
        )


# Global MongoDB instance
mongodb = MongoDB()

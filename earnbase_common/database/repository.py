"""Base repository module."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from earnbase_common.logging import get_logger
from earnbase_common.metrics import metrics
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Base repository for MongoDB collections."""

    def __init__(self, collection: AsyncIOMotorCollection, model: type[T]):
        """Initialize repository."""
        self.collection = collection
        self.model = model

    async def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """Find one document."""
        with metrics.db_operation_latency.labels(
            operation="find_one", collection=self.collection.name
        ).time():
            result = await self.collection.find_one(filter)
            metrics.db_operation_count.labels(
                operation="find_one", collection=self.collection.name
            ).inc()
            return self.model(**result) if result else None

    async def find_many(
        self,
        filter: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple[str, int]]] = None,
    ) -> List[T]:
        """Find many documents."""
        with metrics.db_operation_latency.labels(
            operation="find_many", collection=self.collection.name
        ).time():
            cursor = self.collection.find(filter).skip(skip).limit(limit)
            if sort:
                cursor = cursor.sort(sort)
            results = await cursor.to_list(length=limit)
            metrics.db_operation_count.labels(
                operation="find_many", collection=self.collection.name
            ).inc()
            return [self.model(**result) for result in results]

    async def count(self, filter: Dict[str, Any]) -> int:
        """Count documents."""
        with metrics.db_operation_latency.labels(
            operation="count", collection=self.collection.name
        ).time():
            count = await self.collection.count_documents(filter)
            metrics.db_operation_count.labels(
                operation="count", collection=self.collection.name
            ).inc()
            return count

    async def create(self, data: Dict[str, Any]) -> T:
        """Create document."""
        with metrics.db_operation_latency.labels(
            operation="create", collection=self.collection.name
        ).time():
            data["created_at"] = datetime.utcnow()
            data["updated_at"] = data["created_at"]
            result = await self.collection.insert_one(data)
            metrics.db_operation_count.labels(
                operation="create", collection=self.collection.name
            ).inc()
            doc = await self.find_one({"_id": result.inserted_id})
            assert doc is not None, "Created document not found"
            return doc

    async def update(self, filter: Dict[str, Any], data: Dict[str, Any]) -> Optional[T]:
        """Update document."""
        with metrics.db_operation_latency.labels(
            operation="update", collection=self.collection.name
        ).time():
            data["updated_at"] = datetime.utcnow()
            result = await self.collection.find_one_and_update(
                filter,
                {"$set": data},
                return_document=True,
            )
            metrics.db_operation_count.labels(
                operation="update", collection=self.collection.name
            ).inc()
            return self.model(**result) if result else None

    async def delete(self, filter: Dict[str, Any]) -> bool:
        """Delete document."""
        with metrics.db_operation_latency.labels(
            operation="delete", collection=self.collection.name
        ).time():
            result = await self.collection.delete_one(filter)
            metrics.db_operation_count.labels(
                operation="delete", collection=self.collection.name
            ).inc()
            return result.deleted_count > 0

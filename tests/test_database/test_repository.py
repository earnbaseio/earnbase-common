"""Tests for base repository."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from earnbase_common.database.repository import BaseRepository
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel


@pytest.fixture
def test_model():
    """Create test model class."""

    class TestModel(BaseModel):
        """Test model."""

        id: str
        name: str
        created_at: datetime
        updated_at: datetime

    return TestModel


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.asyncio
class TestBaseRepository:
    """Test base repository."""

    @pytest.fixture
    def collection(self):
        """Create mock collection."""
        mock = AsyncMock(spec=AsyncIOMotorCollection)
        mock.name = "test_collection"
        return mock

    @pytest.fixture
    def repository(self, collection, test_model):
        """Create repository instance."""
        return BaseRepository(collection, test_model)

    @pytest.fixture
    def mock_metrics(self):
        """Create mock metrics."""
        mock = MagicMock()
        mock.db_operation_latency.labels.return_value.time.return_value.__enter__ = (
            MagicMock()
        )
        mock.db_operation_latency.labels.return_value.time.return_value.__exit__ = (
            MagicMock()
        )
        mock.db_operation_count.labels.return_value.inc = MagicMock()
        return mock

    async def test_find_one_success(self, repository, collection, test_model):
        """Test successful find_one operation."""
        now = datetime.utcnow()
        document = {
            "id": "123",
            "name": "test",
            "created_at": now,
            "updated_at": now,
        }
        collection.find_one = AsyncMock(return_value=document)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            result = await repository.find_one({"id": "123"})

            assert isinstance(result, test_model)
            assert result.id == "123"
            assert result.name == "test"
            assert result.created_at == now
            assert result.updated_at == now

            collection.find_one.assert_called_once_with({"id": "123"})
            mock_metrics.db_operation_latency.labels.assert_called_once_with(
                operation="find_one",
                collection="test_collection",
            )
            mock_metrics.db_operation_count.labels.assert_called_once_with(
                operation="find_one",
                collection="test_collection",
            )

    async def test_find_one_not_found(self, repository, collection):
        """Test find_one when document not found."""
        collection.find_one = AsyncMock(return_value=None)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            result = await repository.find_one({"id": "123"})

            assert result is None
            collection.find_one.assert_called_once_with({"id": "123"})
            mock_metrics.db_operation_latency.labels.assert_called_once()

    async def test_find_many(self, repository, collection, test_model):
        """Test find_many operation."""
        now = datetime.utcnow()
        documents = [
            {
                "id": "1",
                "name": "test1",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "2",
                "name": "test2",
                "created_at": now,
                "updated_at": now,
            },
        ]

        # Setup cursor mock
        cursor_mock = AsyncMock()
        cursor_mock.to_list = AsyncMock(return_value=documents)
        cursor_mock.skip = MagicMock(return_value=cursor_mock)
        cursor_mock.limit = MagicMock(return_value=cursor_mock)
        cursor_mock.sort = MagicMock(return_value=cursor_mock)

        # Setup collection mock
        collection.find = MagicMock(return_value=cursor_mock)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            results = await repository.find_many(
                filter={"status": "active"},
                skip=10,
                limit=20,
                sort=[("created_at", -1)],
            )

            assert len(results) == 2
            assert all(isinstance(result, test_model) for result in results)
            assert results[0].id == "1"
            assert results[1].id == "2"

            collection.find.assert_called_once_with({"status": "active"})
            cursor_mock.skip.assert_called_once_with(10)
            cursor_mock.limit.assert_called_once_with(20)
            cursor_mock.sort.assert_called_once_with([("created_at", -1)])
            mock_metrics.db_operation_latency.labels.assert_called_once()
            mock_metrics.db_operation_count.labels.assert_called_once()

    async def test_count(self, repository, collection):
        """Test count operation."""
        collection.count_documents = AsyncMock(return_value=42)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            count = await repository.count({"status": "active"})

            assert count == 42
            collection.count_documents.assert_called_once_with({"status": "active"})
            mock_metrics.db_operation_latency.labels.assert_called_once()

    async def test_create(self, repository, collection, test_model):
        """Test create operation."""
        now = datetime.utcnow()
        insert_result = AsyncMock()
        insert_result.inserted_id = "123"
        collection.insert_one = AsyncMock(return_value=insert_result)

        document = {
            "id": "123",
            "name": "test",
            "created_at": now,
            "updated_at": now,
        }
        collection.find_one = AsyncMock(return_value=document)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            with patch("earnbase_common.database.repository.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value = now
                result = await repository.create({"id": "123", "name": "test"})

                assert isinstance(result, test_model)
                assert result.id == "123"
                assert result.name == "test"
                assert result.created_at == now
                assert result.updated_at == now

                collection.insert_one.assert_called_once()
                collection.find_one.assert_called_once()

                # Verify metrics calls
                assert mock_metrics.db_operation_latency.labels.call_args_list == [
                    call(operation="create", collection="test_collection"),
                    call(operation="find_one", collection="test_collection"),
                ]

                assert mock_metrics.db_operation_count.labels.call_args_list == [
                    call(operation="create", collection="test_collection"),
                    call(operation="find_one", collection="test_collection"),
                ]

    async def test_update(self, repository, collection, test_model):
        """Test update operation."""
        now = datetime.utcnow()
        document = {
            "id": "123",
            "name": "updated",
            "created_at": now,
            "updated_at": now,
        }
        collection.find_one_and_update = AsyncMock(return_value=document)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            with patch("earnbase_common.database.repository.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value = now
                result = await repository.update(
                    {"id": "123"},
                    {"name": "updated"},
                )

                assert isinstance(result, test_model)
                assert result.id == "123"
                assert result.name == "updated"
                assert result.created_at == now
                assert result.updated_at == now

                collection.find_one_and_update.assert_called_once()
                mock_metrics.db_operation_latency.labels.assert_called_once()
                mock_metrics.db_operation_count.labels.assert_called_once()

    async def test_update_not_found(self, repository, collection):
        """Test update when document not found."""
        collection.find_one_and_update = AsyncMock(return_value=None)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            result = await repository.update({"id": "123"}, {"name": "updated"})

            assert result is None
            collection.find_one_and_update.assert_called_once()
            mock_metrics.db_operation_latency.labels.assert_called_once()

    async def test_delete(self, repository, collection):
        """Test delete operation."""
        delete_result = AsyncMock()
        delete_result.deleted_count = 1
        collection.delete_one = AsyncMock(return_value=delete_result)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            result = await repository.delete({"id": "123"})

            assert result is True
            collection.delete_one.assert_called_once_with({"id": "123"})
            mock_metrics.db_operation_latency.labels.assert_called_once()
            mock_metrics.db_operation_count.labels.assert_called_once()

    async def test_delete_not_found(self, repository, collection):
        """Test delete when document not found."""
        delete_result = AsyncMock()
        delete_result.deleted_count = 0
        collection.delete_one = AsyncMock(return_value=delete_result)

        with patch("earnbase_common.database.repository.metrics") as mock_metrics:
            result = await repository.delete({"id": "123"})

            assert result is False
            collection.delete_one.assert_called_once_with({"id": "123"})
            mock_metrics.db_operation_latency.labels.assert_called_once()
            mock_metrics.db_operation_count.labels.assert_called_once()

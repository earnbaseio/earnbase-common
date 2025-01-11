"""Tests for MongoDB client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from earnbase_common.database.mongodb import MongoDB
from pymongo.errors import PyMongoError


@pytest.mark.unit
@pytest.mark.database
class TestMongoDB:
    """Test MongoDB client."""

    @pytest.fixture
    def mongodb(self):
        """Create MongoDB instance."""
        return MongoDB()

    @pytest.fixture
    def mock_motor_client(self):
        """Create mock motor client."""
        mock = AsyncMock()
        mock.admin.command = AsyncMock(return_value=True)  # Mock ping response
        mock.__getitem__ = MagicMock()
        return mock

    @pytest.mark.asyncio
    async def test_connect_success(self, mongodb, mock_motor_client):
        """Test successful connection."""
        # Ensure admin.command is properly mocked for ping
        mock_motor_client.admin.command = AsyncMock(return_value=True)
        mock_motor_client.__getitem__ = MagicMock()

        with patch(
            "motor.motor_asyncio.AsyncIOMotorClient", return_value=mock_motor_client
        ):
            await mongodb.connect(
                url="mongodb://localhost:27017",
                db_name="test_db",
                min_pool_size=5,
                max_pool_size=50,
            )
            assert mongodb.client == mock_motor_client
            assert mongodb.db == mock_motor_client.__getitem__.return_value
            mock_motor_client.admin.command.assert_called_once_with("ping")

    @pytest.mark.asyncio
    async def test_connect_failure(self, mongodb):
        """Test connection failure."""
        mock_client = AsyncMock()
        mock_client.admin.command = AsyncMock(
            side_effect=PyMongoError("Connection failed")
        )
        mock_client.__getitem__ = MagicMock()

        with patch("motor.motor_asyncio.AsyncIOMotorClient", return_value=mock_client):
            with pytest.raises(ConnectionError) as exc_info:
                await mongodb.connect(
                    url="mongodb://localhost:27017",
                    db_name="test_db",
                )
            assert "Failed to connect to MongoDB" in str(exc_info.value)
            assert mongodb.client is None
            assert mongodb.db is None

    @pytest.mark.asyncio
    async def test_close(self, mongodb, mock_motor_client):
        """Test connection close."""
        mongodb.client = mock_motor_client
        await mongodb.close()
        mock_motor_client.close.assert_called_once()
        assert mongodb.client is None
        assert mongodb.db is None

    @pytest.mark.asyncio
    async def test_ping_success(self, mongodb, mock_motor_client):
        """Test successful ping."""
        mongodb.client = mock_motor_client
        result = await mongodb.ping()
        assert result is True
        mock_motor_client.admin.command.assert_called_once_with("ping")

    @pytest.mark.asyncio
    async def test_ping_failure(self, mongodb, mock_motor_client):
        """Test ping failure."""
        mongodb.client = mock_motor_client
        mock_motor_client.admin.command.side_effect = PyMongoError()
        result = await mongodb.ping()
        assert result is False

    @pytest.mark.asyncio
    async def test_ping_no_client(self, mongodb):
        """Test ping with no client."""
        result = await mongodb.ping()
        assert result is False

    @pytest.mark.asyncio
    async def test_find_one(self, mongodb, mock_motor_client):
        """Test find_one operation."""
        mongodb.client = mock_motor_client
        mongodb.db = mock_motor_client.__getitem__.return_value
        collection_mock = AsyncMock()
        mongodb.db.__getitem__.return_value = collection_mock
        collection_mock.find_one.return_value = {"_id": "123", "name": "test"}

        result = await mongodb.find_one("test_collection", {"name": "test"})
        assert result == {"_id": "123", "name": "test"}
        collection_mock.find_one.assert_called_once_with({"name": "test"}, None)

    @pytest.mark.asyncio
    async def test_find_many(self, mongodb, mock_motor_client):
        """Test find_many operation."""
        mongodb.client = mock_motor_client
        mongodb.db = mock_motor_client.__getitem__.return_value
        collection_mock = AsyncMock()
        mongodb.db.__getitem__.return_value = collection_mock

        # Create a mock cursor with async methods
        cursor_mock = AsyncMock()
        cursor_mock.to_list = AsyncMock(return_value=[{"_id": "1"}, {"_id": "2"}])

        # Setup the chain of cursor operations
        collection_mock.find = MagicMock(return_value=cursor_mock)
        cursor_mock.sort = MagicMock(return_value=cursor_mock)
        cursor_mock.skip = MagicMock(return_value=cursor_mock)
        cursor_mock.limit = MagicMock(return_value=cursor_mock)

        result = await mongodb.find_many(
            "test_collection",
            {"status": "active"},
            sort=[("created_at", -1)],
            skip=10,
            limit=20,
        )
        assert result == [{"_id": "1"}, {"_id": "2"}]
        collection_mock.find.assert_called_once_with({"status": "active"}, None)
        cursor_mock.sort.assert_called_once_with([("created_at", -1)])
        cursor_mock.skip.assert_called_once_with(10)
        cursor_mock.limit.assert_called_once_with(20)

    @pytest.mark.asyncio
    async def test_insert_one(self, mongodb, mock_motor_client):
        """Test insert_one operation."""
        mongodb.client = mock_motor_client
        mongodb.db = mock_motor_client.__getitem__.return_value
        collection_mock = AsyncMock()
        mongodb.db.__getitem__.return_value = collection_mock
        collection_mock.insert_one.return_value.inserted_id = "123"

        result = await mongodb.insert_one("test_collection", {"name": "test"})
        assert result == "123"
        collection_mock.insert_one.assert_called_once_with({"name": "test"})

    @pytest.mark.asyncio
    async def test_update_one(self, mongodb, mock_motor_client):
        """Test update_one operation."""
        mongodb.client = mock_motor_client
        mongodb.db = mock_motor_client.__getitem__.return_value
        collection_mock = AsyncMock()
        mongodb.db.__getitem__.return_value = collection_mock
        collection_mock.update_one.return_value.modified_count = 1

        result = await mongodb.update_one(
            "test_collection",
            {"_id": "123"},
            {"$set": {"name": "updated"}},
            upsert=True,
        )
        assert result == 1
        collection_mock.update_one.assert_called_once_with(
            {"_id": "123"},
            {"$set": {"name": "updated"}},
            upsert=True,
        )

    @pytest.mark.asyncio
    async def test_delete_one(self, mongodb, mock_motor_client):
        """Test delete_one operation."""
        mongodb.client = mock_motor_client
        mongodb.db = mock_motor_client.__getitem__.return_value
        collection_mock = AsyncMock()
        mongodb.db.__getitem__.return_value = collection_mock
        collection_mock.delete_one.return_value.deleted_count = 1

        result = await mongodb.delete_one("test_collection", {"_id": "123"})
        assert result == 1
        collection_mock.delete_one.assert_called_once_with({"_id": "123"})

    @pytest.mark.asyncio
    async def test_count_documents(self, mongodb, mock_motor_client):
        """Test count_documents operation."""
        mongodb.client = mock_motor_client
        mongodb.db = mock_motor_client.__getitem__.return_value
        collection_mock = AsyncMock()
        mongodb.db.__getitem__.return_value = collection_mock
        collection_mock.count_documents.return_value = 42

        result = await mongodb.count_documents("test_collection", {"status": "active"})
        assert result == 42
        collection_mock.count_documents.assert_called_once_with({"status": "active"})

    @pytest.mark.asyncio
    async def test_create_index(self, mongodb, mock_motor_client):
        """Test create_index operation."""
        mongodb.client = mock_motor_client
        mongodb.db = mock_motor_client.__getitem__.return_value
        collection_mock = AsyncMock()
        mongodb.db.__getitem__.return_value = collection_mock
        collection_mock.create_index.return_value = "index_name"

        result = await mongodb.create_index(
            "test_collection",
            [("email", 1)],
            unique=True,
            sparse=True,
        )
        assert result == "index_name"
        collection_mock.create_index.assert_called_once_with(
            [("email", 1)],
            unique=True,
            sparse=True,
            background=True,
        )

    @pytest.mark.asyncio
    async def test_operations_without_connection(self, mongodb):
        """Test operations without connection."""
        with pytest.raises(ConnectionError):
            await mongodb.find_one("test_collection", {})

        with pytest.raises(ConnectionError):
            await mongodb.find_many("test_collection", {})

        with pytest.raises(ConnectionError):
            await mongodb.insert_one("test_collection", {})

        with pytest.raises(ConnectionError):
            await mongodb.update_one("test_collection", {}, {})

        with pytest.raises(ConnectionError):
            await mongodb.delete_one("test_collection", {})

        with pytest.raises(ConnectionError):
            await mongodb.count_documents("test_collection", {})

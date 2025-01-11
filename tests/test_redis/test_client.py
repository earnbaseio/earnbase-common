"""Tests for Redis client."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aioredis import Redis
from earnbase_common.redis import RedisClient


@pytest.mark.unit
@pytest.mark.redis
class TestRedisClient:
    """Test RedisClient."""

    @pytest.fixture
    def redis_client(self):
        """Create Redis client."""
        return RedisClient()

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis instance."""
        mock = AsyncMock(spec=Redis)
        mock.ping = AsyncMock()
        mock.get = AsyncMock()
        mock.set = AsyncMock()
        mock.delete = AsyncMock()
        mock.exists = AsyncMock()
        mock.close = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_connect(self, redis_client):
        """Test Redis connection."""
        url = "redis://localhost:6379"
        db = 1
        prefix = "test:"

        with patch("aioredis.from_url") as mock_from_url:
            mock_redis = AsyncMock()
            mock_from_url.return_value = mock_redis

            await redis_client.connect(url=url, db=db, prefix=prefix)

            # Check connection params
            mock_from_url.assert_called_once_with(
                url, db=db, encoding="utf-8", decode_responses=True
            )
            mock_redis.ping.assert_called_once()

            # Check client state
            assert redis_client._client == mock_redis
            assert redis_client._prefix == prefix
            assert redis_client._ttl == 3600  # Default TTL

    @pytest.mark.asyncio
    async def test_connect_failure(self, redis_client):
        """Test Redis connection failure."""
        with patch("aioredis.from_url") as mock_from_url:
            mock_from_url.side_effect = Exception("Connection failed")

            with pytest.raises(Exception) as exc:
                await redis_client.connect(url="redis://invalid")
            assert str(exc.value) == "Connection failed"

    @pytest.mark.asyncio
    async def test_close(self, redis_client, mock_redis):
        """Test closing Redis connection."""
        redis_client._client = mock_redis
        await redis_client.close()
        mock_redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_key_prefix(self, redis_client):
        """Test key prefixing."""
        redis_client._prefix = "test:"
        assert redis_client._get_key("key") == "test:key"

        redis_client._prefix = ""
        assert redis_client._get_key("key") == "key"

    @pytest.mark.asyncio
    async def test_get(self, redis_client, mock_redis):
        """Test getting value from Redis."""
        redis_client._client = mock_redis
        redis_client._prefix = "test:"

        # Test successful get
        mock_redis.get.return_value = json.dumps({"key": "value"})
        result = await redis_client.get("test-key")
        assert result == {"key": "value"}
        mock_redis.get.assert_called_with("test:test-key")

        # Test non-existent key
        mock_redis.get.return_value = None
        result = await redis_client.get("nonexistent")
        assert result is None

        # Test Redis error
        mock_redis.get.side_effect = Exception("Redis error")
        result = await redis_client.get("error-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set(self, redis_client, mock_redis):
        """Test setting value in Redis."""
        redis_client._client = mock_redis
        redis_client._prefix = "test:"
        redis_client._ttl = 3600

        # Test successful set
        value = {"key": "value"}
        result = await redis_client.set("test-key", value)
        assert result is True
        mock_redis.set.assert_called_with("test:test-key", json.dumps(value), ex=3600)

        # Test custom TTL
        result = await redis_client.set("test-key", value, ttl=60)
        assert result is True
        mock_redis.set.assert_called_with("test:test-key", json.dumps(value), ex=60)

        # Test Redis error
        mock_redis.set.side_effect = Exception("Redis error")
        result = await redis_client.set("error-key", value)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete(self, redis_client, mock_redis):
        """Test deleting value from Redis."""
        redis_client._client = mock_redis
        redis_client._prefix = "test:"

        # Test successful delete
        mock_redis.delete.return_value = 1
        result = await redis_client.delete("test-key")
        assert result is True
        mock_redis.delete.assert_called_with("test:test-key")

        # Test Redis error
        mock_redis.delete.side_effect = Exception("Redis error")
        result = await redis_client.delete("error-key")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists(self, redis_client, mock_redis):
        """Test checking key existence in Redis."""
        redis_client._client = mock_redis
        redis_client._prefix = "test:"

        # Test existing key
        mock_redis.exists.return_value = 1
        result = await redis_client.exists("test-key")
        assert result is True
        mock_redis.exists.assert_called_with("test:test-key")

        # Test non-existent key
        mock_redis.exists.return_value = 0
        result = await redis_client.exists("nonexistent")
        assert result is False

        # Test Redis error
        mock_redis.exists.side_effect = Exception("Redis error")
        result = await redis_client.exists("error-key")
        assert result is False

    @pytest.mark.asyncio
    async def test_not_initialized(self, redis_client):
        """Test operations without initialization."""
        with pytest.raises(RuntimeError) as exc:
            await redis_client.get("key")
        assert str(exc.value) == "Redis connection not initialized"

        with pytest.raises(RuntimeError) as exc:
            await redis_client.set("key", "value")
        assert str(exc.value) == "Redis connection not initialized"

        with pytest.raises(RuntimeError) as exc:
            await redis_client.delete("key")
        assert str(exc.value) == "Redis connection not initialized"

        with pytest.raises(RuntimeError) as exc:
            await redis_client.exists("key")
        assert str(exc.value) == "Redis connection not initialized"

    @pytest.mark.asyncio
    async def test_complex_values(self, redis_client, mock_redis):
        """Test handling complex data types."""
        redis_client._client = mock_redis
        redis_client._prefix = "test:"

        # Test nested dictionary
        value = {
            "user": {"id": 1, "name": "Test User", "settings": {"theme": "dark"}},
            "permissions": ["read", "write"],
        }
        mock_redis.get.return_value = json.dumps(value)
        result = await redis_client.get("complex-key")
        assert result == value

        # Test list of dictionaries
        value = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        await redis_client.set("list-key", value)
        mock_redis.set.assert_called_with("test:list-key", json.dumps(value), ex=3600)

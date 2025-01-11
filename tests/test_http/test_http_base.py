"""Tests for base HTTP client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from earnbase_common.http.base import BaseHttpClient
from httpx import HTTPError, Timeout


@pytest.mark.unit
@pytest.mark.http
class TestBaseHttpClient:
    """Test base HTTP client."""

    @pytest.fixture
    def base_url(self):
        """Base URL for testing."""
        return "http://test-service:8000"

    @pytest_asyncio.fixture
    async def http_client(self, base_url):
        """Create HTTP client instance."""
        client = BaseHttpClient(base_url)
        yield client
        await client.close()

    def test_initialization(self, base_url):
        """Test client initialization."""
        client = BaseHttpClient(base_url)
        assert client.base_url == base_url
        assert client.client.base_url == base_url
        assert isinstance(client.client.timeout, Timeout)
        assert client.client.timeout.read == 30.0

    @pytest.mark.asyncio
    async def test_get_success(self, http_client):
        """Test successful GET request."""
        expected_data = {"key": "value"}
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value=expected_data)
        mock_response.aclose = AsyncMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            http_client.client,
            "get",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_get:
            result = await http_client._get("/test")
            assert result == expected_data
            mock_get.assert_called_once_with("/test")
            mock_response.raise_for_status.assert_called_once()
            mock_response.json.assert_awaited_once()
            mock_response.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_failure(self, http_client):
        """Test failed GET request."""
        with patch.object(
            http_client.client, "get", side_effect=HTTPError("Connection error")
        ) as mock_get:
            result = await http_client._get("/test")
            assert result is None
            mock_get.assert_called_once_with("/test")

    @pytest.mark.asyncio
    async def test_post_success(self, http_client):
        """Test successful POST request."""
        request_data = {"request": "data"}
        expected_data = {"response": "data"}
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value=expected_data)
        mock_response.aclose = AsyncMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            http_client.client,
            "post",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_post:
            result = await http_client._post("/test", json=request_data)
            assert result == expected_data
            mock_post.assert_called_once_with("/test", json=request_data)
            mock_response.raise_for_status.assert_called_once()
            mock_response.json.assert_awaited_once()
            mock_response.aclose.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_post_failure(self, http_client):
        """Test failed POST request."""
        request_data = {"request": "data"}
        with patch.object(
            http_client.client, "post", side_effect=HTTPError("Connection error")
        ) as mock_post:
            result = await http_client._post("/test", json=request_data)
            assert result is None
            mock_post.assert_called_once_with("/test", json=request_data)

    @pytest.mark.asyncio
    async def test_health_check_success(self, http_client):
        """Test successful health check."""
        health_data = {"status": "healthy"}
        mock_get = AsyncMock(return_value=health_data)

        with patch.object(http_client, "_get", new=mock_get):
            result = await http_client.health_check()
            assert result == health_data
            mock_get.assert_called_once_with("/health")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, http_client):
        """Test failed health check."""
        mock_get = AsyncMock(return_value=None)

        with patch.object(http_client, "_get", new=mock_get):
            result = await http_client.health_check()
            assert result == {"status": "unhealthy"}
            mock_get.assert_called_once_with("/health")

    @pytest.mark.asyncio
    async def test_get_metrics_success(self, http_client):
        """Test successful metrics retrieval."""
        metrics_data = {"requests": 100}
        mock_get = AsyncMock(return_value=metrics_data)

        with patch.object(http_client, "_get", new=mock_get):
            result = await http_client.get_metrics()
            assert result == metrics_data
            mock_get.assert_called_once_with("/metrics")

    @pytest.mark.asyncio
    async def test_get_metrics_failure(self, http_client):
        """Test failed metrics retrieval."""
        mock_get = AsyncMock(return_value=None)

        with patch.object(http_client, "_get", new=mock_get):
            result = await http_client.get_metrics()
            assert result == {"error": "Failed to get metrics"}
            mock_get.assert_called_once_with("/metrics")

    @pytest.mark.asyncio
    async def test_close(self, http_client):
        """Test client close."""
        mock_aclose = AsyncMock()

        with patch.object(http_client.client, "aclose", new=mock_aclose):
            await http_client.close()
            mock_aclose.assert_called_once()

"""Base HTTP client."""

from typing import Any, Dict, Optional

import httpx
from earnbase_common.logging import get_logger
from pydantic import AnyHttpUrl

logger = get_logger(__name__)


class BaseHttpClient:
    """Base HTTP client with common functionality."""

    def __init__(self, base_url: AnyHttpUrl):
        """Initialize client with base URL."""
        self.base_url = str(base_url).rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def _get(self, path: str) -> Optional[Dict[str, Any]]:
        """Send GET request."""
        try:
            response = await self.client.get(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"GET request failed for {path}: {str(e)}")
            return None

    async def _post(self, path: str, json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send POST request."""
        try:
            response = await self.client.post(path, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"POST request failed for {path}: {str(e)}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        result = await self._get("/health")
        return result or {"status": "unhealthy"}

    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        result = await self._get("/metrics")
        return result or {"error": "Failed to get metrics"}

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

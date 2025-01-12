"""Response metadata middleware."""

import time
from typing import Any, Dict, Optional

from earnbase_common.responses import BaseResponse
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class MetadataMiddleware(BaseHTTPMiddleware):
    """Middleware for adding metadata to responses."""

    def __init__(
        self,
        app: ASGIApp,
        service_name: str,
        service_version: str,
        api_version: str,
    ):
        """Initialize middleware."""
        super().__init__(app)
        self.service_name = service_name
        self.service_version = service_version
        self.api_version = api_version

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request."""
        # Track request timing
        request.state.received_at = time.time()

        # Process request
        response = await call_next(request)

        # Add metadata to response
        if hasattr(response, "body"):
            try:
                body = response.body.decode()
                if body:
                    metadata = self._create_metadata(request)
                    # Update response body with metadata
                    response_data = BaseResponse.model_validate_json(body)
                    response_data.meta = metadata
                    response.body = response_data.model_dump_json().encode()
            except Exception:
                # If any error occurs during metadata processing,
                # return original response
                pass

        return response

    def _create_metadata(self, request: Request) -> Dict[str, Any]:
        """Create response metadata."""
        received_at = getattr(request.state, "received_at", time.time())
        responded_at = time.time()

        metadata = {
            "request": {
                "id": getattr(request.state, "request_id", None),
                "received_at": received_at,
                "responded_at": responded_at,
                "duration": round(responded_at - received_at, 6),
            },
            "service": {
                "name": self.service_name,
                "version": self.service_version,
            },
            "api": {
                "version": self.api_version,
            },
        }

        # Add rate limit info if available
        rate_limit = self._get_rate_limit_info(request)
        if rate_limit:
            metadata["rate_limit"] = rate_limit

        return metadata

    def _get_rate_limit_info(self, request: Request) -> Optional[Dict[str, Any]]:
        """Get rate limit information."""
        # Rate limit info will be added by rate limit middleware
        # or from gateway headers
        rate_limit = {}
        headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]

        for header in headers:
            value = request.headers.get(header)
            if value:
                key = header.replace("X-RateLimit-", "").lower()
                rate_limit[key] = value

        return rate_limit if rate_limit else None

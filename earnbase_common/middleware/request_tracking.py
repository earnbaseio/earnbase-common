"""Request tracking middleware."""

import uuid
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from earnbase_common.logging import get_logger

logger = get_logger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking requests."""

    def __init__(self, app: ASGIApp):
        """Initialize middleware."""
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.time()

        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        # Calculate request duration
        duration = time.time() - request.state.start_time

        # Log request details
        logger.info(
            "request_processed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration": duration,
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        return response

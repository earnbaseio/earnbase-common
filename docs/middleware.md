# Middleware

## Overview

The middleware module provides FastAPI middleware components for:
- Request tracking and logging
- Security headers management
- Performance monitoring
- Request/Response transformation

## Features

### Request Tracking

```python
from earnbase_common.middleware import RequestTrackingMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(RequestTrackingMiddleware)

# Features:
# - Unique request ID generation
# - Request timing
# - Detailed request logging
# - Request ID header injection

# Example log output:
{
    "event": "request_processed",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "method": "GET",
    "url": "http://api.example.com/users",
    "status_code": 200,
    "duration": 0.125,
    "client_host": "192.168.1.1",
    "user_agent": "Mozilla/5.0 ..."
}

# Response headers:
# X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

### Security Headers

```python
from earnbase_common.middleware import SecurityHeadersMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)

# Added security headers:
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - X-XSS-Protection: 1; mode=block
# - Strict-Transport-Security: max-age=31536000; includeSubDomains
# - Content-Security-Policy: default-src 'self'; ...
```

## Best Practices

### 1. Middleware Order

```python
from fastapi import FastAPI
from earnbase_common.middleware import (
    RequestTrackingMiddleware,
    SecurityHeadersMiddleware
)

app = FastAPI()

# Order matters - first added = outer layer
app.add_middleware(RequestTrackingMiddleware)  # Executes first
app.add_middleware(SecurityHeadersMiddleware)  # Executes second
```

### 2. Error Handling

```python
from fastapi import FastAPI, Request
from earnbase_common.middleware import BaseMiddleware
from earnbase_common.logging import get_logger

logger = get_logger(__name__)

class ErrorHandlingMiddleware(BaseMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                "request_failed",
                error=str(e),
                request_id=request.state.request_id
            )
            raise
```

### 3. Performance Considerations

```python
from fastapi import FastAPI, Request
from earnbase_common.middleware import BaseMiddleware
from earnbase_common.metrics import metrics

class PerformanceMiddleware(BaseMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        with metrics.request_latency.time():
            response = await call_next(request)
            
        # Track response size
        size = len(response.body)
        metrics.response_size.observe(size)
        
        return response
```

## Future Features

### 1. Rate Limiting

```python
class RateLimitMiddleware(BaseMiddleware):
    """Rate limit requests by IP or token."""
    
    def __init__(
        self,
        app: ASGIApp,
        rate_limit: int,
        time_window: int
    ):
        """Initialize rate limiter."""
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
    
    async def is_rate_limited(
        self,
        key: str
    ) -> bool:
        """Check if request is rate limited."""
        pass
    
    async def update_rate_limit(
        self,
        key: str
    ) -> None:
        """Update rate limit counters."""
        pass
```

### 2. Request Validation

```python
class ValidationMiddleware(BaseMiddleware):
    """Validate requests before processing."""
    
    async def validate_headers(
        self,
        headers: Dict[str, str]
    ) -> None:
        """Validate request headers."""
        pass
    
    async def validate_payload(
        self,
        body: bytes
    ) -> None:
        """Validate request payload."""
        pass
    
    async def validate_query_params(
        self,
        params: Dict[str, str]
    ) -> None:
        """Validate query parameters."""
        pass
```

### 3. Caching

```python
class CacheMiddleware(BaseMiddleware):
    """Cache responses for GET requests."""
    
    async def get_cached_response(
        self,
        key: str
    ) -> Optional[Response]:
        """Get cached response."""
        pass
    
    async def cache_response(
        self,
        key: str,
        response: Response,
        ttl: int
    ) -> None:
        """Cache response with TTL."""
        pass
    
    async def should_cache(
        self,
        request: Request,
        response: Response
    ) -> bool:
        """Determine if response should be cached."""
        pass
```

### 4. Authentication

```python
class AuthMiddleware(BaseMiddleware):
    """Handle authentication and token validation."""
    
    async def validate_token(
        self,
        token: str
    ) -> Dict[str, Any]:
        """Validate authentication token."""
        pass
    
    async def get_user(
        self,
        token_data: Dict[str, Any]
    ) -> Optional[User]:
        """Get user from token data."""
        pass
    
    async def refresh_token(
        self,
        token: str
    ) -> str:
        """Refresh authentication token."""
        pass
```

### 5. Request Transformation

```python
class TransformMiddleware(BaseMiddleware):
    """Transform requests and responses."""
    
    async def transform_request(
        self,
        request: Request
    ) -> Request:
        """Transform incoming request."""
        pass
    
    async def transform_response(
        self,
        response: Response
    ) -> Response:
        """Transform outgoing response."""
        pass
    
    async def compress_response(
        self,
        response: Response
    ) -> Response:
        """Compress response data."""
        pass
``` 
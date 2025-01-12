# Middleware

## Overview

The middleware module provides FastAPI middleware components for common functionality like security headers, request tracking, and metrics collection. These middleware components can be easily added to any FastAPI application.

## Features

### Security Headers Middleware

Adds security headers to all responses:

```python
from fastapi import FastAPI
from earnbase_common.middleware import SecurityHeadersMiddleware

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
```

Added security headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000; includeSubDomains
- Content-Security-Policy: Configurable CSP rules

### Request Tracking Middleware

Tracks and logs request details:

```python
from fastapi import FastAPI
from earnbase_common.middleware import RequestTrackingMiddleware

app = FastAPI()
app.add_middleware(RequestTrackingMiddleware)

@app.get("/users")
async def get_users(request: Request):
    # Access request ID
    request_id = request.state.request_id
    
    # Access start time
    start_time = request.state.start_time
    
    return {"request_id": request_id}
```

Features:
- Generates unique request ID
- Tracks request duration
- Logs request details (method, URL, status, duration)
- Adds request ID to response headers

## Usage

### 1. Basic Setup

```python
from fastapi import FastAPI
from earnbase_common.middleware import (
    SecurityHeadersMiddleware,
    RequestTrackingMiddleware
)

app = FastAPI()

# Add middleware in order
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTrackingMiddleware)
```

### 2. Request Context

Access request context in route handlers:

```python
@app.get("/api/data")
async def get_data(request: Request):
    # Access request tracking info
    request_id = request.state.request_id
    start_time = request.state.start_time
    
    logger.info(
        "Processing request",
        request_id=request_id,
        path="/api/data"
    )
    
    return {"data": "value"}
```

### 3. Custom Headers

Add custom security headers:

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

class CustomHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Add custom headers
        response.headers["X-Custom-Header"] = "value"
        
        return response

app = FastAPI()
app.add_middleware(CustomHeadersMiddleware)
```

## Best Practices

1. **Middleware Order**:
   - Add security middleware first
   - Add request tracking early in the chain
   - Consider dependencies between middleware

2. **Performance**:
   - Keep middleware logic lightweight
   - Avoid blocking operations
   - Use async operations when possible

3. **Error Handling**:
   - Handle exceptions in middleware
   - Preserve error responses
   - Log middleware errors properly

4. **Security**:
   - Validate and sanitize headers
   - Use secure defaults
   - Follow security best practices

## Examples

### 1. Complete Middleware Stack

```python
from fastapi import FastAPI
from earnbase_common.middleware import (
    SecurityHeadersMiddleware,
    RequestTrackingMiddleware
)
from earnbase_common.logging import get_logger

logger = get_logger(__name__)

app = FastAPI()

# Add security headers
app.add_middleware(SecurityHeadersMiddleware)

# Add request tracking
app.add_middleware(RequestTrackingMiddleware)

@app.get("/api/users")
async def get_users(request: Request):
    logger.info(
        "Getting users",
        request_id=request.state.request_id
    )
    return {"users": []}
```

### 2. Custom Tracking Middleware

```python
class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.metrics = get_metrics()
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        # Track request
        with self.metrics.request_duration.labels(
            method=request.method,
            path=request.url.path
        ).time():
            response = await call_next(request)
            
        # Update metrics
        self.metrics.request_count.labels(
            method=request.method,
            path=request.url.path,
            status=response.status_code
        ).inc()
        
        return response
```

### 3. Error Handling Middleware

```python
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors."""
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
            
        except Exception as e:
            logger.error(
                "Request failed",
                request_id=request.state.request_id,
                error=str(e),
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request.state.request_id
                }
            )
```
``` 
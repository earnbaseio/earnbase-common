# HTTP

## Overview

The HTTP module provides two main components:
1. A robust HTTP client for making external requests
2. Utilities and components for building HTTP APIs using FastAPI

## Features

### HTTP Client

```python
from earnbase_common.http import BaseHttpClient
from pydantic import AnyHttpUrl

# Initialize client
client = BaseHttpClient(
    base_url=AnyHttpUrl("https://api.example.com")
)

# Make GET request
data = await client._get("/users")

# Make POST request
response = await client._post(
    "/users",
    json={"name": "John"}
)

# Health check
health = await client.health_check()

# Get metrics
metrics = await client.get_metrics()

# Close client
await client.close()
```

### FastAPI Components

#### Request Context

```python
from earnbase_common.http import RequestContext
from fastapi import Request
from typing import Optional

class APIRequestContext(RequestContext):
    """API request context."""
    
    def __init__(self, request: Request):
        """Initialize context."""
        self.request = request
        self.request_id = self.generate_request_id()
        self.start_time = time.time()
        self.user = None
        self.tenant = None
    
    def generate_request_id(self) -> str:
        """Generate unique request ID."""
        return str(uuid.uuid4())
    
    def get_user(self) -> Optional[dict]:
        """Get authenticated user."""
        return self.user
    
    def set_user(self, user: dict) -> None:
        """Set authenticated user."""
        self.user = user

# Usage in middleware
@app.middleware("http")
async def context_middleware(
    request: Request,
    call_next: RequestHandler
):
    """Setup request context."""
    context = APIRequestContext(request)
    request.state.context = context
    return await call_next(request)
```

#### API Router

```python
from earnbase_common.http import APIRouter
from earnbase_common.responses import Response

router = APIRouter()

@router.get("/users")
async def list_users() -> Response:
    users = await user_service.list_users()
    return Response(data=users)
```

#### Request Validation

```python
from earnbase_common.http import RequestValidator
from pydantic import BaseModel, validator

class CreateUserRequest(BaseModel):
    """Create user request model."""
    email: str
    password: str
    
    @validator("email")
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValidationError("Invalid email format")
        return v

# Usage in route handlers
@router.post("/users")
async def create_user(data: CreateUserRequest) -> Response:
    user = await user_service.create_user(
        email=data.email,
        password=data.password
    )
    return Response(data=user)
```

## Best Practices

### 1. HTTP Client Usage

```python
# Use context manager for automatic cleanup
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com")
    data = response.json()

# Configure timeouts
client = BaseHttpClient(
    base_url="https://api.example.com",
    timeout=30.0
)

# Handle errors gracefully
try:
    response = await client._get("/users")
    if response is None:
        logger.error("Request failed")
    else:
        process_data(response)
finally:
    await client.close()
```

### 2. API Development

```python
# Use dependency injection
def get_user_service(request: Request) -> UserService:
    return request.app.state.user_service

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
) -> Response:
    user = await service.get_user(user_id)
    return Response(data=user)

# Add response documentation
@router.post(
    "/users",
    response_model=Response[User],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse}
    }
)
async def create_user(data: CreateUserRequest) -> Response:
    pass
```

## Future Features

### 1. Enhanced HTTP Client

```python
class EnhancedHttpClient(BaseHttpClient):
    """Enhanced HTTP client with additional features."""
    
    def __init__(
        self,
        base_url: AnyHttpUrl,
        retry_config: RetryConfig,
        auth_config: AuthConfig,
        cache_config: CacheConfig
    ):
        """Initialize enhanced client."""
        super().__init__(base_url)
        self.retry_config = retry_config
        self.auth_config = auth_config
        self.cache_config = cache_config
```

### 2. API Versioning

```python
class VersionedAPIRouter(APIRouter):
    """Router with API versioning."""
    
    def __init__(self, version: str):
        """Initialize router."""
        super().__init__(prefix=f"/v{version}")
```

### 3. Rate Limiting

```python
class RateLimiter:
    """Rate limit requests."""
    
    async def check_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """Check if request is within limit."""
        pass
```

### 4. Circuit Breaker

```python
class CircuitBreaker:
    """Circuit breaker for external calls."""
    
    async def call(
        self,
        func: Callable,
        fallback: Optional[Callable] = None
    ) -> Any:
        """Make call with circuit breaker."""
        pass
```

### 5. Request Tracing

```python
class RequestTracer:
    """Trace requests across services."""
    
    def start_span(
        self,
        name: str,
        parent_id: Optional[str] = None
    ) -> str:
        """Start new trace span."""
        pass
    
    def end_span(self, span_id: str) -> None:
        """End trace span."""
        pass
```

### 6. GraphQL Support

```python
class GraphQLRouter(APIRouter):
    """Router for GraphQL endpoints."""
    
    def add_query(
        self,
        name: str,
        resolver: Callable
    ) -> None:
        """Add GraphQL query."""
        pass
    
    def add_mutation(
        self,
        name: str,
        resolver: Callable
    ) -> None:
        """Add GraphQL mutation."""
        pass
``` 
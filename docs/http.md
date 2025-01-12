# HTTP

## Overview

The HTTP module provides a robust HTTP client implementation using `httpx` for making HTTP requests. It includes automatic error handling, logging, and common functionality like health checks and metrics collection.

## Features

### Base HTTP Client

The `BaseHttpClient` class provides a foundation for making HTTP requests:

```python
from earnbase_common.http import BaseHttpClient
from pydantic import AnyHttpUrl

# Initialize client
client = BaseHttpClient(
    base_url=AnyHttpUrl("https://api.example.com")
)

# Make requests
data = await client.get("/users")
result = await client.post("/users", json={"name": "John"})

# Health check
health = await client.health_check()
print(health)  # {"status": "healthy"}

# Get metrics
metrics = await client.get_metrics()
print(metrics)  # {"requests": 100, "errors": 0}

# Close client
await client.close()
```

## Key Features

### 1. Automatic Error Handling

Built-in error handling and logging:

```python
try:
    data = await client.get("/users")
    if data is None:
        # Request failed, error was logged
        handle_error()
except Exception as e:
    logger.error("Request failed", error=str(e))
```

### 2. Type Safety

Type hints and Pydantic models for request/response data:

```python
from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Dict, Any

class User(BaseModel):
    name: str
    email: str

class UserClient(BaseHttpClient):
    async def create_user(self, user: User) -> Optional[Dict[str, Any]]:
        return await self._post("/users", json=user.model_dump())

    async def get_user(self, user_id: str) -> Optional[User]:
        data = await self._get(f"/users/{user_id}")
        return User(**data) if data else None
```

### 3. Health Checks

Built-in health check support:

```python
async def check_service_health():
    client = BaseHttpClient(base_url="https://api.example.com")
    health = await client.health_check()
    
    if health["status"] == "healthy":
        logger.info("Service is healthy")
    else:
        logger.error("Service is unhealthy")
```

### 4. Metrics Collection

Automatic metrics collection:

```python
async def collect_metrics():
    client = BaseHttpClient(base_url="https://api.example.com")
    metrics = await client.get_metrics()
    
    # Process metrics
    requests = metrics.get("requests", 0)
    errors = metrics.get("errors", 0)
    latency = metrics.get("latency", {})
```

## Best Practices

1. **Resource Management**:
   - Always close clients when done
   - Use async context managers when possible
   - Handle connection timeouts properly

2. **Error Handling**:
   - Check for None return values
   - Log errors with context
   - Handle network errors gracefully

3. **Type Safety**:
   - Use Pydantic models for request/response data
   - Add proper type hints
   - Validate URLs with AnyHttpUrl

4. **Performance**:
   - Reuse client instances
   - Configure appropriate timeouts
   - Use connection pooling for multiple requests

5. **Security**:
   - Use HTTPS for all requests
   - Handle sensitive data properly
   - Validate server certificates

## Examples

### 1. Extended Client

```python
class APIClient(BaseHttpClient):
    """Extended API client with custom methods."""
    
    async def get_users(
        self,
        page: int = 1,
        limit: int = 10
    ) -> Optional[Dict[str, Any]]:
        """Get paginated users."""
        return await self._get(
            f"/users?page={page}&limit={limit}"
        )
    
    async def create_user(
        self,
        user_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create new user."""
        return await self._post(
            "/users",
            json=user_data
        )
```

### 2. Service Client

```python
class ServiceClient(BaseHttpClient):
    """Client for internal service communication."""
    
    async def notify(
        self,
        event: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Send notification to service."""
        result = await self._post(
            "/events",
            json={
                "event": event,
                "payload": payload
            }
        )
        return result is not None
```

### 3. Authenticated Client

```python
class AuthClient(BaseHttpClient):
    """Client with authentication."""
    
    def __init__(
        self,
        base_url: AnyHttpUrl,
        api_key: str
    ):
        """Initialize with API key."""
        super().__init__(base_url)
        self.client.headers["Authorization"] = f"Bearer {api_key}"
    
    async def get_protected_resource(
        self
    ) -> Optional[Dict[str, Any]]:
        """Get protected resource."""
        return await self._get("/protected")
```
``` 
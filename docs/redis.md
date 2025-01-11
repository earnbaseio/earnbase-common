# Redis

## Overview

The Redis module provides an asynchronous Redis client with features like:
- Connection management with automatic reconnection
- Key prefixing for namespace isolation
- JSON serialization for complex data types
- Automatic TTL management
- Error handling and logging

## Features

### Basic Usage

```python
from earnbase_common.redis import redis_client

# Connect to Redis
await redis_client.connect(
    url="redis://localhost:6379",
    db=0,
    prefix="myapp:",
    ttl=3600  # 1 hour default TTL
)

# Store data
user = {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
}
await redis_client.set("user:123", user)

# Retrieve data
user = await redis_client.get("user:123")
if user:
    print(user["name"])  # John Doe

# Delete data
await redis_client.delete("user:123")

# Check existence
exists = await redis_client.exists("user:123")

# Close connection
await redis_client.close()
```

### Key Management

```python
from earnbase_common.redis import RedisClient

# Create client with prefix
client = RedisClient()
await client.connect(
    url="redis://localhost:6379",
    prefix="myapp:prod:"  # All keys will be prefixed
)

# Keys will be automatically prefixed
await client.set("users:count", 42)
# Actual Redis key: "myapp:prod:users:count"

# TTL management
await client.set(
    "cache:data",
    {"key": "value"},
    ttl=300  # 5 minutes TTL
)
```

### Error Handling

```python
from earnbase_common.redis import RedisClient
from earnbase_common.logging import get_logger

logger = get_logger(__name__)

async def cache_data():
    try:
        # Attempt to store data
        success = await redis_client.set(
            "cache:key",
            {"data": "value"}
        )
        if not success:
            logger.error("Failed to cache data")
            
    except RuntimeError as e:
        # Handle connection errors
        logger.error(
            "redis_error",
            error=str(e),
            operation="cache_data"
        )
```

## Best Practices

### 1. Connection Management

```python
from contextlib import asynccontextmanager
from earnbase_common.redis import RedisClient

@asynccontextmanager
async def get_redis():
    """Get Redis client with automatic cleanup."""
    client = RedisClient()
    try:
        await client.connect(
            url="redis://localhost:6379",
            prefix="myapp:"
        )
        yield client
    finally:
        await client.close()

# Usage
async def process_data():
    async with get_redis() as redis:
        await redis.set("key", "value")
```

### 2. Key Namespacing

```python
class UserCache:
    """User cache with namespaced keys."""
    
    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.prefix = "users:"
    
    def get_key(self, user_id: str) -> str:
        """Get namespaced key."""
        return f"{self.prefix}{user_id}"
    
    async def cache_user(self, user_id: str, data: dict):
        """Cache user data."""
        key = self.get_key(user_id)
        await self.redis.set(key, data)
```

### 3. Data Serialization

```python
from datetime import datetime
from typing import Any

class CacheSerializer:
    """Serializer for cache data."""
    
    @staticmethod
    def serialize(data: Any) -> str:
        """Serialize data for caching."""
        if isinstance(data, datetime):
            return data.isoformat()
        return str(data)
    
    @staticmethod
    def deserialize(data: str, type_: type) -> Any:
        """Deserialize cached data."""
        if type_ == datetime:
            return datetime.fromisoformat(data)
        return type_(data)
```

## Future Features

### 1. Redis Cluster Support

```python
class RedisClusterClient(RedisClient):
    """Redis cluster client."""
    
    async def connect_to_cluster(
        self,
        nodes: List[str],
        replica_factor: int = 1
    ) -> None:
        """Connect to Redis cluster."""
        pass
    
    async def get_node_status(
        self,
        node: str
    ) -> Dict[str, Any]:
        """Get node status."""
        pass
    
    async def rebalance_cluster(self) -> None:
        """Rebalance cluster data."""
        pass
```

### 2. Caching Patterns

```python
class CachePattern:
    """Common caching patterns."""
    
    async def cache_aside(
        self,
        key: str,
        getter: Callable,
        ttl: int
    ) -> Any:
        """Cache-aside pattern."""
        pass
    
    async def write_through(
        self,
        key: str,
        value: Any,
        setter: Callable
    ) -> None:
        """Write-through pattern."""
        pass
    
    async def write_behind(
        self,
        key: str,
        value: Any,
        setter: Callable
    ) -> None:
        """Write-behind pattern."""
        pass
```

### 3. Pub/Sub Support

```python
class RedisPubSub:
    """Redis pub/sub support."""
    
    async def subscribe(
        self,
        channel: str,
        handler: Callable
    ) -> None:
        """Subscribe to channel."""
        pass
    
    async def publish(
        self,
        channel: str,
        message: Any
    ) -> int:
        """Publish message to channel."""
        pass
    
    async def pattern_subscribe(
        self,
        pattern: str,
        handler: Callable
    ) -> None:
        """Subscribe to pattern."""
        pass
```

### 4. Cache Invalidation

```python
class CacheInvalidator:
    """Cache invalidation strategies."""
    
    async def invalidate_by_prefix(
        self,
        prefix: str
    ) -> int:
        """Invalidate keys by prefix."""
        pass
    
    async def invalidate_by_pattern(
        self,
        pattern: str
    ) -> int:
        """Invalidate keys by pattern."""
        pass
    
    async def invalidate_by_tag(
        self,
        tag: str
    ) -> int:
        """Invalidate keys by tag."""
        pass
```

### 5. Rate Limiting

```python
class RedisRateLimiter:
    """Rate limiting using Redis."""
    
    async def check_rate(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """Check rate limit."""
        pass
    
    async def get_remaining(
        self,
        key: str
    ) -> int:
        """Get remaining requests."""
        pass
    
    async def reset_counter(
        self,
        key: str
    ) -> None:
        """Reset rate limit counter."""
        pass
``` 
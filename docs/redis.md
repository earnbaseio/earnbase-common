# Redis

## Overview

The Redis module provides a robust Redis client implementation with support for caching, session management, and key-value operations. It includes features like connection pooling, key prefixing, automatic TTL management, and structured logging.

## Features

### Redis Client

The `RedisClient` class provides a high-level interface for Redis operations:

```python
from earnbase_common.redis import RedisClient

# Connect to Redis
redis = await RedisClient.connect(
    url="redis://localhost:6379",
    db=0,
    prefix="myapp",  # Optional key prefix
    ttl=3600        # Default TTL in seconds
)

# Basic operations
await redis.set("user:123", "John Doe")
value = await redis.get("user:123")  # "John Doe"

# Custom expiration
await redis.set("session:abc", "data", expire=1800)  # 30 minutes

# Check existence
exists = await redis.exists("user:123")  # True

# Delete key
await redis.delete("user:123")

# Get TTL
ttl = await redis.ttl("session:abc")  # Seconds remaining

# Close connection
await redis.close()
```

### Caching

Example of using Redis for caching:

```python
from earnbase_common.redis import RedisClient
import json

class Cache:
    def __init__(self, redis: RedisClient):
        self.redis = redis

    async def get_or_set(
        self,
        key: str,
        factory,
        expire: int = 3600
    ):
        """Get cached value or compute and cache it."""
        # Try to get from cache
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # Compute value
        value = await factory()
        
        # Cache value
        await self.redis.set(
            key,
            json.dumps(value),
            expire=expire
        )
        
        return value

# Usage
cache = Cache(redis)
user = await cache.get_or_set(
    "user:123",
    lambda: fetch_user_from_db("123"),
    expire=300  # 5 minutes
)
```

### Session Management

Example of session handling with Redis:

```python
from earnbase_common.redis import RedisClient
from uuid import uuid4
import json

class Session:
    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.prefix = "session"
        self.ttl = 1800  # 30 minutes

    async def create(self, data: dict) -> str:
        """Create new session."""
        session_id = str(uuid4())
        key = f"{self.prefix}:{session_id}"
        
        await self.redis.set(
            key,
            json.dumps(data),
            expire=self.ttl
        )
        
        return session_id

    async def get(self, session_id: str) -> dict:
        """Get session data."""
        key = f"{self.prefix}:{session_id}"
        data = await self.redis.get(key)
        
        if not data:
            raise ValueError("Session not found")
            
        return json.loads(data)

    async def update(
        self,
        session_id: str,
        data: dict
    ) -> None:
        """Update session data."""
        key = f"{self.prefix}:{session_id}"
        
        if not await self.redis.exists(key):
            raise ValueError("Session not found")
            
        await self.redis.set(
            key,
            json.dumps(data),
            expire=self.ttl
        )

    async def delete(self, session_id: str) -> None:
        """Delete session."""
        key = f"{self.prefix}:{session_id}"
        await self.redis.delete(key)

# Usage
session = Session(redis)

# Create session
session_id = await session.create({
    "user_id": "123",
    "role": "admin"
})

# Get session
data = await session.get(session_id)

# Update session
data["last_access"] = "2024-01-12T00:00:00Z"
await session.update(session_id, data)

# Delete session
await session.delete(session_id)
```

## Key Features

### 1. Connection Management

- Automatic connection handling
- Connection pooling
- Graceful disconnection
- Connection testing with PING

### 2. Key Management

- Optional key prefixing
- Default TTL configuration
- Custom expiration times
- TTL querying

### 3. Error Handling

- Structured error logging
- Connection error handling
- Operation error handling
- Runtime checks

### 4. Performance

- Connection pooling
- Async operations
- Minimal overhead
- Efficient key prefixing

## Best Practices

1. **Connection Management**:
   - Use connection pooling
   - Handle disconnections gracefully
   - Close connections properly
   - Monitor connection health

2. **Key Design**:
   - Use meaningful key prefixes
   - Set appropriate TTLs
   - Handle key collisions
   - Use consistent naming

3. **Error Handling**:
   - Handle connection errors
   - Log operation failures
   - Implement retries
   - Validate inputs

4. **Performance**:
   - Use appropriate data structures
   - Set reasonable TTLs
   - Monitor memory usage
   - Implement caching strategies

## Examples

### 1. Rate Limiting

```python
from earnbase_common.redis import RedisClient
from datetime import datetime

class RateLimiter:
    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.prefix = "ratelimit"

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """Check if operation is allowed."""
        redis_key = f"{self.prefix}:{key}"
        
        # Get current count
        count = await self.redis.get(redis_key)
        if not count:
            # First request
            await self.redis.set(redis_key, "1", expire=window)
            return True
            
        if int(count) >= limit:
            return False
            
        # Increment counter
        await self.redis.set(
            redis_key,
            str(int(count) + 1),
            expire=window
        )
        return True

# Usage
limiter = RateLimiter(redis)

# Allow 5 requests per minute
allowed = await limiter.is_allowed(
    "user:123",
    limit=5,
    window=60
)
```

### 2. Distributed Lock

```python
from earnbase_common.redis import RedisClient
from uuid import uuid4
import asyncio

class Lock:
    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.prefix = "lock"

    async def acquire(
        self,
        key: str,
        timeout: int = 10
    ) -> str:
        """Acquire lock."""
        lock_id = str(uuid4())
        redis_key = f"{self.prefix}:{key}"
        
        deadline = asyncio.get_event_loop().time() + timeout
        
        while True:
            # Try to acquire lock
            acquired = await self.redis.set(
                redis_key,
                lock_id,
                expire=timeout
            )
            
            if acquired:
                return lock_id
                
            # Check timeout
            if asyncio.get_event_loop().time() >= deadline:
                raise TimeoutError("Lock acquisition timeout")
                
            await asyncio.sleep(0.1)

    async def release(
        self,
        key: str,
        lock_id: str
    ) -> None:
        """Release lock."""
        redis_key = f"{self.prefix}:{key}"
        
        # Check lock ownership
        current_id = await self.redis.get(redis_key)
        if current_id == lock_id:
            await self.redis.delete(redis_key)

# Usage
lock = Lock(redis)

# Acquire lock
lock_id = await lock.acquire("resource:123", timeout=10)

try:
    # Do something with resource
    pass
finally:
    # Release lock
    await lock.release("resource:123", lock_id)
```

### 3. Pub/Sub

```python
from earnbase_common.redis import RedisClient
import json
import asyncio

class PubSub:
    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.prefix = "channel"

    async def publish(
        self,
        channel: str,
        message: dict
    ) -> None:
        """Publish message to channel."""
        redis_channel = f"{self.prefix}:{channel}"
        await self.redis.publish(
            redis_channel,
            json.dumps(message)
        )

    async def subscribe(
        self,
        channel: str,
        callback
    ) -> None:
        """Subscribe to channel."""
        redis_channel = f"{self.prefix}:{channel}"
        pubsub = self.redis.pubsub()
        
        await pubsub.subscribe(redis_channel)
        
        try:
            while True:
                message = await pubsub.get_message()
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    await callback(data)
                    
                await asyncio.sleep(0.01)
                
        finally:
            await pubsub.unsubscribe(redis_channel)

# Usage
pubsub = PubSub(redis)

# Publisher
await pubsub.publish(
    "notifications",
    {
        "type": "user_created",
        "user_id": "123"
    }
)

# Subscriber
async def handle_message(data: dict):
    print(f"Received: {data}")

await pubsub.subscribe("notifications", handle_message)
```
``` 
# Database

## Overview

The database module provides a robust MongoDB integration with repository pattern support. It includes automatic retries, connection pooling, metrics collection, and type-safe operations.

## Features

### MongoDB Client

The `MongoDB` class provides a high-level interface for MongoDB operations:

```python
from earnbase_common.database import MongoDB

# Initialize and connect
mongodb = MongoDB()
await mongodb.connect(
    url="mongodb://localhost:27017",
    db_name="mydb",
    min_pool_size=10,
    max_pool_size=100
)

# Basic operations
doc = await mongodb.find_one("users", {"email": "user@example.com"})
docs = await mongodb.find_many("users", {"status": "active"}, limit=10)
user_id = await mongodb.insert_one("users", {"name": "John"})
```

### Repository Pattern

The `BaseRepository` provides a type-safe repository pattern implementation:

```python
from earnbase_common.database import BaseRepository
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    status: str = "active"

class UserRepository(BaseRepository[User]):
    """User repository."""
    
    def __init__(self, mongodb: MongoDB):
        """Initialize repository."""
        super().__init__(
            collection=mongodb.db["users"],
            model=User
        )

# Usage
repo = UserRepository(mongodb)
user = await repo.find_one({"email": "user@example.com"})
users = await repo.find_many({"status": "active"})
```

## Key Features

### 1. Automatic Retries

MongoDB operations are automatically retried with configurable settings:

```python
from earnbase_common.retry import RetryConfig

retry_config = RetryConfig(
    max_attempts=3,
    max_delay=5.0,
    min_delay=1.0,
    exceptions=(ConnectionFailure, ServerSelectionTimeoutError)
)

mongodb = MongoDB()
await mongodb.connect(
    url="mongodb://localhost:27017",
    db_name="mydb",
    retry_config=retry_config
)
```

### 2. Connection Pooling

Built-in connection pooling support:

```python
# Configure pool size
mongodb = MongoDB()
await mongodb.connect(
    url="mongodb://localhost:27017",
    db_name="mydb",
    min_pool_size=10,  # Minimum connections
    max_pool_size=100  # Maximum connections
)
```

### 3. Metrics Collection

Automatic metrics collection for database operations:

```python
# Metrics are automatically collected
with db_operation_latency.labels(
    operation="find_one",
    collection=self.collection.name
).time():
    result = await self.collection.find_one(filter)
    db_operation_count.labels(
        operation="find_one",
        collection=self.collection.name
    ).inc()
```

### 4. Type Safety

Repository pattern with Pydantic models for type safety:

```python
class Product(BaseModel):
    name: str
    price: float
    stock: int = 0

class ProductRepository(BaseRepository[Product]):
    """Product repository with type safety."""
    pass

# Type-safe operations
product = await repo.find_one({"name": "Phone"})
print(product.price)  # Type hints work
```

## Basic Operations

### 1. Query Operations

```python
# Find one document
doc = await mongodb.find_one(
    collection="users",
    query={"email": "user@example.com"},
    projection={"password": 0}
)

# Find many documents
docs = await mongodb.find_many(
    collection="users",
    query={"status": "active"},
    sort=[("created_at", -1)],
    skip=0,
    limit=10
)

# Count documents
count = await mongodb.count_documents(
    collection="users",
    query={"status": "active"}
)
```

### 2. Write Operations

```python
# Insert operations
doc_id = await mongodb.insert_one(
    collection="users",
    document={"name": "John", "email": "john@example.com"}
)

doc_ids = await mongodb.insert_many(
    collection="users",
    documents=[
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"}
    ]
)

# Update operations
modified = await mongodb.update_one(
    collection="users",
    query={"email": "john@example.com"},
    update={"$set": {"status": "active"}},
    upsert=False
)

modified = await mongodb.update_many(
    collection="users",
    query={"status": "inactive"},
    update={"$set": {"status": "active"}},
    upsert=False
)

# Delete operations
deleted = await mongodb.delete_one(
    collection="users",
    query={"email": "john@example.com"}
)

deleted = await mongodb.delete_many(
    collection="users",
    query={"status": "inactive"}
)
```

### 3. Index Management

```python
# Create index
index_name = await mongodb.create_index(
    collection="users",
    keys=[("email", 1)],
    unique=True,
    sparse=False,
    background=True
)

# Drop index
await mongodb.drop_index(
    collection="users",
    index_name="email_1"
)

# List indexes
indexes = await mongodb.list_indexes(
    collection="users"
)
```

## Repository Pattern Usage

### 1. Basic Repository

```python
class UserRepository(BaseRepository[User]):
    """Basic user repository."""
    pass

# Basic operations
user = await repo.find_one({"email": "user@example.com"})
users = await repo.find_many(
    filter={"status": "active"},
    skip=0,
    limit=10,
    sort=[("created_at", -1)]
)
```

### 2. Extended Repository

```python
class UserRepository(BaseRepository[User]):
    """Extended user repository with custom methods."""
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        return await self.find_one({"email": email})
    
    async def find_active_users(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> List[User]:
        """Find active users."""
        return await self.find_many(
            filter={"status": "active"},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate user."""
        return await self.update(
            filter={"_id": user_id},
            data={"status": "inactive"}
        )
```

## Best Practices

### 1. Connection Management

```python
# In your application startup
async def startup():
    mongodb = MongoDB()
    try:
        await mongodb.connect(
            url=settings.MONGODB_URL,
            db_name=settings.MONGODB_DB_NAME
        )
        # Verify connection
        if not await mongodb.ping():
            raise ConnectionError("MongoDB connection failed")
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise

# In your application shutdown
async def shutdown():
    await mongodb.close()
```

### 2. Error Handling

```python
try:
    result = await mongodb.find_one("users", {"_id": "invalid-id"})
except ConnectionError as e:
    logger.error("MongoDB connection error", error=str(e))
    raise
except PyMongoError as e:
    logger.error("MongoDB operation error", error=str(e))
    raise
```

### 3. Repository Implementation

```python
class BaseUserRepository(Protocol):
    """User repository protocol."""
    
    async def find_by_email(self, email: str) -> Optional[User]: ...
    async def find_active_users(self) -> List[User]: ...

class MongoUserRepository(BaseRepository[User], BaseUserRepository):
    """MongoDB user repository implementation."""
    
    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.find_one({"email": email})
    
    async def find_active_users(self) -> List[User]:
        return await self.find_many({"status": "active"})
```
``` 
# Earnbase Common Module

Common utilities and shared functionality for Earnbase Platform services.

## Installation

### Development Environment

```bash
# Install from local source
cd earnbase-common
pdm install -e .
```

### Production Environment

```bash
# Install from private registry
pdm add earnbase-common
```

## Service Configuration

Add dependency to `pyproject.toml`:

```toml
[project]
dependencies = [
    "earnbase-common @ {root:uri}/earnbase-common",  # For development
    # or
    "earnbase-common>=0.1.0",  # For production
]
```

## Using MongoDB Client

### Initialize Connection

```python
from earnbase_common.database import mongodb
from earnbase_common.logging import get_logger

logger = get_logger(__name__)

async def startup():
    """Initialize MongoDB connection when service starts."""
    await mongodb.connect(
        url="mongodb://localhost:27017",
        db_name="earnbase",
        min_pool_size=10,
        max_pool_size=100
    )

async def shutdown():
    """Close MongoDB connection when service shuts down."""
    await mongodb.close()
```

### Collection Operations

```python
# Find one document
user = await mongodb.find_one(
    collection="users",
    query={"email": "user@example.com"}
)

# Find multiple documents
users = await mongodb.find_many(
    collection="users",
    query={"is_active": True},
    sort=[("created_at", -1)],
    skip=0,
    limit=10
)

# Insert document
user_id = await mongodb.insert_one(
    collection="users",
    document={
        "email": "new@example.com",
        "name": "New User"
    }
)

# Update document
modified_count = await mongodb.update_one(
    collection="users",
    query={"_id": user_id},
    update={
        "$set": {"is_active": False}
    }
)

# Delete document
deleted_count = await mongodb.delete_one(
    collection="users",
    query={"_id": user_id}
)

# Count documents
total = await mongodb.count_documents(
    collection="users",
    query={"is_active": True}
)
```

### Index Management

```python
# Create index
await mongodb.create_index(
    collection="users",
    keys=[("email", 1)],
    unique=True
)

# Drop index
await mongodb.drop_index(
    collection="users",
    index_name="email_1"
)

# List indexes
indexes = await mongodb.list_indexes(collection="users")
```

### Error Handling

```python
from pymongo.errors import PyMongoError

try:
    await mongodb.insert_one(collection="users", document=user_data)
except PyMongoError as e:
    logger.error(
        "mongodb_error",
        operation="insert_user",
        error=str(e),
        error_type=type(e).__name__
    )
    raise
```

## Logging

### Logging Configuration

```python
from earnbase_common.logging import configure_logging, get_logger

# Configure logging when service starts
configure_logging()

# Use logger
logger = get_logger(__name__)

logger.info("user_created", user_id=user_id, email=email)
logger.error("operation_failed", error=str(error))
```

## Error Handling

### Using Exception Handlers

```python
from earnbase_common.errors import (
    APIError,
    ValidationError,
    NotFoundError,
    register_error_handlers
)
from fastapi import FastAPI

app = FastAPI()

# Register error handlers
register_error_handlers(app)

# Use exceptions
async def get_user(user_id: str):
    user = await mongodb.find_one("users", {"_id": user_id})
    if not user:
        raise NotFoundError(
            message="User not found",
            details={"user_id": user_id}
        )
    return user
```

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License 
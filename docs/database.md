# Database

## Overview

The database module provides a high-level interface for working with MongoDB in an asynchronous way. It includes connection management, CRUD operations, and a generic repository pattern with built-in metrics and logging.

## Features

### MongoDB Connection

```python
from earnbase_common.database import mongodb
from earnbase_common.config import BaseSettings

# Configure MongoDB
settings = BaseSettings("config.yaml")
await mongodb.connect(
    url=settings.MONGODB_URL,
    db_name=settings.MONGODB_DB_NAME,
    min_pool_size=settings.MONGODB_MIN_POOL_SIZE,
    max_pool_size=settings.MONGODB_MAX_POOL_SIZE
)

# Check connection
is_connected = await mongodb.ping()

# Close connection
await mongodb.close()
```

### Basic CRUD Operations

```python
from earnbase_common.database import mongodb
from typing import Dict, Any

# Find operations
user = await mongodb.find_one(
    collection="users",
    query={"email": "user@example.com"}
)

users = await mongodb.find_many(
    collection="users",
    query={"status": "active"},
    sort=[("created_at", -1)],
    skip=0,
    limit=10
)

# Insert operations
user_id = await mongodb.insert_one(
    collection="users",
    document={"email": "new@example.com"}
)

user_ids = await mongodb.insert_many(
    collection="users",
    documents=[
        {"email": "user1@example.com"},
        {"email": "user2@example.com"}
    ]
)

# Update operations
modified_count = await mongodb.update_one(
    collection="users",
    query={"_id": user_id},
    update={"$set": {"status": "inactive"}},
    upsert=False
)

# Delete operations
deleted_count = await mongodb.delete_one(
    collection="users",
    query={"_id": user_id}
)

# Count documents
total = await mongodb.count_documents(
    collection="users",
    query={"status": "active"}
)
```

### Generic Repository

```python
from earnbase_common.database import BaseRepository
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """User model."""
    id: str
    email: str
    name: Optional[str] = None
    status: str = "active"
    created_at: datetime
    updated_at: datetime

class UserRepository(BaseRepository[User]):
    """User repository."""
    
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
    
    async def create_user(
        self,
        email: str,
        name: Optional[str] = None
    ) -> User:
        """Create new user."""
        return await self.create({
            "email": email,
            "name": name,
            "status": "active"
        })
    
    async def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate user."""
        return await self.update(
            filter={"_id": user_id},
            data={"status": "inactive"}
        )

# Usage
user_repo = UserRepository(mongodb.db.users, User)
user = await user_repo.create_user("user@example.com")
users = await user_repo.find_active_users(limit=10)
```

## Best Practices

### 1. Connection Management

```python
from earnbase_common.database import mongodb
from contextlib import asynccontextmanager

class DatabaseManager:
    """Manage database connections."""
    
    def __init__(self, settings: BaseSettings):
        """Initialize manager."""
        self.settings = settings
    
    async def connect(self) -> None:
        """Connect to database."""
        await mongodb.connect(
            url=self.settings.MONGODB_URL,
            db_name=self.settings.MONGODB_DB_NAME,
            min_pool_size=self.settings.MONGODB_MIN_POOL_SIZE,
            max_pool_size=self.settings.MONGODB_MAX_POOL_SIZE
        )
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
        await mongodb.close()
    
    @asynccontextmanager
    async def connection(self):
        """Get database connection."""
        await self.connect()
        try:
            yield mongodb
        finally:
            await self.disconnect()

# Usage
db_manager = DatabaseManager(settings)
async with db_manager.connection() as db:
    users = await db.find_many("users", {"status": "active"})
```

### 2. Error Handling

```python
from earnbase_common.database import mongodb
from pymongo.errors import PyMongoError
from earnbase_common.errors import DatabaseError

class DatabaseClient:
    """Database client with error handling."""
    
    async def safe_operation(self, operation: str) -> Any:
        """Execute database operation safely."""
        try:
            if not await mongodb.ping():
                raise ConnectionError("Database not connected")
                
            result = await getattr(mongodb, operation)()
            return result
            
        except PyMongoError as e:
            logger.error(
                "database_error",
                operation=operation,
                error=str(e)
            )
            raise DatabaseError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            logger.error(
                "unexpected_error",
                operation=operation,
                error=str(e)
            )
            raise

# Usage
client = DatabaseClient()
try:
    result = await client.safe_operation("find_one")
except DatabaseError as e:
    # Handle database error
    pass
```

### 3. Repository Pattern

```python
from earnbase_common.database import BaseRepository
from typing import TypeVar, Generic

T = TypeVar("T", bound=BaseModel)

class Repository(Generic[T]):
    """Generic repository interface."""
    
    async def find_by_id(self, id: str) -> Optional[T]:
        """Find by ID."""
        pass
    
    async def find_all(self) -> List[T]:
        """Find all."""
        pass
    
    async def create(self, data: Dict[str, Any]) -> T:
        """Create new."""
        pass
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update existing."""
        pass
    
    async def delete(self, id: str) -> bool:
        """Delete existing."""
        pass

class MongoRepository(Repository[T], BaseRepository[T]):
    """MongoDB repository implementation."""
    
    async def find_by_id(self, id: str) -> Optional[T]:
        """Find by ID."""
        return await self.find_one({"_id": id})
    
    async def find_all(self) -> List[T]:
        """Find all."""
        return await self.find_many({})
```

## Advanced Usage

### Transactions

```python
from earnbase_common.database import mongodb
from motor.motor_asyncio import AsyncIOMotorClientSession

async def transfer_money(
    from_account: str,
    to_account: str,
    amount: float
) -> bool:
    """Transfer money between accounts."""
    async with await mongodb.client.start_session() as session:
        async with session.start_transaction():
            try:
                # Deduct from source
                await mongodb.update_one(
                    collection="accounts",
                    query={"_id": from_account},
                    update={"$inc": {"balance": -amount}},
                    session=session
                )
                
                # Add to destination
                await mongodb.update_one(
                    collection="accounts",
                    query={"_id": to_account},
                    update={"$inc": {"balance": amount}},
                    session=session
                )
                
                await session.commit_transaction()
                return True
                
            except Exception as e:
                await session.abort_transaction()
                logger.error("transfer_failed", error=str(e))
                return False
```

### Indexes

```python
from earnbase_common.database import mongodb

# Create indexes
await mongodb.create_index(
    collection="users",
    keys=[("email", 1)],
    unique=True
)

await mongodb.create_index(
    collection="orders",
    keys=[
        ("user_id", 1),
        ("created_at", -1)
    ],
    background=True
)

# List indexes
indexes = await mongodb.list_indexes("users")

# Drop index
await mongodb.drop_index("users", "email_1")
```

### Aggregation

```python
from earnbase_common.database import mongodb

async def get_user_stats() -> Dict[str, Any]:
    """Get user statistics."""
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_age": {"$avg": "$age"}
            }
        },
        {
            "$project": {
                "status": "$_id",
                "count": 1,
                "avg_age": 1,
                "_id": 0
            }
        }
    ]
    
    return await mongodb.db.users.aggregate(pipeline).to_list(None)
``` 
# Responses

## Overview

The Responses module provides standardized response models for FastAPI applications with features like:
- Base response models with success/error handling
- Consistent JSON response format
- Pagination support
- Detailed error responses with metadata

## Features

### Basic Usage

```python
from earnbase_common.responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse
)

# Success response
async def get_user(user_id: str):
    user = await db.get_user(user_id)
    return SuccessResponse(
        data=user,
        message="User retrieved successfully"
    )

# Error response
async def create_user(user_data: dict):
    try:
        user = await db.create_user(user_data)
        return SuccessResponse(
            data=user,
            message="User created successfully"
        )
    except ValidationError as e:
        return ErrorResponse(
            error="Invalid user data",
            details=e.errors()
        )

# Paginated response
async def list_users(page: int = 1, per_page: int = 10):
    users = await db.get_users(
        skip=(page - 1) * per_page,
        limit=per_page
    )
    total = await db.count_users()
    
    return PaginatedResponse(
        data=users,
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    )
```

### Response Models

#### BaseResponse

```python
from earnbase_common.responses import BaseResponse

response = BaseResponse(
    success=True,
    message="Operation successful",
    code="USER_CREATED"
)
```

Fields:
- `success`: bool - Whether the request was successful
- `message`: Optional[str] - Response message
- `code`: Optional[str] - Response code

#### SuccessResponse

```python
from earnbase_common.responses import SuccessResponse

response = SuccessResponse(
    data={"id": "123", "name": "John"},
    message="User found",
    meta={"version": "1.0"}
)
```

Fields:
- Inherits from `BaseResponse`
- `data`: Optional[Any] - Response data
- `meta`: Optional[Dict[str, Any]] - Response metadata

#### ErrorResponse

```python
from earnbase_common.responses import ErrorResponse

response = ErrorResponse(
    error="User not found",
    details={"user_id": "123"},
    errors=[
        {
            "field": "email",
            "message": "Invalid email format"
        }
    ]
)
```

Fields:
- Inherits from `BaseResponse`
- `error`: str - Error message
- `details`: Optional[Dict[str, Any]] - Error details
- `errors`: Optional[List[Dict[str, Any]]] - List of validation errors

#### PaginatedResponse

```python
from earnbase_common.responses import PaginatedResponse

response = PaginatedResponse(
    data=[user1, user2, user3],
    meta={
        "page": 1,
        "per_page": 10,
        "total": 100,
        "total_pages": 10
    }
)
```

Fields:
- `data`: List[Any] - List of items
- `meta`: PaginationMetadata - Pagination metadata

### Custom JSON Response

```python
from fastapi import FastAPI
from earnbase_common.responses import CustomJSONResponse

app = FastAPI(
    default_response_class=CustomJSONResponse
)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # Response will be wrapped in {"data": ...}
    return {
        "id": user_id,
        "name": "John Doe"
    }
```

## Best Practices

### 1. Consistent Response Format

```python
# Good - Using standard response models
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        user = await db.get_user(user_id)
        return SuccessResponse(
            data=user,
            message="User retrieved"
        )
    except NotFoundError:
        return ErrorResponse(
            error="User not found",
            details={"user_id": user_id}
        )

# Bad - Inconsistent response format
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.get_user(user_id)
    if not user:
        return {"error": "Not found"}
    return user  # Raw response
```

### 2. Error Handling

```python
from earnbase_common.responses import ErrorResponse
from earnbase_common.errors import AppError

class ErrorHandler:
    """Handle application errors."""
    
    @staticmethod
    def handle_error(error: Exception) -> ErrorResponse:
        """Convert exception to error response."""
        if isinstance(error, AppError):
            return ErrorResponse(
                error=error.message,
                code=error.code,
                details=error.details
            )
        
        if isinstance(error, ValidationError):
            return ErrorResponse(
                error="Validation error",
                code="VALIDATION_ERROR",
                errors=error.errors()
            )
            
        # Default error response
        return ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR"
        )
```

### 3. Pagination

```python
from earnbase_common.responses import PaginatedResponse
from typing import TypeVar, Generic, List

T = TypeVar("T")

class PaginatedList(Generic[T]):
    """Generic paginated list."""
    
    def __init__(
        self,
        items: List[T],
        total: int,
        page: int,
        per_page: int
    ):
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        
    def to_response(self) -> PaginatedResponse:
        """Convert to paginated response."""
        return PaginatedResponse(
            data=self.items,
            meta={
                "page": self.page,
                "per_page": self.per_page,
                "total": self.total,
                "total_pages": (self.total + self.per_page - 1) // self.per_page
            }
        )
```

## Future Features

### 1. Response Caching

```python
from earnbase_common.responses import CacheableResponse

class CacheableResponse(SuccessResponse):
    """Cacheable response with ETags."""
    
    def __init__(
        self,
        data: Any,
        cache_key: str,
        ttl: int = 3600
    ):
        super().__init__(data=data)
        self.cache_key = cache_key
        self.ttl = ttl
        
    async def get_etag(self) -> str:
        """Generate ETag for response."""
        pass
        
    async def is_modified(self, etag: str) -> bool:
        """Check if response is modified."""
        pass
```

### 2. Response Transformation

```python
from earnbase_common.responses import ResponseTransformer

class ResponseTransformer:
    """Transform response data."""
    
    async def transform_data(
        self,
        data: Any,
        fields: List[str]
    ) -> Any:
        """Transform response data."""
        pass
        
    async def filter_fields(
        self,
        data: Any,
        include: List[str]
    ) -> Any:
        """Filter response fields."""
        pass
        
    async def expand_relations(
        self,
        data: Any,
        expand: List[str]
    ) -> Any:
        """Expand related data."""
        pass
```

### 3. Response Versioning

```python
from earnbase_common.responses import VersionedResponse

class VersionedResponse(SuccessResponse):
    """Versioned response."""
    
    def __init__(
        self,
        data: Any,
        version: str
    ):
        super().__init__(data=data)
        self.version = version
        
    async def transform_version(
        self,
        target_version: str
    ) -> Any:
        """Transform data to target version."""
        pass
```

### 4. Response Compression

```python
from earnbase_common.responses import CompressedResponse

class CompressedResponse(SuccessResponse):
    """Compressed response."""
    
    async def compress_data(
        self,
        algorithm: str = "gzip"
    ) -> bytes:
        """Compress response data."""
        pass
        
    async def decompress_data(
        self,
        data: bytes
    ) -> Any:
        """Decompress response data."""
        pass
```

### 5. Response Metrics

```python
from earnbase_common.responses import MetricsResponse

class MetricsResponse(SuccessResponse):
    """Response with metrics."""
    
    def __init__(
        self,
        data: Any,
        track_metrics: bool = True
    ):
        super().__init__(data=data)
        self.track_metrics = track_metrics
        
    async def record_metrics(self) -> None:
        """Record response metrics."""
        pass
        
    async def get_response_time(self) -> float:
        """Get response time."""
        pass
``` 
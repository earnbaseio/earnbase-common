# Responses

## Overview

The responses module provides standardized response models for API endpoints using Pydantic. It includes base response types, success and error responses, pagination support, and custom JSON response handling.

## Features

### Base Response Models

All response models inherit from `BaseResponse`:

```python
from earnbase_common.responses import BaseResponse, SuccessResponse, ErrorResponse

# Base response with required fields
response = BaseResponse(
    success=True,
    message="Operation completed",
    code="SUCCESS"
)

# Success response with data
success = SuccessResponse(
    message="User created",
    data={"id": "123", "name": "John"},
    meta={"timestamp": "2024-01-12T00:00:00Z"}
)

# Error response with details
error = ErrorResponse(
    error="Validation failed",
    details={"field": "email", "message": "Invalid format"},
    errors=[
        {"field": "email", "message": "Invalid format"},
        {"field": "phone", "message": "Required field"}
    ]
)
```

### Pagination Support

Built-in support for paginated responses:

```python
from earnbase_common.responses import PaginatedResponse, PaginationMetadata

# Create pagination metadata
meta = PaginationMetadata(
    page=1,
    per_page=10,
    total=100,
    total_pages=10
)

# Create paginated response
response = PaginatedResponse(
    data=[{"id": "1", "name": "Item 1"}, {"id": "2", "name": "Item 2"}],
    meta=meta
)

# Response format:
{
    "data": [
        {"id": "1", "name": "Item 1"},
        {"id": "2", "name": "Item 2"}
    ],
    "meta": {
        "page": 1,
        "per_page": 10,
        "total": 100,
        "total_pages": 10
    }
}
```

### Custom JSON Response

FastAPI response class for consistent JSON formatting:

```python
from fastapi import FastAPI
from earnbase_common.responses import CustomJSONResponse

app = FastAPI()

# Use custom response class
@app.get("/users/{user_id}", response_class=CustomJSONResponse)
async def get_user(user_id: str):
    return {
        "id": user_id,
        "name": "John Doe"
    }

# Response will be wrapped:
{
    "data": {
        "id": "123",
        "name": "John Doe"
    }
}
```

## Key Features

### 1. Standardized Responses

- Consistent response structure
- Type validation with Pydantic
- Optional fields support
- Metadata handling

### 2. Error Handling

- Detailed error responses
- Multiple error support
- Error details and metadata
- Error code standardization

### 3. Pagination

- Built-in pagination metadata
- Configurable page size
- Total count tracking
- Page calculation

### 4. JSON Formatting

- Automatic response wrapping
- Consistent data structure
- Error response handling
- Custom serialization

## Best Practices

1. **Response Structure**:
   - Use appropriate response types
   - Include meaningful messages
   - Add relevant metadata
   - Follow consistent patterns

2. **Error Handling**:
   - Provide clear error messages
   - Include error details
   - Use standard error codes
   - Handle multiple errors

3. **Pagination**:
   - Set reasonable page sizes
   - Include total counts
   - Handle empty results
   - Validate page numbers

4. **Performance**:
   - Minimize response size
   - Use appropriate serialization
   - Cache when possible
   - Handle large datasets

## Examples

### 1. API Endpoint

```python
from fastapi import FastAPI, HTTPException
from earnbase_common.responses import (
    SuccessResponse,
    ErrorResponse,
    CustomJSONResponse
)

app = FastAPI()

@app.get(
    "/users/{user_id}",
    response_model=SuccessResponse,
    response_class=CustomJSONResponse
)
async def get_user(user_id: str):
    try:
        user = await fetch_user(user_id)
        return SuccessResponse(
            message="User retrieved successfully",
            data=user,
            meta={"cached": False}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error="User not found",
                details={"user_id": user_id}
            ).dict()
        )
```

### 2. List Endpoint

```python
from fastapi import FastAPI, Query
from earnbase_common.responses import (
    PaginatedResponse,
    PaginationMetadata,
    CustomJSONResponse
)

app = FastAPI()

@app.get(
    "/users",
    response_model=PaginatedResponse,
    response_class=CustomJSONResponse
)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    # Get total count
    total = await count_users()
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Get data
    users = await fetch_users(
        offset=offset,
        limit=per_page
    )
    
    # Create response
    return PaginatedResponse(
        data=users,
        meta=PaginationMetadata(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages
        )
    )
```

### 3. Error Handling

```python
from fastapi import FastAPI, HTTPException
from earnbase_common.responses import ErrorResponse
from typing import List

app = FastAPI()

@app.post("/users")
async def create_user(user: dict):
    errors: List[dict] = []
    
    # Validate email
    if not is_valid_email(user.get("email")):
        errors.append({
            "field": "email",
            "message": "Invalid email format"
        })
    
    # Validate password
    if not is_valid_password(user.get("password")):
        errors.append({
            "field": "password",
            "message": "Password too weak"
        })
    
    # Return validation errors
    if errors:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Validation failed",
                errors=errors
            ).dict()
        )
    
    # Create user
    try:
        new_user = await create_user_in_db(user)
        return SuccessResponse(
            message="User created successfully",
            data=new_user
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to create user",
                details={"message": str(e)}
            ).dict()
        )
``` 
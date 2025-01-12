# Errors

## Overview

The errors module provides a comprehensive error handling system for REST APIs built with FastAPI. It includes standardized error classes, error handlers, and consistent error response formats.

## Features

### Error Classes

The module defines a hierarchy of error classes:

```python
from earnbase_common.errors import (
    APIError,  # Base class
    AuthenticationError,  # 401 Unauthorized
    AuthorizationError,  # 403 Forbidden
    ValidationError,  # 400 Bad Request
    NotFoundError,  # 404 Not Found
    ConflictError,  # 409 Conflict
    InternalError,  # 500 Internal Server Error
)

# Basic usage
raise NotFoundError(
    message="User not found",
    code="USER_NOT_FOUND",
    details={"user_id": "123"}
)
```

### Error Handlers

Built-in error handlers for FastAPI:

```python
from earnbase_common.errors import register_error_handlers
from fastapi import FastAPI

app = FastAPI()

# Register all error handlers
register_error_handlers(app)
```

## Error Response Format

All errors follow a consistent JSON format:

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {
            // Optional error details
        }
    }
}
```

## Error Types

### 1. Authentication Error (401)

Used for authentication failures:

```python
raise AuthenticationError(
    message="Invalid credentials",
    code="INVALID_CREDENTIALS",
    details={"reason": "expired_token"}
)
```

### 2. Authorization Error (403)

Used for permission issues:

```python
raise AuthorizationError(
    message="Permission denied",
    code="INSUFFICIENT_PERMISSIONS",
    details={"required_role": "admin"}
)
```

### 3. Validation Error (400)

Used for input validation failures:

```python
raise ValidationError(
    message="Invalid input",
    code="INVALID_INPUT",
    details={
        "fields": [
            {
                "field": "email",
                "message": "Invalid email format",
                "type": "value_error.email"
            }
        ]
    }
)
```

### 4. Not Found Error (404)

Used when resources are not found:

```python
raise NotFoundError(
    message="Resource not found",
    code="RESOURCE_NOT_FOUND",
    details={"resource_type": "user", "id": "123"}
)
```

### 5. Conflict Error (409)

Used for resource conflicts:

```python
raise ConflictError(
    message="User already exists",
    code="USER_EXISTS",
    details={"email": "user@example.com"}
)
```

### 6. Internal Error (500)

Used for unexpected server errors:

```python
raise InternalError(
    message="Database connection failed",
    code="DB_CONNECTION_ERROR",
    details={"db_host": "localhost"}
)
```

## Error Handling

### 1. Basic Error Handling

```python
from fastapi import FastAPI
from earnbase_common.errors import NotFoundError, register_error_handlers

app = FastAPI()
register_error_handlers(app)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await find_user(user_id)
    if not user:
        raise NotFoundError(
            message="User not found",
            code="USER_NOT_FOUND",
            details={"user_id": user_id}
        )
    return user
```

### 2. Validation Error Handling

The module automatically handles Pydantic validation errors:

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    name: str

@app.post("/users")
async def create_user(user: UserCreate):
    # Pydantic validation errors are automatically handled
    # and converted to ValidationError responses
    return await create_user_in_db(user)
```

### 3. Custom Error Handling

You can add custom error handlers:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(CustomError)
async def custom_error_handler(request: Request, exc: CustomError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )
```

## Best Practices

1. **Use Specific Error Types**:
   - Choose the most specific error class for each case
   - Include relevant details in the error response
   - Use consistent error codes within your application

2. **Error Logging**:
   - All errors are automatically logged with details
   - Include request_id in logs for tracing
   - Log additional context when needed

3. **Error Codes**:
   - Use UPPERCASE_WITH_UNDERSCORES format
   - Make codes descriptive and specific
   - Document all error codes used in your API

4. **Error Messages**:
   - Write clear, human-readable messages
   - Include actionable information when possible
   - Keep messages concise but informative

5. **Security Considerations**:
   - Don't expose sensitive information in error details
   - Use appropriate status codes for security-related errors
   - Log security-related errors appropriately
``` 
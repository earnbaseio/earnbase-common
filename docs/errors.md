# Errors

## Overview

The errors module provides a standardized way to handle errors across the application. It includes a hierarchy of error types, error handlers, and utilities for consistent error responses.

## Features

### Error Types

```python
from earnbase_common.errors import (
    APIError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    InternalError
)

# Base API Error
raise APIError(
    message="Something went wrong",
    code="ERROR",
    status_code=500,
    details={"key": "value"}
)

# Validation Error
raise ValidationError(
    message="Invalid input",
    details={"field": "email", "error": "invalid format"}
)

# Authentication Error
raise AuthenticationError(
    message="Invalid credentials",
    details={"reason": "expired token"}
)

# Authorization Error
raise AuthorizationError(
    message="Permission denied",
    details={"required_role": "admin"}
)

# Not Found Error
raise NotFoundError(
    message="User not found",
    details={"user_id": "123"}
)

# Conflict Error
raise ConflictError(
    message="Email already exists",
    details={"email": "user@example.com"}
)

# Internal Error
raise InternalError(
    message="Database connection failed",
    details={"service": "mongodb"}
)
```

### Error Handlers

```python
from earnbase_common.errors import register_error_handlers
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Register all error handlers
app = FastAPI()
register_error_handlers(app)

# Custom error handler
@app.exception_handler(CustomError)
async def custom_error_handler(
    request: Request,
    exc: CustomError
) -> JSONResponse:
    """Handle custom errors."""
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

### Error Response Format

```python
from earnbase_common.errors import create_error_response
from typing import Dict, Any

def create_api_error_response(
    error: Exception
) -> Dict[str, Any]:
    """Create API error response."""
    if isinstance(error, APIError):
        return create_error_response(
            status_code=error.status_code,
            message=error.message,
            code=error.code,
            details=error.details
        )
    
    # Default internal error
    return create_error_response(
        status_code=500,
        message="Internal server error",
        code="INTERNAL_ERROR"
    )

# Example response format
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "fields": [
                {
                    "field": "email",
                    "message": "Invalid email format",
                    "type": "value_error"
                }
            ]
        }
    }
}
```

## Best Practices

### 1. Error Hierarchy

```python
from earnbase_common.errors import APIError
from typing import Dict, Any, Optional

class DomainError(APIError):
    """Base class for domain errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize domain error."""
        super().__init__(
            message=message,
            code=code,
            status_code=400,
            details=details
        )

class UserError(DomainError):
    """User domain errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "USER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize user error."""
        super().__init__(
            message=message,
            code=code,
            details=details
        )

# Usage
class InvalidUserStateError(UserError):
    """Invalid user state error."""
    
    def __init__(
        self,
        user_id: str,
        current_state: str,
        target_state: str
    ):
        """Initialize error."""
        super().__init__(
            message=f"Invalid state transition",
            code="INVALID_USER_STATE",
            details={
                "user_id": user_id,
                "current_state": current_state,
                "target_state": target_state
            }
        )
```

### 2. Error Handling

```python
from earnbase_common.errors import (
    NotFoundError,
    ValidationError,
    InternalError
)
from earnbase_common.logging import get_logger

logger = get_logger(__name__)

class UserService:
    """User service with error handling."""
    
    async def get_user(self, user_id: str) -> User:
        """Get user by ID."""
        try:
            user = await self.repository.find_one({"_id": user_id})
            if not user:
                raise NotFoundError(
                    message="User not found",
                    details={"user_id": user_id}
                )
            return user
            
        except DatabaseError as e:
            logger.error(
                "database_error",
                operation="get_user",
                user_id=user_id,
                error=str(e)
            )
            raise InternalError(
                message="Failed to get user",
                details={"user_id": user_id}
            )
    
    async def create_user(self, data: Dict[str, Any]) -> User:
        """Create new user."""
        try:
            # Validate unique email
            existing = await self.repository.find_one({
                "email": data["email"]
            })
            if existing:
                raise ValidationError(
                    message="Email already exists",
                    details={"email": data["email"]}
                )
            
            return await self.repository.create(data)
            
        except ValidationError:
            raise
            
        except Exception as e:
            logger.error(
                "create_user_failed",
                data=data,
                error=str(e)
            )
            raise InternalError(
                message="Failed to create user"
            )
```

### 3. Error Logging

```python
from earnbase_common.errors import APIError
from earnbase_common.logging import get_logger
from typing import Optional

logger = get_logger(__name__)

class ErrorLogger:
    """Error logger with context."""
    
    def __init__(self, request: Request):
        """Initialize logger."""
        self.request = request
        self.logger = logger
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error with context."""
        error_data = {
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "request_id": self.request.state.request_id,
            "path": self.request.url.path,
            "method": self.request.method
        }
        
        if isinstance(error, APIError):
            error_data.update({
                "error_code": error.code,
                "error_details": error.details
            })
        
        if context:
            error_data.update(context)
        
        self.logger.error("request_error", **error_data)

# Usage
error_logger = ErrorLogger(request)
try:
    result = await process_request()
except Exception as e:
    error_logger.log_error(e, {"user_id": "123"})
    raise
```

## Future Features

The following features are planned for future releases:

### 1. Error Recovery

```python
class ErrorRecovery:
    """Error recovery strategies."""
    
    async def retry_with_backoff(
        self,
        operation: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Any:
        """Retry operation with exponential backoff."""
        pass
    
    async def circuit_breaker(
        self,
        operation: Callable,
        failure_threshold: int = 5,
        reset_timeout: int = 60
    ) -> Any:
        """Circuit breaker pattern."""
        pass
    
    async def fallback_strategy(
        self,
        operation: Callable,
        fallback: Callable
    ) -> Any:
        """Fallback on failure."""
        pass
```

### 2. Error Aggregation

```python
class ErrorAggregator:
    """Aggregate and analyze errors."""
    
    async def collect_errors(
        self,
        time_window: int
    ) -> List[Dict[str, Any]]:
        """Collect errors in time window."""
        pass
    
    async def analyze_trends(
        self,
        error_type: str
    ) -> Dict[str, Any]:
        """Analyze error trends."""
        pass
    
    async def generate_report(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Report:
        """Generate error report."""
        pass
```

### 3. Error Correlation

```python
class ErrorCorrelation:
    """Correlate errors across services."""
    
    async def trace_error(
        self,
        error_id: str
    ) -> List[Dict[str, Any]]:
        """Trace error across services."""
        pass
    
    async def find_related_errors(
        self,
        error: APIError
    ) -> List[APIError]:
        """Find related errors."""
        pass
    
    async def build_error_chain(
        self,
        root_error: APIError
    ) -> ErrorChain:
        """Build chain of related errors."""
        pass
```

### 4. Smart Error Messages

```python
class SmartErrorMessage:
    """Generate smart error messages."""
    
    def translate_error(
        self,
        error: APIError,
        language: str
    ) -> str:
        """Translate error message."""
        pass
    
    def suggest_solution(
        self,
        error: APIError
    ) -> str:
        """Suggest solution for error."""
        pass
    
    def format_for_user(
        self,
        error: APIError,
        user_type: str
    ) -> str:
        """Format error for user type."""
        pass
```

### 5. Error Metrics

```python
class ErrorMetrics:
    """Collect error metrics."""
    
    async def track_error_rate(
        self,
        error_type: str,
        window: int = 60
    ) -> float:
        """Track error rate."""
        pass
    
    async def measure_impact(
        self,
        error: APIError
    ) -> Dict[str, Any]:
        """Measure error impact."""
        pass
    
    async def alert_threshold(
        self,
        metric: str,
        threshold: float
    ) -> None:
        """Set alert threshold."""
        pass
``` 
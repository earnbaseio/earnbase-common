# Logging

## Overview

The logging module provides structured logging using `structlog` with support for multiple output formats (JSON, console), log rotation, and sensitive data filtering. It includes configuration for both development and production environments.

## Features

### Structured Logging

Basic usage with structured logging:

```python
from earnbase_common.logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("User logged in", user_id="123")
logger.error("Operation failed", error="Connection timeout")

# With context
logger.info(
    "Processing request",
    request_id="req-123",
    method="POST",
    path="/users"
)
```

### Configuration

Configure logging for your service:

```python
from earnbase_common.logging import setup_logging

# Setup logging
setup_logging(
    service_name="my-service",
    log_file="/var/log/my-service/app.log",
    log_level="INFO",
    debug=False  # True for development
)
```

## Key Features

### 1. Multiple Output Formats

Support for both JSON and console output:

```python
# Production (JSON format)
{
    "timestamp": "2024-01-11T12:34:56.789Z",
    "level": "info",
    "event": "User logged in",
    "logger": "my_service.auth",
    "user_id": "123",
    "service": "my-service"
}

# Development (colored console output)
[12:34:56] INFO     User logged in                    user_id=123 service=my-service
```

### 2. Log Rotation

Automatic log rotation with size limits:

```python
# Configuration
{
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    }
}
```

### 3. Sensitive Data Filtering

Automatic filtering of sensitive information:

```python
# Before filtering
logger.info(
    "User authenticated",
    token="secret-token-123",
    user_data={"password": "123456"}
)

# After filtering
{
    "event": "User authenticated",
    "token": "***FILTERED***",
    "user_data": {
        "password": "***FILTERED***"
    }
}
```

### 4. Service Information

Automatic addition of service context:

```python
logger.info("Service started")

# Output includes service info
{
    "event": "Service started",
    "service": "my-service",
    "environment": "production"
}
```

## Best Practices

1. **Structured Data**:
   - Use key-value pairs for context
   - Keep keys consistent across logs
   - Use meaningful event names

2. **Log Levels**:
   - DEBUG: Detailed debugging information
   - INFO: General operational events
   - WARNING: Warning messages for potential issues
   - ERROR: Error events that might still allow the application to continue
   - CRITICAL: Critical events that may lead to application failure

3. **Context**:
   - Include request_id for tracing
   - Add user_id when available
   - Include relevant business context

4. **Security**:
   - Never log sensitive data
   - Use sensitive data filtering
   - Be careful with error details in production

## Examples

### 1. Request Logging

```python
from earnbase_common.logging import get_logger
from typing import Optional

logger = get_logger(__name__)

async def process_request(
    request_id: str,
    user_id: Optional[str] = None
):
    """Process request with logging."""
    logger.info(
        "Processing request",
        request_id=request_id,
        user_id=user_id,
        method="POST",
        path="/api/v1/users"
    )
    
    try:
        # Process request
        result = await do_something()
        
        logger.info(
            "Request completed",
            request_id=request_id,
            duration_ms=1000
        )
        return result
        
    except Exception as e:
        logger.error(
            "Request failed",
            request_id=request_id,
            error=str(e),
            exc_info=True
        )
        raise
```

### 2. Business Logic Logging

```python
class UserService:
    """User service with logging."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = get_logger(__name__)
    
    async def create_user(
        self,
        email: str,
        name: str
    ):
        """Create user with logging."""
        self.logger.info(
            "Creating user",
            email=email,
            name=name
        )
        
        try:
            user = await self.repository.create({
                "email": email,
                "name": name
            })
            
            self.logger.info(
                "User created",
                user_id=str(user.id),
                email=email
            )
            return user
            
        except Exception as e:
            self.logger.error(
                "Failed to create user",
                email=email,
                error=str(e)
            )
            raise
```

### 3. Background Task Logging

```python
class DataProcessor:
    """Background data processor with logging."""
    
    def __init__(self):
        """Initialize processor."""
        self.logger = get_logger(__name__)
    
    async def process_batch(
        self,
        batch_id: str,
        items: list
    ):
        """Process data batch with logging."""
        self.logger.info(
            "Starting batch processing",
            batch_id=batch_id,
            items_count=len(items)
        )
        
        processed = 0
        errors = 0
        
        for item in items:
            try:
                await self.process_item(item)
                processed += 1
                
                if processed % 100 == 0:
                    self.logger.info(
                        "Batch progress",
                        batch_id=batch_id,
                        processed=processed,
                        total=len(items)
                    )
                    
            except Exception as e:
                errors += 1
                self.logger.error(
                    "Item processing failed",
                    batch_id=batch_id,
                    item_id=item.id,
                    error=str(e)
                )
        
        self.logger.info(
            "Batch processing completed",
            batch_id=batch_id,
            processed=processed,
            errors=errors
        )
``` 
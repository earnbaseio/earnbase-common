# Logging

## Overview

The logging module provides structured logging capabilities using `structlog` with features like:
- JSON formatting
- Log rotation
- Sensitive data filtering
- Service information enrichment
- Multiple output handlers (console, file, error file)

## Features

### Basic Usage

```python
from earnbase_common.logging import get_logger, setup_logging

# Setup logging for your service
setup_logging(
    service_name="my-service",
    log_file="/var/log/my-service/app.log",
    log_level="INFO",
    debug=False
)

# Get a logger instance
logger = get_logger(__name__)

# Log messages with context
logger.info(
    "user_created",
    user_id="123",
    email="user@example.com"
)

# Log errors with stack traces
try:
    raise ValueError("Something went wrong")
except Exception as e:
    logger.error(
        "operation_failed",
        error=str(e),
        operation="create_user"
    )
```

### Structured Output

JSON format (production):
```json
{
    "timestamp": "2024-01-11T10:30:45.123Z",
    "level": "info",
    "event": "user_created",
    "logger": "my_service.users",
    "user_id": "123",
    "email": "user@example.com",
    "service": "my-service"
}
```

Console format (debug):
```
2024-01-11 10:30:45 [INFO] my_service.users: user_created
    user_id=123
    email=user@example.com
    service=my-service
```

### Log Configuration

```python
from earnbase_common.logging import setup_logging

# Basic setup
setup_logging(
    service_name="my-service",
    log_file="/var/log/my-service/app.log"
)

# Advanced setup
setup_logging(
    service_name="my-service",
    log_file="/var/log/my-service/app.log",
    log_level="DEBUG",  # More verbose logging
    debug=True  # Colored console output
)
```

### Custom Processors

```python
from earnbase_common.logging.processors import (
    add_service_info,
    filter_sensitive_data
)

# Service info processor
def custom_service_info(logger, name, event_dict):
    """Add custom service information."""
    event_dict["environment"] = "production"
    event_dict["version"] = "1.0.0"
    return event_dict

# Sensitive data filtering
def custom_filter(logger, name, event_dict):
    """Filter additional sensitive fields."""
    if "credit_card" in event_dict:
        event_dict["credit_card"] = "***FILTERED***"
    return event_dict
```

## Best Practices

### 1. Structured Events

```python
# Good - structured event with context
logger.info(
    "payment_processed",
    payment_id="123",
    amount=99.99,
    currency="USD"
)

# Bad - unstructured string message
logger.info(
    "Payment 123 processed for $99.99 USD"
)
```

### 2. Error Handling

```python
try:
    result = process_payment(payment_id)
except PaymentError as e:
    logger.error(
        "payment_failed",
        error=str(e),
        payment_id=payment_id,
        error_code=e.code
    )
    raise
except Exception as e:
    logger.exception(
        "unexpected_error",
        operation="process_payment",
        payment_id=payment_id
    )
    raise
```

### 3. Performance Logging

```python
import time

def log_duration(logger, operation):
    """Log operation duration."""
    start = time.time()
    yield
    duration = time.time() - start
    logger.info(
        "operation_completed",
        operation=operation,
        duration_ms=int(duration * 1000)
    )

# Usage
async def process_batch(items):
    async with log_duration(logger, "batch_processing"):
        for item in items:
            await process_item(item)
```

## Future Features

### 1. Log Aggregation

```python
class LogAggregator:
    """Aggregate logs across services."""
    
    async def collect_logs(
        self,
        services: List[str],
        time_range: Tuple[datetime, datetime]
    ) -> List[Dict[str, Any]]:
        """Collect logs from multiple services."""
        pass
    
    async def search_logs(
        self,
        query: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search logs with query and filters."""
        pass
```

### 2. Metrics Integration

```python
class LogMetrics:
    """Extract metrics from logs."""
    
    async def count_events(
        self,
        event_type: str,
        time_window: int
    ) -> int:
        """Count events in time window."""
        pass
    
    async def calculate_stats(
        self,
        metric: str,
        group_by: str
    ) -> Dict[str, float]:
        """Calculate statistics from logs."""
        pass
```

### 3. Log Analysis

```python
class LogAnalyzer:
    """Analyze logs for patterns."""
    
    async def detect_anomalies(
        self,
        baseline: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in logs."""
        pass
    
    async def generate_insights(
        self,
        time_range: Tuple[datetime, datetime]
    ) -> List[Dict[str, Any]]:
        """Generate insights from logs."""
        pass
```

### 4. Custom Formatters

```python
class LogFormatter:
    """Custom log formatters."""
    
    def format_for_elk(
        self,
        event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format for ELK stack."""
        pass
    
    def format_for_datadog(
        self,
        event_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format for Datadog."""
        pass
```

### 5. Log Retention

```python
class LogRetention:
    """Manage log retention."""
    
    async def archive_logs(
        self,
        older_than: datetime
    ) -> None:
        """Archive old logs."""
        pass
    
    async def cleanup_logs(
        self,
        retention_days: int
    ) -> None:
        """Clean up old logs."""
        pass
``` 
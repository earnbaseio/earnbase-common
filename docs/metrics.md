# Metrics

## Overview

The metrics module provides standardized metrics collection using Prometheus with features like:
- Multiple metric types (Counter, Gauge, Histogram, Summary)
- Automatic metric name formatting
- Decorator-based metrics collection
- Pre-configured metrics for HTTP, Database, and Service monitoring

## Features

### Basic Usage

```python
from earnbase_common.metrics import (
    counter,
    histogram,
    gauge,
    summary,
    metrics_decorator
)

# Counter metric
request_counter = counter(
    "http_requests_total",
    labels={"method": "GET", "endpoint": "/users"}
)
request_counter.inc()

# Histogram metric
latency_histogram = histogram(
    "request_duration_seconds",
    label_names=["method", "endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)
with latency_histogram.time():
    process_request()

# Gauge metric
active_users = gauge(
    "active_users_total",
    labels={"status": "online"}
)
active_users.set(42)

# Summary metric
response_size = summary(
    "response_size_bytes",
    labels={"content_type": "application/json"}
)
response_size.observe(1024)
```

### Decorator Usage

```python
from earnbase_common.metrics import metrics_decorator

# Count function calls
@metrics_decorator.counter(
    "function_calls_total",
    labels={"function": "process_user"}
)
def process_user(user_id: str):
    # Process user
    pass

# Measure function duration
@metrics_decorator.histogram(
    "function_duration_seconds",
    label_names=["function", "status"]
)
async def process_payment(payment_id: str):
    # Process payment
    pass
```

### Built-in Metrics

```python
from earnbase_common.metrics.metrics import metrics

# HTTP metrics
metrics.request_count.labels(
    method="POST",
    endpoint="/users",
    status=201
).inc()

with metrics.request_latency.labels(
    method="GET",
    endpoint="/users"
).time():
    # Handle request
    pass

# Database metrics
metrics.db_operation_count.labels(
    operation="insert",
    collection="users"
).inc()

with metrics.db_operation_latency.labels(
    operation="find",
    collection="orders"
).time():
    # Database operation
    pass

# Service metrics
metrics.service_info.labels(
    version="1.0.0",
    environment="production"
).set(1)

metrics.service_uptime.set(3600)  # 1 hour
```

## Best Practices

### 1. Metric Naming

```python
# Good - clear and descriptive names
counter("http_requests_total")
histogram("request_duration_seconds")
gauge("active_connections")

# Bad - unclear or inconsistent names
counter("requests")  # Too vague
histogram("time")   # Too generic
gauge("conn_num")   # Unclear abbreviation
```

### 2. Label Usage

```python
# Good - relevant and specific labels
counter(
    "http_requests_total",
    labels={
        "method": "GET",
        "path": "/api/v1/users",
        "status": "200"
    }
)

# Bad - too many or irrelevant labels
counter(
    "http_requests_total",
    labels={
        "method": "GET",
        "path": "/api/v1/users",
        "status": "200",
        "user_agent": "...",  # Too specific
        "timestamp": "...",   # Use time series instead
        "request_id": "..."   # Too high cardinality
    }
)
```

### 3. Performance Monitoring

```python
# Track operation duration
with metrics.operation_latency.time():
    result = await process_operation()

# Track resource usage
metrics.memory_usage.set(
    get_memory_usage()
)

# Track error rates
try:
    await process_request()
except Exception as e:
    metrics.error_count.labels(
        type=type(e).__name__
    ).inc()
    raise
```

## Future Features

### 1. Metric Aggregation

```python
class MetricAggregator:
    """Aggregate metrics across services."""
    
    async def collect_metrics(
        self,
        services: List[str]
    ) -> Dict[str, Any]:
        """Collect metrics from multiple services."""
        pass
    
    async def aggregate_by_label(
        self,
        metric_name: str,
        label: str
    ) -> Dict[str, float]:
        """Aggregate metric by label."""
        pass
```

### 2. Alert Rules

```python
class MetricAlerts:
    """Define and manage metric alerts."""
    
    def add_threshold_alert(
        self,
        metric: str,
        threshold: float,
        duration: str = "5m"
    ) -> None:
        """Add threshold-based alert."""
        pass
    
    def add_trend_alert(
        self,
        metric: str,
        change_percent: float,
        window: str = "1h"
    ) -> None:
        """Add trend-based alert."""
        pass
```

### 3. Custom Exporters

```python
class MetricExporter:
    """Export metrics to various systems."""
    
    async def export_to_datadog(
        self,
        api_key: str
    ) -> None:
        """Export to Datadog."""
        pass
    
    async def export_to_cloudwatch(
        self,
        namespace: str
    ) -> None:
        """Export to CloudWatch."""
        pass
```

### 4. Metric Analysis

```python
class MetricAnalyzer:
    """Analyze metrics for patterns."""
    
    async def detect_anomalies(
        self,
        metric: str,
        window: str = "1h"
    ) -> List[Dict[str, Any]]:
        """Detect metric anomalies."""
        pass
    
    async def forecast_values(
        self,
        metric: str,
        horizon: str = "1d"
    ) -> List[Dict[str, Any]]:
        """Forecast metric values."""
        pass
```

### 5. Custom Collectors

```python
class CustomCollector:
    """Collect custom application metrics."""
    
    def collect_runtime_metrics(self) -> None:
        """Collect Python runtime metrics."""
        pass
    
    def collect_system_metrics(self) -> None:
        """Collect system metrics."""
        pass
    
    def collect_business_metrics(self) -> None:
        """Collect business-specific metrics."""
        pass
``` 
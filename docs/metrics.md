# Metrics

## Overview

The metrics module provides standardized metrics collection using Prometheus client library. It includes support for different metric types (Counter, Histogram, Gauge, Summary) and automatic metrics collection for database operations and HTTP requests.

## Features

### Basic Usage

```python
from earnbase_common.metrics import metrics

# Counter metric
request_counter = metrics.counter(
    "http_requests_total",
    labelnames=["method", "path"]
)
request_counter.labels(method="GET", path="/users").inc()

# Histogram metric
request_duration = metrics.histogram(
    "http_request_duration_seconds",
    label_names=["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)
with request_duration.labels(method="GET", path="/users").time():
    # Process request
    pass
```

### Metric Types

#### 1. Counter

Used for cumulative values that only increase:

```python
# Track total requests
requests = metrics.counter(
    "requests_total",
    labelnames=["status"]
)

# Increment counter
requests.labels(status="success").inc()
requests.labels(status="error").inc()
```

#### 2. Histogram

Used for measuring distributions of values:

```python
# Track request duration
latency = metrics.histogram(
    "request_duration_seconds",
    label_names=["endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# Measure duration
with latency.labels(endpoint="/api/users").time():
    # Process request
    pass
```

#### 3. Gauge

Used for values that can go up and down:

```python
# Track active connections
connections = metrics.gauge(
    "active_connections",
    labelnames=["type"]
)

# Update gauge
connections.labels(type="websocket").inc()  # Connection opened
connections.labels(type="websocket").dec()  # Connection closed
```

#### 4. Summary

Used for calculating quantiles over time:

```python
# Track response size
response_size = metrics.summary(
    "response_size_bytes",
    labelnames=["content_type"]
)

# Observe value
response_size.labels(content_type="application/json").observe(1234)
```

## Built-in Metrics

### 1. Database Metrics

```python
from earnbase_common.metrics import (
    db_operation_latency,
    db_operation_count
)

# Track database operations
with db_operation_latency.labels(
    operation="find",
    collection="users"
).time():
    await collection.find_one({"id": "123"})

db_operation_count.labels(
    operation="find",
    collection="users"
).inc()
```

### 2. HTTP Metrics

```python
from earnbase_common.metrics import (
    http_request_latency,
    http_request_count,
    http_request_in_progress
)

# Track HTTP requests
with http_request_latency.labels(
    method="GET",
    path="/api/users",
    status=200
).time():
    # Handle request
    pass

http_request_count.labels(
    method="GET",
    path="/api/users",
    status=200
).inc()
```

### 3. Service Metrics

```python
from earnbase_common.metrics import (
    service_info,
    service_uptime
)

# Set service information
service_info.labels(
    version="1.0.0",
    environment="production"
).set(1)

# Update uptime
service_uptime.set(3600)  # 1 hour
```

## Decorators

### 1. Counter Decorator

```python
from earnbase_common.metrics import MetricsDecorator

metrics_decorator = MetricsDecorator(metrics)

@metrics_decorator.counter(
    "function_calls_total",
    labelnames=["function"]
)
async def process_data():
    # Function is automatically counted
    pass
```

### 2. Histogram Decorator

```python
@metrics_decorator.histogram(
    "function_duration_seconds",
    label_names=["function"],
    buckets=(0.1, 0.5, 1.0)
)
async def process_request():
    # Duration is automatically measured
    pass
```

## Best Practices

1. **Naming Conventions**:
   - Use snake_case for metric names
   - Add units to metric names (e.g. _seconds, _bytes)
   - Use descriptive label names
   - Keep cardinality under control

2. **Label Usage**:
   - Use labels for dimensions that matter
   - Avoid high cardinality labels
   - Keep label values stable
   - Use meaningful label names

3. **Metric Types**:
   - Use Counter for events and totals
   - Use Histogram for durations and sizes
   - Use Gauge for current values
   - Use Summary for quantiles

4. **Performance**:
   - Reuse metric objects
   - Be careful with high-cardinality labels
   - Use appropriate bucket sizes
   - Monitor memory usage

## Examples

### 1. API Endpoint Monitoring

```python
from fastapi import FastAPI
from earnbase_common.metrics import (
    http_request_latency,
    http_request_count
)

app = FastAPI()

@app.middleware("http")
async def metrics_middleware(request, call_next):
    # Track request
    with http_request_latency.labels(
        method=request.method,
        path=request.url.path,
        status=200
    ).time():
        response = await call_next(request)
        
    http_request_count.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()
    
    return response
```

### 2. Database Operation Monitoring

```python
class MetricsRepository:
    """Repository with metrics collection."""
    
    def __init__(self, collection, metrics):
        self.collection = collection
        self.metrics = metrics
    
    async def find_one(self, query):
        with self.metrics.db_operation_latency.labels(
            operation="find_one",
            collection=self.collection.name
        ).time():
            result = await self.collection.find_one(query)
            
        self.metrics.db_operation_count.labels(
            operation="find_one",
            collection=self.collection.name
        ).inc()
        
        return result
```

### 3. Background Task Monitoring

```python
class TaskProcessor:
    """Background task processor with metrics."""
    
    def __init__(self):
        self.task_duration = metrics.histogram(
            "task_processing_seconds",
            label_names=["task_type"],
            buckets=(1, 5, 10, 30, 60)
        )
        self.task_count = metrics.counter(
            "tasks_processed_total",
            labelnames=["task_type", "status"]
        )
    
    async def process_task(self, task):
        with self.task_duration.labels(
            task_type=task.type
        ).time():
            try:
                result = await self._process(task)
                self.task_count.labels(
                    task_type=task.type,
                    status="success"
                ).inc()
                return result
            except Exception:
                self.task_count.labels(
                    task_type=task.type,
                    status="error"
                ).inc()
                raise
```
``` 
# Earnbase Common

Core library for Earnbase Platform services.

## Overview

Earnbase Common provides shared components, utilities, and standards for building microservices in the Earnbase Platform. It implements common patterns and best practices to ensure consistency across services.

## Features

### Domain Models

Base classes for domain-driven design:

- **BaseModel**: Enhanced Pydantic model with common functionality
```python
from earnbase_common.models import BaseModel
from datetime import datetime
from typing import Optional

class User(BaseModel):
    name: str
    email: str
    created_at: datetime
    status: Optional[str] = None

# Models are immutable by default
user = User(
    name="John",
    email="john@example.com",
    created_at=datetime.utcnow()
)
```

- **Entity**: Base class for domain entities
```python
from earnbase_common.models import Entity
from typing import Optional

class Product(Entity):
    name: str
    price: float
    description: Optional[str] = None

product = Product(name="Phone", price=999.99)
print(str(product))  # Product(id=123e4567-e89b-12d3-a456-426614174000)
```

- **AggregateRoot**: Base class for aggregate roots with event management
```python
from earnbase_common.models import AggregateRoot, DomainEvent

class OrderCreated(DomainEvent):
    order_id: str
    total_amount: float

class Order(AggregateRoot):
    customer_id: str
    total: float
    status: str = "pending"

    def place(self) -> None:
        """Place the order."""
        self.status = "placed"
        
        # Add domain event
        self.add_event(
            OrderCreated(
                event_type="OrderCreated",
                aggregate_id=str(self.id),
                aggregate_type="Order",
                order_id=str(self.id),
                total_amount=self.total
            )
        )
        
        # Update version
        self.increment_version()

# Create and place order
order = Order(customer_id="123", total=100.0)
order.place()

# Access events and version
print(order.events)  # [OrderCreated(...)]
print(order.version)  # 2
```

Key features:
- Immutable models with Pydantic validation
- Event sourcing with domain events
- Automatic versioning and timestamps
- UUID generation for entities
- Type safety and validation

For detailed documentation, see [Models](docs/models.md).

### Security

Comprehensive security utilities:

```python
from earnbase_common.security import (
    JWTConfig,
    TokenManager,
    PasswordHasher,
    SecurityPolicy
)

# JWT token management
config = JWTConfig(secret_key="your-secret-key")
manager = TokenManager(config)

# Create tokens
access_token = manager.create_token(
    data={"user_id": "123"},
    token_type="access"
)

# Password management
hasher = PasswordHasher()
hash_value = await hasher.hash("StrongP@ssw0rd")
is_valid = await hasher.verify("StrongP@ssw0rd", hash_value.value)

# Security policies
policy = SecurityPolicy()
min_length = policy.PASSWORD_MIN_LENGTH  # 8
max_attempts = policy.MAX_LOGIN_ATTEMPTS  # 5
token_expire = policy.ACCESS_TOKEN_EXPIRE_MINUTES  # 30
```

Key features:
- JWT token creation and verification
- Password hashing with policy validation
- Security policy configuration
- Session management
- Account lockout protection
- Token expiration control

For detailed documentation, see [Security](docs/security.md).

### Value Objects

Immutable value objects for common domain concepts:

```python
from earnbase_common.value_objects import (
    Email,
    PhoneNumber,
    Money,
    Address
)
from decimal import Decimal

# Email validation
email = Email(value="user@example.com")
print(str(email))  # user@example.com

# Phone number with country code
phone = PhoneNumber(
    value="1234567890",
    country_code="84"
)
print(str(phone))  # +841234567890

# Money with currency
price = Money(amount=Decimal("99.99"), currency="USD")
discount = Money(amount=Decimal("10.00"), currency="USD")
final = price - discount
print(str(final))  # 89.99 USD

# Address with optional unit
address = Address(
    street="123 Main St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105",
    unit="4B"
)
print(str(address))
# Unit 4B, 123 Main St, San Francisco, CA 94105, USA
```

Key features:
- Immutable value objects
- Format validation
- Pattern matching
- String representation
- Equality comparison
- Type safety
- Arithmetic operations (Money)

For detailed documentation, see [Value Objects](docs/value_objects.md).

### Core Components

- **Database**: MongoDB integration and repository patterns
```python
from earnbase_common.database import MongoDB, BaseRepository
from pydantic import BaseModel

# MongoDB client with automatic retries and connection pooling
mongodb = MongoDB()
await mongodb.connect(
    url="mongodb://localhost:27017",
    db_name="mydb",
    min_pool_size=10,
    max_pool_size=100
)

# Type-safe repository pattern
class User(BaseModel):
    name: str
    email: str
    status: str = "active"

class UserRepository(BaseRepository[User]):
    def __init__(self, mongodb: MongoDB):
        super().__init__(
            collection=mongodb.db["users"],
            model=User
        )

# Use repository
repo = UserRepository(mongodb)
user = await repo.find_one({"email": "user@example.com"})
users = await repo.find_many({"status": "active"})
```

Key features:
- MongoDB client with automatic retries
- Connection pooling and lifecycle management
- Type-safe repository pattern with Pydantic
- Automatic metrics collection
- Built-in error handling

For detailed documentation, see [Database](docs/database.md).

- **Redis**: Caching and session management
```python
from earnbase_common.redis import RedisClient, Cache

# Use Redis for caching
cache = Cache()
await cache.set("key", "value", expire=300)  # 5 minutes
value = await cache.get("key")

# Use Redis for session
session = await RedisClient.get_session("session_id")
await session.set("user_id", "123")
user_id = await session.get("user_id")
```

- **HTTP**: HTTP client and request handling
```python
from earnbase_common.http import HTTPClient

# Make HTTP requests
client = HTTPClient()
response = await client.get("https://api.example.com/users")
user = await client.post(
    "https://api.example.com/users",
    json={"name": "John"}
)
```

- **Metrics**: Performance monitoring and metrics collection
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
with request_duration.time():
    # Process request
    pass

# Gauge metric
active_users = metrics.gauge(
    "active_users",
    labelnames=["status"]
)
active_users.labels(status="online").set(42)

# Summary metric
response_size = metrics.summary(
    "response_size_bytes",
    labelnames=["content_type"]
)
response_size.labels(content_type="json").observe(1024)
```

Key features:
- Multiple metric types (Counter, Histogram, Gauge, Summary)
- Automatic metrics collection for HTTP and Database operations
- Built-in service metrics (uptime, info)
- Prometheus integration
- Decorator-based metrics collection

For detailed documentation, see [Metrics](docs/metrics.md).

- **Logging**: Structured logging and error tracking
```python
from earnbase_common.logging import get_logger, setup_logging

# Configure logging
setup_logging(
    service_name="my-service",
    log_file="/var/log/my-service/app.log",
    log_level="INFO",
    debug=False  # True for development
)

# Get logger
logger = get_logger(__name__)

# Structured logging with context
logger.info(
    "Processing request",
    request_id="req-123",
    method="POST",
    path="/users"
)

# Error logging with details
try:
    result = await process_data()
except Exception as e:
    logger.error(
        "Operation failed",
        error=str(e),
        operation="process_data",
        exc_info=True
    )
```

Key features:
- Structured logging with JSON/Console formats
- Automatic log rotation and size limits
- Sensitive data filtering
- Service context enrichment
- Multiple output handlers (console, file, error file)

For detailed documentation, see [Logging](docs/logging.md).

## Database Operations

The MongoDB client now includes a retry mechanism using tenacity. This helps handle temporary connection issues and improves reliability.

### Retry Configuration

You can customize the retry behavior:

```python
from earnbase_common.retry import RetryConfig
from earnbase_common.database import mongodb

# Custom retry config
retry_config = RetryConfig(
    max_attempts=5,
    max_delay=10.0,
    min_delay=1.0,
    exceptions=(ConnectionError, TimeoutError)
)

# Apply to MongoDB client
await mongodb.connect(
    url="mongodb://localhost:27017",
    db_name="earnbase",
    retry_config=retry_config
)
```

Default retry configuration:
- Max attempts: 3
- Max delay: 5 seconds
- Min delay: 1 second
- Retried exceptions: ConnectionFailure, ServerSelectionTimeoutError

All database operations (find, insert, update, delete) automatically use the configured retry mechanism.

## Project Structure

```
earnbase_common/
├── config/         # Configuration management
├── database/       # Database integration
├── errors/         # Error handling
├── http/          # HTTP utilities
├── logging/       # Logging configuration
├── metrics/       # Metrics collection
├── middleware/    # HTTP middleware
├── models/        # Domain models
├── redis/         # Redis integration
├── responses/     # API responses
├── security/      # Security utilities
└── value_objects/ # Domain value objects
```

## Installation

```bash
pdm add earnbase-common
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Dependency Injection with Containers

The `containers` module provides a standardized way to manage dependencies across services using the dependency-injector package.

### BaseContainer

The `BaseContainer` class serves as a foundation for service-specific containers, providing common functionality:

```python
from earnbase_common.containers import BaseContainer
from dependency_injector import providers

class ServiceContainer(BaseContainer):
    """Service-specific container."""
    
    # Override config with service-specific settings
    config = providers.Singleton(ServiceSettings)
    
    # Add service-specific providers
    service = providers.Singleton(MyService)
    repository = providers.Singleton(MyRepository)
```

### Common Providers

The `BaseContainer` includes several pre-configured providers:

1. **MongoDB**:
```python
# Automatically configured from settings
mongodb = providers.Singleton(MongoDB)

# Access in your code
mongodb_client = container.mongodb()
await mongodb_client.connect(
    url=config.MONGODB_URL,
    db_name=config.MONGODB_DB_NAME
)
```

2. **Redis**:
```python
# Optional Redis support
redis = providers.Singleton(RedisClient)

# Access in your code if configured
redis_client = container.redis()
if redis_url:
    await redis_client.connect(
        url=redis_url,
        db=redis_db
    )
```

3. **Metrics**:
```python
# Metrics collection
metrics = providers.Singleton(
    MetricsManager,
    enabled=config.METRICS_ENABLED
)
```

### Resource Lifecycle

The `BaseContainer` manages resource lifecycle automatically:

```python
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    container = ServiceContainer()
    
    try:
        # Initialize resources (MongoDB, Redis, etc.)
        await container.init_resources()
        
        # Wire container
        container.wire(packages=["my_service"])
        
        yield
        
    finally:
        # Cleanup resources
        await container.shutdown_resources()
```

### Configuration Integration

The container works seamlessly with the configuration system:

```python
from earnbase_common.config import BaseSettings

class ServiceSettings(BaseSettings):
    """Service-specific settings."""
    
    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load service-specific mappings."""
        mappings = super()._load_yaml_mappings(config)
        
        # Add service-specific mappings
        service_mappings = {
            "SERVICE_NAME": config["service"]["name"],
            "MONGODB_URL": config["mongodb"]["url"],
            "REDIS_URL": config["redis"].get("url"),
            "METRICS_ENABLED": config["metrics"].get("enabled", True),
        }
        
        mappings.update(service_mappings)
        return mappings
```

### Best Practices

1. **Resource Management**:
   - Always use `init_resources()` and `shutdown_resources()`
   - Handle optional resources like Redis gracefully
   - Implement proper error handling for resource initialization

2. **Configuration**:
   - Use type-safe configuration with proper defaults
   - Handle optional settings gracefully
   - Validate configuration during initialization

3. **Dependency Wiring**:
   - Wire containers at application startup
   - Use proper package scoping for wiring
   - Avoid circular dependencies

4. **Error Handling**:
   - Handle resource initialization failures
   - Implement proper cleanup in shutdown
   - Log resource lifecycle events

### Configuration

The configuration system provides a flexible and type-safe way to manage settings:

```python
from earnbase_common.config import BaseSettings

class ServiceSettings(BaseSettings):
    """Service-specific settings."""
    
    # Default values with type hints
    SERVICE_NAME: str
    DEBUG: bool = True
    HTTP_PORT: int = 8000

# Load from file
settings = ServiceSettings("config.yaml")

# Load with environment variables
# SERVICE_NAME=my-service python app.py

# Load with direct arguments
settings = ServiceSettings(
    config_path="config.yaml",
    DEBUG=False,
    HTTP_PORT=9000
)
```

Key features:
- Multiple configuration sources (YAML, env vars, direct args)
- Type validation and immutability
- Environment-specific settings
- Secure handling of sensitive data
- Service-specific prefixes for env vars

For detailed documentation, see [Configuration](docs/config.md).

### Dependency Injection

The containers module provides a powerful dependency injection system:

```python
from earnbase_common.containers import BaseContainer
from dependency_injector import providers

class ServiceContainer(BaseContainer):
    """Service container."""
    
    # Common providers are pre-configured:
    # - config: Settings management
    # - mongodb: Database connection
    # - redis: Cache client
    # - metrics: Metrics collection
    
    # Add service-specific providers
    repository = providers.Singleton(
        Repository,
        mongodb=mongodb
    )
    
    service = providers.Singleton(
        Service,
        repository=repository,
        redis=redis
    )

# Resource lifecycle management
async def lifespan(app: FastAPI):
    container = ServiceContainer()
    try:
        await container.init_resources()
        container.wire(packages=["my_service"])
        yield
    finally:
        await container.shutdown_resources()
```

Key features:
- Pre-configured common providers
- Resource lifecycle management
- Integration with FastAPI
- Testing support with provider overrides
- Async resource providers
- Factory and contextual providers

For detailed documentation, see [Containers](docs/containers.md).

- **Middleware**: HTTP middleware components
```python
from fastapi import FastAPI
from earnbase_common.middleware import (
    SecurityHeadersMiddleware,
    RequestTrackingMiddleware
)

app = FastAPI()

# Add security headers
app.add_middleware(SecurityHeadersMiddleware)  # Adds security headers

# Add request tracking
app.add_middleware(RequestTrackingMiddleware)  # Tracks request details

@app.get("/users")
async def get_users(request: Request):
    # Access request tracking info
    request_id = request.state.request_id
    start_time = request.state.start_time
    
    return {"request_id": request_id}
```

Key features:
- Security headers middleware (XSS, CSP, HSTS)
- Request tracking with unique IDs
- Request/Response logging
- Performance monitoring
- Error handling

For detailed documentation, see [Middleware](docs/middleware.md).

### Redis

Redis client with caching and session management:

```python
from earnbase_common.redis import RedisClient

# Connect to Redis
redis = await RedisClient.connect(
    url="redis://localhost:6379",
    db=0,
    prefix="myapp",  # Optional key prefix
    ttl=3600        # Default TTL in seconds
)

# Basic operations
await redis.set("user:123", "John Doe")
value = await redis.get("user:123")  # "John Doe"

# Custom expiration
await redis.set("session:abc", "data", expire=1800)  # 30 minutes

# Check existence and TTL
exists = await redis.exists("user:123")  # True
ttl = await redis.ttl("session:abc")     # Seconds remaining

# Close connection
await redis.close()
```

Key features:
- Connection pooling and management
- Key prefixing and TTL configuration
- Structured error handling and logging
- Support for caching and sessions
- Distributed locks and rate limiting
- Pub/Sub messaging

For detailed documentation, see [Redis](docs/redis.md).

### Responses

Standardized API response models:

```python
from earnbase_common.responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    CustomJSONResponse
)

# Success response
response = SuccessResponse(
    message="User created",
    data={"id": "123", "name": "John"},
    meta={"timestamp": "2024-01-12T00:00:00Z"}
)

# Error response
error = ErrorResponse(
    error="Validation failed",
    details={"field": "email", "message": "Invalid format"},
    errors=[
        {"field": "email", "message": "Invalid format"},
        {"field": "phone", "message": "Required field"}
    ]
)

# Paginated response
paginated = PaginatedResponse(
    data=[{"id": "1"}, {"id": "2"}],
    meta={
        "page": 1,
        "per_page": 10,
        "total": 100,
        "total_pages": 10
    }
)

# FastAPI integration
app = FastAPI()

@app.get(
    "/users/{user_id}",
    response_model=SuccessResponse,
    response_class=CustomJSONResponse
)
async def get_user(user_id: str):
    return {
        "id": user_id,
        "name": "John Doe"
    }
```

Key features:
- Standardized response structure
- Type validation with Pydantic
- Error handling with details
- Pagination support
- Custom JSON formatting
- FastAPI integration

For detailed documentation, see [Responses](docs/responses.md).
``` 
</rewritten_file>
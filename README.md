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
from uuid import UUID

class User(BaseModel):
    name: str
    email: str
    created_at: datetime

# Models are immutable by default
user = User(name="John", email="john@example.com")
# user.name = "Jane"  # This will raise an error
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
        self.status = "placed"
        self.add_event(
            OrderCreated(
                event_type="OrderCreated",
                aggregate_id=str(self.id),
                aggregate_type="Order",
                order_id=str(self.id),
                total_amount=self.total
            )
        )
        self.increment_version()

order = Order(customer_id="123", total=100.0)
order.place()
print(order.events)  # [OrderCreated(id=..., aggregate_id=...)]
```

### Security

Comprehensive security utilities:

- **SecurityPolicy**: Centralized security configuration
```python
from earnbase_common.security import SecurityPolicy

policy = SecurityPolicy()
min_length = policy.PASSWORD_MIN_LENGTH  # 8
max_attempts = policy.MAX_LOGIN_ATTEMPTS  # 5
token_expire = policy.ACCESS_TOKEN_EXPIRE_MINUTES  # 30
```

- **TokenManager**: JWT token handling with type safety
```python
from earnbase_common.security import JWTConfig, TokenManager

config = JWTConfig(secret_key="your-secret-key")
manager = TokenManager(config)

# Create access token
token = manager.create_token(
    data={"user_id": "123"},
    token_type="access"
)
print(str(token))  # Bearer eyJ0eXAi...

# Verify token
try:
    payload = manager.verify_token(token.value, expected_type="access")
except ValidationError as e:
    print(e)  # Token has expired
```

- **PasswordHasher**: Secure password handling with policy validation
```python
from earnbase_common.security import PasswordHasher

hasher = PasswordHasher()

# Hash password with policy validation
try:
    hash_value = await hasher.hash("weak")
except ValidationError as e:
    print(e)  # Password must be at least 8 characters long

# Hash valid password
hash_value = await hasher.hash("StrongP@ssw0rd")
print(str(hash_value))  # ********

# Verify password
is_valid = await hasher.verify("StrongP@ssw0rd", hash_value.value)
print(is_valid)  # True
```

### Value Objects

Immutable value objects for common domain concepts:

- **Email**: Email validation and formatting with regex pattern
```python
from earnbase_common.value_objects import Email

# Create and validate an email
email = Email(value="user@example.com")
print(str(email))  # user@example.com

# Invalid email will raise ValueError
try:
    invalid_email = Email(value="invalid-email")
except ValueError as e:
    print(e)  # Invalid email format
```

- **PhoneNumber**: Phone number validation with country code support
```python
from earnbase_common.value_objects import PhoneNumber

# Create phone number with country code
phone = PhoneNumber(value="1234567890", country_code="84")
print(str(phone))  # +841234567890

# Invalid phone number will raise ValueError
try:
    invalid_phone = PhoneNumber(value="123", country_code="84")
except ValueError as e:
    print(e)  # Invalid phone number format
```

- **Money**: Currency handling with validation and arithmetic operations
```python
from earnbase_common.value_objects import Money
from decimal import Decimal

# Create money objects
balance = Money(amount=Decimal("100.50"), currency="USD")
payment = Money(amount=Decimal("50.25"), currency="USD")

# Arithmetic operations
new_balance = balance - payment
print(str(new_balance))  # 50.25 USD

# Cannot add different currencies
try:
    eur = Money(amount=Decimal("20"), currency="EUR")
    total = balance + eur
except ValueError as e:
    print(e)  # Cannot add different currencies
```

- **Address**: Address formatting with unit support
```python
from earnbase_common.value_objects import Address

# Create address with unit
address = Address(
    street="123 Main St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105",
    unit="4B"
)
print(str(address))  # Unit 4B, 123 Main St, San Francisco, CA 94105, USA

# Create address without unit
office = Address(
    street="456 Market St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105"
)
print(str(office))  # 456 Market St, San Francisco, CA 94105, USA
```

### Core Components

- **Database**: MongoDB integration and repository patterns
```python
from earnbase_common.database import MongoRepository
from earnbase_common.models import BaseModel

class UserRepository(MongoRepository[User]):
    collection_name = "users"

    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.find_one({"email.value": email})

# Use repository
repo = UserRepository()
user = await repo.find_by_email("user@example.com")
await repo.save(user)
```

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
from earnbase_common.metrics import Counter, Histogram

# Track request count
request_counter = Counter("http_requests_total", "Total HTTP requests")
request_counter.inc()

# Track request duration
request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds"
)
with request_duration.time():
    # Process request
    pass
```

- **Logging**: Structured logging and error tracking
```python
from earnbase_common.logging import Logger

logger = Logger(__name__)
logger.info("Processing request", request_id="123")
try:
    # Some operation
    pass
except Exception as e:
    logger.error("Failed to process request", error=str(e))
```

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
``` 
</rewritten_file>
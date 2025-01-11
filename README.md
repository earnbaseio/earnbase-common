# Earnbase Common

Core library for Earnbase Platform services.

## Overview

Earnbase Common provides shared components, utilities, and standards for building microservices in the Earnbase Platform. It implements common patterns and best practices to ensure consistency across services.

## Features

### Domain-Driven Design Components

- **Base Models**
  - `BaseModel`: Foundation for all domain models with JSON serialization
  - `DomainEvent`: Event tracking with automatic type assignment
  - `AggregateRoot`: Aggregate root pattern with event management

- **Value Objects**
  - `Email`: Email validation and formatting
  - `PasswordHash`: Secure password hash handling
  - `Token`: JWT token management with expiration
  - `PhoneNumber`: Phone number validation with country codes
  - `Money`: Currency handling with validation
  - `Address`: Address formatting and validation

### Security

- **Password Management**
  - Strong password validation with configurable policies
  - Secure hashing using bcrypt
  - Password verification utilities

- **Token Management**
  - JWT token creation and validation
  - Support for access and refresh tokens
  - Configurable token expiration policies

### Metrics & Monitoring

- **Prometheus Integration**
  - Counter, Histogram, Gauge, Summary metrics
  - Custom metric decorators
  - Standardized metric naming

- **Decorators**
  - `@metrics_decorator.counter`: Count method calls
  - `@metrics_decorator.histogram`: Measure execution time

### Database & Caching

- MongoDB client with connection pooling
- Redis client for caching
- Repository pattern implementations

### Error Handling

- Standard error types
- Error response formatting
- Validation error handling

## Installation

```bash
pdm add earnbase-common
```

## Quick Start

```python
from earnbase_common.models import BaseModel
from earnbase_common.value_objects import Email, Money
from earnbase_common.security import SecurityPolicy, TokenManager
from earnbase_common.metrics import metrics_decorator

# Define a domain model
class User(BaseModel):
    email: Email
    balance: Money
    is_active: bool = True

# Use security policies
security_policy = SecurityPolicy()
min_length = security_policy.PASSWORD_MIN_LENGTH

# Track metrics
@metrics_decorator.histogram("method_duration_seconds", ["method", "status"])
async def process_user(user: User):
    # Your code here
    pass
```

## Documentation

Detailed documentation is available in the `docs` directory:

- [Models](docs/models.md): Domain models and aggregates
- [Value Objects](docs/value-objects.md): Immutable value objects
- [Security](docs/security.md): Security features and policies
- [Metrics](docs/metrics.md): Metrics collection and monitoring

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
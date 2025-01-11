# Earnbase Common

A comprehensive utility package providing common functionality for Earnbase microservices.

## Features

### Core Components

- **Configuration Management** (`config/`)
  - YAML-based configuration loading
  - Environment variable support
  - Pydantic settings validation

- **Database Integration** (`database/`)
  - MongoDB async connection management
  - Connection pooling
  - Database operation utilities

- **Error Handling** (`errors/`)
  - Standardized error classes
  - Custom exception handling
  - Error response formatting

- **HTTP Utilities** (`http/`)
  - Request/Response handling
  - HTTP client utilities
  - API response formatting

- **Logging** (`logging/`)
  - Structured logging with structlog
  - Log formatting and configuration
  - Log level management

- **Metrics** (`metrics/`)
  - Prometheus metrics integration
  - Custom metrics collection
  - Monitoring utilities

- **Middleware** (`middleware/`)
  - Request tracking
  - Authentication middleware
  - Cross-cutting concerns

- **Redis Integration** (`redis/`)
  - Async Redis client
  - Connection management
  - Caching utilities

- **Response Handling** (`responses/`)
  - Standardized response models
  - Success/Error response formatting
  - JSON serialization

- **Security** (`security/`)
  - JWT token management
  - Password hashing
  - Cryptographic utilities

## Installation

```bash
pdm add earnbase-common
```

## Usage

### Configuration

```python
from earnbase_common.config import load_config

config = load_config("config.yaml")
```

### Database

```python
from earnbase_common.database import mongodb

await mongodb.connect(url="mongodb://localhost:27017")
```

### Logging

```python
from earnbase_common.logging import get_logger

logger = get_logger(__name__)
logger.info("message", extra={"key": "value"})
```

### Redis

```python
from earnbase_common.redis import redis_client

await redis_client.connect(url="redis://localhost:6379")
```

### Response Models

```python
from earnbase_common.responses import SuccessResponse

response = SuccessResponse(
    success=True,
    message="Operation successful",
    data={"key": "value"}
)
```

## Development

### Prerequisites

- Python 3.9+
- PDM

### Setup

1. Clone the repository
2. Install dependencies:
```bash
pdm install
```

### Testing

```bash
pdm run pytest
```

### Building

```bash
pdm build
```

## Version Compatibility

- Python: >=3.9
- FastAPI: >=0.104.1
- Pydantic: >=2.5.2
- Motor: >=3.3.2

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT

## Support

For support, email dev@earnbase.io 
# Configuration

## Overview

The configuration module provides a flexible and type-safe way to manage application settings using YAML files, environment variables, and direct arguments. It extends Pydantic's BaseModel to provide validation, immutability, and type conversion.

## Features

### Base Settings

The `BaseSettings` class serves as the foundation for all configuration in Earnbase services:

```python
from earnbase_common.config import BaseSettings

class ServiceSettings(BaseSettings):
    """Service-specific settings."""
    
    # Default values with type hints
    SERVICE_NAME: str
    DEBUG: bool = True
    HTTP_PORT: int = 8000
    
    def __init__(self, config_path: str = None, **kwargs):
        """Initialize settings from multiple sources."""
        super().__init__(config_path, **kwargs)
```

### Configuration Sources

Settings are loaded from multiple sources in the following priority order:

1. Direct arguments (kwargs)
2. Environment variables
3. YAML configuration file

### Default Settings

The base configuration includes:

```python
# Service info
ENV: str = "development"
DEBUG: bool = True
ENABLE_DOCS: bool = True

# HTTP Server
HTTP_HOST: str = "0.0.0.0"
HTTP_PORT: int = 8000
HTTP_WORKERS: int = 1
API_PREFIX: str = "/api/v1"

# Logging
LOG_LEVEL: str = "INFO"
LOG_FILE: Optional[str] = None

# MongoDB
MONGODB_MIN_POOL_SIZE: int = 10
MONGODB_MAX_POOL_SIZE: int = 100

# Redis
REDIS_URL: Optional[str] = None
REDIS_DB: int = 0
REDIS_PREFIX: str = ""
REDIS_TTL: int = 3600

# Metrics
METRICS_ENABLED: bool = True
```

### YAML Configuration

Example `config.yaml`:

```yaml
service:
  name: "user-service"
  description: "User management service"
  version: "1.0.0"
  env: "development"
  debug: true
  enable_docs: true

http:
  host: "0.0.0.0"
  port: 8000
  workers: 1
  api_prefix: "/api/v1"

logging:
  level: "INFO"
  file: "logs/service.log"

mongodb:
  url: "mongodb://localhost:27017"
  db_name: "users"
  min_pool_size: 10
  max_pool_size: 100

redis:
  url: "redis://localhost:6379"
  db: 0
  prefix: "users:"
  ttl: 3600

metrics:
  enabled: true
```

### Environment Variables

Settings can be overridden using environment variables with service prefix:

```bash
# For user-service
export USER_SERVICE_HTTP_PORT=9000
export USER_SERVICE_MONGODB_URL="mongodb://prod:27017"

# For auth-service
export AUTH_SERVICE_HTTP_PORT=9001
export AUTH_SERVICE_REDIS_URL="redis://prod:6379"
```

## Key Features

### 1. Immutable Settings

Settings are immutable after initialization to ensure configuration consistency:

```python
settings = ServiceSettings(config_path="config.yaml")
# This will raise TypeError
settings.HTTP_PORT = 9000
```

### 2. Service Prefix

Environment variables are automatically prefixed based on the service name:

```python
class AuthSettings(BaseSettings):
    """Auth service settings."""
    pass

# Will look for AUTH_SERVICE_* environment variables
settings = AuthSettings()
```

### 3. Automatic Validation

Type validation and custom validators are supported:

```python
from pydantic import validator

class ValidatedSettings(BaseSettings):
    RATE_LIMITS: Dict[str, int]
    
    @validator("RATE_LIMITS")
    def validate_rate_limits(cls, v: Dict[str, int]) -> Dict[str, int]:
        for endpoint, limit in v.items():
            if limit <= 0:
                raise ValueError(f"Rate limit for {endpoint} must be positive")
        return v
```

## Best Practices

### 1. Environment-Specific Configuration

Create separate settings classes for different environments:

```python
class ProductionSettings(BaseSettings):
    """Production environment settings."""
    
    # Override defaults for production
    DEBUG: bool = False
    ENABLE_DOCS: bool = False
    
    # Additional production settings
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
```

### 2. Sensitive Data Handling

Handle sensitive data securely:

```python
from earnbase_common.security import decrypt_value

class SecureSettings(BaseSettings):
    """Settings with encrypted values."""
    
    DB_PASSWORD: str
    API_KEY: str
    
    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load and decrypt sensitive values."""
        mappings = super()._load_yaml_mappings(config)
        
        # Decrypt sensitive values
        mappings.update({
            "DB_PASSWORD": decrypt_value(config["database"]["password"]),
            "API_KEY": decrypt_value(config["api"]["key"]),
        })
        return mappings
```

### 3. Custom YAML Mappings

Extend YAML mapping for service-specific needs:

```python
class CustomSettings(BaseSettings):
    """Settings with custom mappings."""
    
    CUSTOM_FIELD: str = "default"
    
    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add custom mappings."""
        mappings = super()._load_yaml_mappings(config)
        mappings["CUSTOM_FIELD"] = config.get("custom", {}).get(
            "field", "default"
        )
        return mappings
```

## Usage Examples

### 1. Basic Usage

```python
# Load from file
settings = ServiceSettings("config.yaml")

# Load with overrides
settings = ServiceSettings(
    config_path="config.yaml",
    DEBUG=False,
    HTTP_PORT=9000
)
```

### 2. Environment-Based Configuration

```python
def get_settings():
    """Get environment-specific settings."""
    env = os.getenv("ENV", "development")
    
    if env == "production":
        return ProductionSettings("config.prod.yaml")
    elif env == "staging":
        return StagingSettings("config.staging.yaml")
    else:
        return DevelopmentSettings("config.dev.yaml")
```

### 3. With FastAPI

```python
from fastapi import FastAPI, Depends

app = FastAPI()
settings = get_settings()

@app.get("/config")
async def get_config(settings: Settings = Depends(get_settings)):
    return {
        "environment": settings.ENV,
        "debug": settings.DEBUG,
        "api_prefix": settings.API_PREFIX
    }
``` 
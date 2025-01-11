# Configuration

## Overview

The configuration module provides a flexible and type-safe way to manage application settings using YAML files and environment variables. It extends Pydantic's BaseSettings to provide validation and type conversion.

## Features

### Base Settings

```python
from earnbase_common.config import BaseSettings

class ServiceSettings(BaseSettings):
    """Service-specific settings."""
    
    def __init__(self, config_path: str, **kwargs):
        """Initialize settings from YAML file."""
        super().__init__(config_path, **kwargs)
    
    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add service-specific mappings."""
        mappings = super()._load_yaml_mappings(config)
        mappings.update({
            "CUSTOM_SETTING": config["service"].get("custom_setting"),
        })
        return mappings

# Usage
settings = ServiceSettings("config.yaml")
```

### Default Settings

The base configuration includes:

```python
# Service info
SERVICE_NAME: str
DESCRIPTION: str
VERSION: str
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
MONGODB_URL: str
MONGODB_DB_NAME: str
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

## Best Practices

### 1. Environment-Specific Configuration

```python
from earnbase_common.config import BaseSettings
from typing import Optional

class ProductionSettings(BaseSettings):
    """Production environment settings."""
    
    # Override defaults
    DEBUG: bool = False
    ENABLE_DOCS: bool = False
    
    # Additional security settings
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
    
    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load production mappings."""
        mappings = super()._load_yaml_mappings(config)
        
        # Add SSL settings
        ssl_config = config.get("ssl", {})
        mappings.update({
            "SSL_CERT_PATH": ssl_config.get("cert_path"),
            "SSL_KEY_PATH": ssl_config.get("key_path"),
        })
        
        return mappings

# Usage
if ENV == "production":
    settings = ProductionSettings("config.prod.yaml")
else:
    settings = BaseSettings("config.dev.yaml")
```

### 2. Sensitive Data Handling

```python
from earnbase_common.config import BaseSettings
from earnbase_common.security import decrypt_value

class SecureSettings(BaseSettings):
    """Settings with encrypted values."""
    
    # Sensitive fields
    DB_PASSWORD: str
    API_KEY: str
    
    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load and decrypt sensitive values."""
        mappings = super()._load_yaml_mappings(config)
        
        # Decrypt sensitive values
        db_config = config["database"]
        mappings.update({
            "DB_PASSWORD": decrypt_value(
                db_config["password"],
                self.ENCRYPTION_KEY
            ),
            "API_KEY": decrypt_value(
                config["api"]["key"],
                self.ENCRYPTION_KEY
            ),
        })
        
        return mappings
```

### 3. Configuration Validation

```python
from earnbase_common.config import BaseSettings
from pydantic import validator
from typing import Dict

class ValidatedSettings(BaseSettings):
    """Settings with custom validation."""
    
    # Custom fields
    RATE_LIMITS: Dict[str, int]
    
    @validator("RATE_LIMITS")
    def validate_rate_limits(
        cls,
        v: Dict[str, int]
    ) -> Dict[str, int]:
        """Validate rate limit values."""
        for endpoint, limit in v.items():
            if limit <= 0:
                raise ValueError(
                    f"Rate limit for {endpoint} must be positive"
                )
        return v
    
    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load validated mappings."""
        mappings = super()._load_yaml_mappings(config)
        mappings["RATE_LIMITS"] = config["rate_limits"]
        return mappings
```

## Future Features

The following features are planned for future releases:

### 1. Dynamic Configuration

```python
class DynamicSettings(BaseSettings):
    """Settings that can be updated at runtime."""
    
    def reload_config(self) -> None:
        """Reload configuration from source."""
        pass
    
    def watch_changes(self) -> None:
        """Watch for configuration changes."""
        pass
    
    async def get_setting(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """Get setting value with possible remote fetch."""
        pass
```

### 2. Configuration Store

```python
class ConfigStore:
    """Centralized configuration store."""
    
    async def get_service_config(
        self,
        service_name: str,
        version: str
    ) -> Dict[str, Any]:
        """Get service configuration."""
        pass
    
    async def update_config(
        self,
        service_name: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update service configuration."""
        pass
    
    async def watch_updates(
        self,
        service_name: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """Watch for configuration updates."""
        pass
```

### 3. Configuration Inheritance

```python
class BaseServiceConfig(BaseSettings):
    """Base configuration for all services."""
    pass

class AuthConfig(BaseServiceConfig):
    """Authentication service configuration."""
    pass

class APIConfig(BaseServiceConfig):
    """API service configuration."""
    pass
```

### 4. Enhanced Validation

```python
class ValidatedConfig(BaseSettings):
    """Configuration with enhanced validation."""
    
    @validator("MONGODB_URL")
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate MongoDB connection URL."""
        pass
    
    @validator("REDIS_URL")
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis connection URL."""
        pass
    
    def validate_connections(self) -> None:
        """Validate all service connections."""
        pass
```

### 5. Configuration Migration

```python
class ConfigMigration:
    """Handle configuration version migrations."""
    
    async def migrate(
        self,
        old_config: Dict[str, Any],
        new_version: str
    ) -> Dict[str, Any]:
        """Migrate configuration to new version."""
        pass
    
    async def rollback(
        self,
        config: Dict[str, Any],
        version: str
    ) -> Dict[str, Any]:
        """Rollback configuration to previous version."""
        pass
``` 
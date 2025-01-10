"""Base settings module."""

from typing import Optional

from pydantic_settings import BaseSettings as PydanticBaseSettings


class BaseSettings(PydanticBaseSettings):
    """Base settings class."""

    # Service info
    SERVICE_NAME: str
    DESCRIPTION: str
    VERSION: str = "0.1.0"
    ENV: str = "development"
    DEBUG: bool = True
    ENABLE_DOCS: bool = True

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/service.log"

    # HTTP Server
    HTTP_HOST: str = "0.0.0.0"
    HTTP_PORT: int = 5000
    HTTP_WORKERS: int = 1
    API_PREFIX: str = "/api/v1"

    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100

    # Metrics
    METRICS_ENABLED: bool = True
    METRICS_PORT: Optional[int] = None

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True

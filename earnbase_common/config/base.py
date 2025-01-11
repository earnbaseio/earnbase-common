"""Base settings for all services."""

import os
from typing import Any, Dict, Optional

import yaml
from earnbase_common.logging import get_logger
from pydantic_settings import BaseSettings as PydanticBaseSettings

logger = get_logger(__name__)


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # log
    logger.info(f"Loading config from {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


class BaseSettings(PydanticBaseSettings):
    """Base settings class for all services."""

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

    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load YAML mappings. Override this method to add service-specific mappings."""
        return {
            # Service info
            "SERVICE_NAME": config["service"]["name"],
            "DESCRIPTION": config["service"]["description"],
            "VERSION": config["service"]["version"],
            "ENV": config["service"].get("env", "development"),
            "DEBUG": config["service"].get("debug", True),
            "ENABLE_DOCS": config["service"].get("enable_docs", True),
            # HTTP Server
            "HTTP_HOST": config["http"].get("host", "0.0.0.0"),
            "HTTP_PORT": config["http"].get("port", 8000),
            "HTTP_WORKERS": config["http"].get("workers", 1),
            "API_PREFIX": config["http"].get("api_prefix", "/api/v1"),
            # Logging
            "LOG_LEVEL": config["logging"].get("level", "INFO"),
            "LOG_FILE": config["logging"].get("file"),
            # MongoDB
            "MONGODB_URL": config["mongodb"]["url"],
            "MONGODB_DB_NAME": config["mongodb"]["db_name"],
            "MONGODB_MIN_POOL_SIZE": config["mongodb"].get("min_pool_size", 10),
            "MONGODB_MAX_POOL_SIZE": config["mongodb"].get("max_pool_size", 100),
            # Redis
            "REDIS_URL": config["redis"].get("url"),
            "REDIS_DB": config["redis"].get("db", 0),
            "REDIS_PREFIX": config["redis"].get("prefix", ""),
            "REDIS_TTL": config["redis"].get("ttl", 3600),
            # Metrics
            "METRICS_ENABLED": config.get("metrics", {}).get("enabled", True),
        }

    def __init__(self, config_path: str, **kwargs):
        """Initialize settings with values from YAML."""
        config = load_yaml_config(config_path)

        # log count of keys
        logger.info(f"Loaded {len(config)} keys from {config_path}")

        # Get YAML mappings from child class if overridden
        yaml_mappings = self._load_yaml_mappings(config)

        # Update kwargs with YAML values
        for key, value in yaml_mappings.items():
            if key not in kwargs:
                kwargs[key] = value

        super().__init__(**kwargs)

    @classmethod
    def get_service_prefix(cls) -> str:
        """Get service prefix for environment variables."""
        module_path = cls.__module__.split(".")
        if len(module_path) >= 2:
            service_name = module_path[0].replace("-", "_").upper()
            return f"{service_name}_"
        return ""

"""Base settings module."""

import os
from typing import Any, Dict, Optional

import yaml
from earnbase_common.logging import get_logger

logger = get_logger(__name__)


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load YAML config file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        logger.info(
            "config_loaded",
            path=config_path,
            keys=len(config) if config else 0,
        )
        return config


class BaseSettings:
    """Base settings class."""

    REQUIRED_FIELDS = [
        ("service", ["name", "description", "version"]),
        ("mongodb", ["url", "db_name"]),
    ]

    def __init__(
        self,
        config_path: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialize settings."""
        # Load config from file
        config = {}
        if config_path:
            config = load_yaml_config(config_path)
            self._validate_config(config)

        # Load mappings
        yaml_mappings = self._load_yaml_mappings(config)

        # Override with environment variables
        env_mappings = self._load_env_mappings()
        yaml_mappings.update(env_mappings)

        # Override with kwargs
        yaml_mappings.update(kwargs)

        # Set attributes
        for key, value in yaml_mappings.items():
            setattr(self, key, value)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate required fields in config."""
        for section, fields in self.REQUIRED_FIELDS:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")

            section_config = config[section]
            for field in fields:
                if field not in section_config:
                    raise ValueError(f"Missing required field: {section}.{field}")

    def _load_yaml_mappings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load YAML mappings. Override this method to add service-specific mappings."""
        service_config = config.get("service", {})
        http_config = config.get("http", {})
        logging_config = config.get("logging", {})
        mongodb_config = config.get("mongodb", {})
        redis_config = config.get("redis", {})
        metrics_config = config.get("metrics", {})

        return {
            # Service info
            "SERVICE_NAME": service_config.get("name", "default-service"),
            "DESCRIPTION": service_config.get(
                "description", "Default service description"
            ),
            "VERSION": service_config.get("version", "0.1.0"),
            "ENV": service_config.get("env", "development"),
            "DEBUG": service_config.get("debug", True),
            "ENABLE_DOCS": service_config.get("enable_docs", True),
            # HTTP Server
            "HTTP_HOST": http_config.get("host", "0.0.0.0"),
            "HTTP_PORT": http_config.get("port", 8000),
            "HTTP_WORKERS": http_config.get("workers", 1),
            "API_PREFIX": http_config.get("api_prefix", "/api/v1"),
            # Logging
            "LOG_LEVEL": logging_config.get("level", "INFO"),
            "LOG_FILE": logging_config.get("file"),
            # MongoDB
            "MONGODB_URL": mongodb_config.get("url", "mongodb://localhost:27017"),
            "MONGODB_DB_NAME": mongodb_config.get("db_name", "default"),
            "MONGODB_MIN_POOL_SIZE": mongodb_config.get("min_pool_size", 10),
            "MONGODB_MAX_POOL_SIZE": mongodb_config.get("max_pool_size", 100),
            # Redis
            "REDIS_URL": redis_config.get("url"),
            "REDIS_DB": redis_config.get("db", 0),
            "REDIS_PREFIX": redis_config.get("prefix", ""),
            "REDIS_TTL": redis_config.get("ttl", 3600),
            # Metrics
            "METRICS_ENABLED": metrics_config.get("enabled", True),
        }

    def _load_env_mappings(self) -> Dict[str, Any]:
        """Load environment variables."""
        mappings = {}

        for key in os.environ:
            # Check both with and without prefix
            clean_key = key
            prefix = self.get_service_prefix()
            if prefix and key.startswith(prefix):
                clean_key = key[len(prefix) :]

            value = os.environ[key]

            # Convert common types
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "").isdigit() and value.count(".") == 1:
                value = float(value)

            mappings[clean_key] = value

        return mappings

    @classmethod
    def get_service_prefix(cls) -> str:
        """Get service prefix for environment variables."""
        # For test cases or direct usage, return empty string
        if (
            cls.__module__ == "__main__"
            or cls.__module__.startswith("test_")
            or cls == BaseSettings
        ):
            return ""

        module_path = cls.__module__.split(".")
        if len(module_path) > 1:
            service_name = module_path[0].replace("-", "_").upper()
            return f"{service_name}_"
        return ""

"""Base settings module."""

import os
from typing import Any, Dict, Optional

import yaml
from earnbase_common.logging import get_logger
from pydantic import BaseModel, ConfigDict

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


class BaseSettings(BaseModel):
    """Base settings class."""

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields
        validate_assignment=True,  # Validate on assignment
        frozen=True,  # Make settings immutable
    )

    def __init__(
        self,
        config_path: Optional[str] = None,
        **kwargs,
    ):
        """Initialize settings."""
        # Load config from file
        config = {}
        if config_path:
            config = load_yaml_config(config_path)

        # Override with environment variables
        env_mappings = self._load_env_mappings()
        config.update(env_mappings)

        # Override with kwargs
        config.update(kwargs)

        # Initialize model
        super().__init__(**config)

    def _load_env_mappings(self) -> Dict[str, Any]:
        """Load environment variables."""
        mappings = {}
        for key, value in os.environ.items():
            if key.isupper():  # Only load uppercase env vars
                mappings[key] = value
        return mappings

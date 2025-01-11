"""Tests for base settings."""

import os
import tempfile
from unittest.mock import patch

import pytest
import yaml
from earnbase_common.config.base import BaseSettings, load_yaml_config


@pytest.mark.unit
@pytest.mark.config
class TestBaseSettings:
    """Test BaseSettings."""

    @pytest.fixture
    def sample_config(self):
        """Create sample config dictionary."""
        return {
            "service": {
                "name": "test-service",
                "description": "Test Service",
                "version": "0.1.0",
                "env": "test",
                "debug": True,
                "enable_docs": True,
            },
            "http": {
                "host": "localhost",
                "port": 8080,
                "workers": 2,
                "api_prefix": "/api/v2",
            },
            "logging": {
                "level": "DEBUG",
                "file": "/tmp/test.log",
            },
            "mongodb": {
                "url": "mongodb://localhost:27017",
                "db_name": "test_db",
                "min_pool_size": 5,
                "max_pool_size": 50,
            },
            "redis": {
                "url": "redis://localhost:6379",
                "db": 1,
                "prefix": "test:",
                "ttl": 1800,
            },
            "metrics": {
                "enabled": True,
            },
        }

    @pytest.fixture
    def config_file(self, sample_config):
        """Create temporary config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(sample_config, f)
            return f.name

    def test_load_yaml_config(self, config_file, sample_config):
        """Test loading YAML config."""
        config = load_yaml_config(config_file)
        assert config == sample_config

        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            load_yaml_config("nonexistent.yaml")

    def test_base_settings_initialization(self, config_file):
        """Test BaseSettings initialization."""
        settings = BaseSettings(config_path=config_file)

        # Check service info
        assert settings.SERVICE_NAME == "test-service"
        assert settings.DESCRIPTION == "Test Service"
        assert settings.VERSION == "0.1.0"
        assert settings.ENV == "test"
        assert settings.DEBUG is True
        assert settings.ENABLE_DOCS is True

        # Check HTTP settings
        assert settings.HTTP_HOST == "localhost"
        assert settings.HTTP_PORT == 8080
        assert settings.HTTP_WORKERS == 2
        assert settings.API_PREFIX == "/api/v2"

        # Check logging settings
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.LOG_FILE == "/tmp/test.log"

        # Check MongoDB settings
        assert settings.MONGODB_URL == "mongodb://localhost:27017"
        assert settings.MONGODB_DB_NAME == "test_db"
        assert settings.MONGODB_MIN_POOL_SIZE == 5
        assert settings.MONGODB_MAX_POOL_SIZE == 50

        # Check Redis settings
        assert settings.REDIS_URL == "redis://localhost:6379"
        assert settings.REDIS_DB == 1
        assert settings.REDIS_PREFIX == "test:"
        assert settings.REDIS_TTL == 1800

        # Check metrics settings
        assert settings.METRICS_ENABLED is True

    def test_settings_with_env_override(self, config_file):
        """Test environment variable override."""
        with patch.dict(
            os.environ,
            {
                "SERVICE_NAME": "env-service",
                "HTTP_PORT": "9000",
                "MONGODB_URL": "mongodb://testhost:27017",
                "REDIS_TTL": "7200",
            },
        ):
            settings = BaseSettings(config_path=config_file)
            assert settings.SERVICE_NAME == "env-service"
            assert settings.HTTP_PORT == 9000
            assert settings.MONGODB_URL == "mongodb://testhost:27017"
            assert settings.REDIS_TTL == 7200

    def test_settings_with_kwargs_override(self, config_file):
        """Test kwargs override."""
        settings = BaseSettings(
            config_path=config_file,
            SERVICE_NAME="kwarg-service",
            HTTP_PORT=9090,
            MONGODB_URL="mongodb://kwarghost:27017",
        )
        assert settings.SERVICE_NAME == "kwarg-service"
        assert settings.HTTP_PORT == 9090
        assert settings.MONGODB_URL == "mongodb://kwarghost:27017"

    def test_settings_defaults(self, sample_config):
        """Test default values."""
        # Remove optional fields
        minimal_config = {
            "service": {
                "name": "test-service",
                "description": "Test Service",
                "version": "0.1.0",
            },
            "http": {},
            "logging": {},
            "mongodb": {
                "url": "mongodb://localhost:27017",
                "db_name": "test_db",
            },
            "redis": {},
            "metrics": {},
        }

        # Create config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(minimal_config, f)
            config_file = f.name

        settings = BaseSettings(config_path=config_file)

        # Check default values
        assert settings.ENV == "development"
        assert settings.DEBUG is True
        assert settings.ENABLE_DOCS is True
        assert settings.HTTP_HOST == "0.0.0.0"
        assert settings.HTTP_PORT == 8000
        assert settings.HTTP_WORKERS == 1
        assert settings.API_PREFIX == "/api/v1"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.LOG_FILE is None
        assert settings.MONGODB_MIN_POOL_SIZE == 10
        assert settings.MONGODB_MAX_POOL_SIZE == 100
        assert settings.REDIS_URL is None
        assert settings.REDIS_DB == 0
        assert settings.REDIS_PREFIX == ""
        assert settings.REDIS_TTL == 3600
        assert settings.METRICS_ENABLED is True

    def test_service_prefix(self):
        """Test service prefix generation."""
        # Test default prefix
        assert BaseSettings.get_service_prefix() == ""

        # Test custom module path
        class CustomSettings(BaseSettings):
            """Custom settings class."""

            pass

        CustomSettings.__module__ = "my_service.config"
        assert CustomSettings.get_service_prefix() == "MY_SERVICE_"

        # Test hyphenated service name
        CustomSettings.__module__ = "my-service.config"
        assert CustomSettings.get_service_prefix() == "MY_SERVICE_"

    def test_invalid_config(self):
        """Test invalid configuration."""
        # Missing required fields
        invalid_config = {
            "service": {
                "name": "test-service",
                # Missing description and version
            },
            "mongodb": {
                # Missing required fields
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(invalid_config, f)
            config_file = f.name

        with pytest.raises(ValueError):
            BaseSettings(config_path=config_file)

    def test_yaml_mappings_override(self, sample_config):
        """Test overriding _load_yaml_mappings."""

        class CustomSettings(BaseSettings):
            """Custom settings with additional mappings."""

            CUSTOM_FIELD: str = "default"

            def _load_yaml_mappings(self, config):
                mappings = super()._load_yaml_mappings(config)
                mappings["CUSTOM_FIELD"] = config.get("custom", {}).get(
                    "field", "default"
                )
                return mappings

        # Add custom field to config
        sample_config["custom"] = {"field": "custom_value"}

        # Create config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(sample_config, f)
            config_file = f.name

        settings = CustomSettings(config_path=config_file)
        assert settings.CUSTOM_FIELD == "custom_value"

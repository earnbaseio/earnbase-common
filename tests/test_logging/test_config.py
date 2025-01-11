"""Tests for logging configuration."""

import json
import logging
import os
import tempfile
from unittest.mock import patch

import pytest
import structlog
from earnbase_common.logging import setup_logging
from earnbase_common.logging.config import (
    ensure_log_dir,
    get_logging_config,
    get_shared_processors,
)


@pytest.mark.unit
@pytest.mark.logging
class TestLoggingConfig:
    """Test logging configuration."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def log_file(self, temp_log_dir):
        """Create log file path."""
        return os.path.join(temp_log_dir, "test.log")

    def test_ensure_log_dir(self, temp_log_dir):
        """Test log directory creation."""
        log_file = os.path.join(temp_log_dir, "logs", "test.log")
        ensure_log_dir(log_file)
        assert os.path.exists(os.path.dirname(log_file))

    def test_get_shared_processors(self):
        """Test shared processors configuration."""
        processors = get_shared_processors()

        # Convert processors to string representation for easier checking
        processor_strings = [str(p) for p in processors]

        # Check required processors are present
        assert any("TimeStamper" in p for p in processor_strings)
        assert any("add_logger_name" in p for p in processor_strings)
        assert any("add_log_level" in p for p in processor_strings)
        assert any("add_service_info" in p for p in processor_strings)
        assert any("filter_sensitive_data" in p for p in processor_strings)
        assert any("StackInfoRenderer" in p for p in processor_strings)
        assert any("format_exc_info" in p for p in processor_strings)

    def test_get_logging_config(self, log_file):
        """Test logging configuration generation."""
        config = get_logging_config(
            service_name="test-service",
            log_file=log_file,
            log_level="DEBUG",
            debug=True,
        )

        # Check basic structure
        assert config["version"] == 1
        assert not config["disable_existing_loggers"]

        # Check formatters
        assert "json" in config["formatters"]
        assert "colored" in config["formatters"]

        # Check handlers
        handlers = config["handlers"]
        assert "console" in handlers
        assert "file" in handlers
        assert "error_file" in handlers

        # Check console handler
        assert handlers["console"]["formatter"] == "colored"
        assert handlers["console"]["class"] == "logging.StreamHandler"

        # Check file handler
        assert handlers["file"]["formatter"] == "json"
        assert handlers["file"]["filename"] == log_file
        assert handlers["file"]["maxBytes"] == 10485760  # 10MB
        assert handlers["file"]["backupCount"] == 5

        # Check loggers
        loggers = config["loggers"]
        assert "" in loggers  # Root logger
        assert "uvicorn" in loggers
        assert "uvicorn.error" in loggers
        assert "uvicorn.access" in loggers

    def test_setup_logging(self, log_file):
        """Test logging setup."""
        setup_logging(
            service_name="test-service",
            log_file=log_file,
            log_level="INFO",
            debug=False,
        )

        # Get root logger
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

        # Check handlers
        handler_classes = [h.__class__.__name__ for h in root_logger.handlers]
        assert "StreamHandler" in handler_classes
        assert "RotatingFileHandler" in handler_classes

    def test_logging_output_format(self, log_file):
        """Test logging output format."""
        setup_logging(
            service_name="test-service",
            log_file=log_file,
            log_level="INFO",
            debug=False,
        )
        logger = structlog.get_logger()

        # Log a test message
        test_data = {
            "user_id": 123,
            "action": "test",
            "password": "secret123",  # Should be filtered
        }
        logger.info("test_message", **test_data)

        # Read log file
        with open(log_file, "r") as f:
            log_entry = json.loads(f.read().strip())

        # Check log structure
        assert "timestamp" in log_entry
        assert log_entry["event"] == "test_message"
        assert log_entry["level"] == "info"
        assert log_entry["user_id"] == 123
        assert log_entry["action"] == "test"
        assert log_entry["password"] == "***FILTERED***"  # Should be filtered

    def test_error_logging(self, log_file):
        """Test error logging configuration."""
        setup_logging(service_name="test-service", log_file=log_file)
        logger = structlog.get_logger()

        # Create an exception
        try:
            raise ValueError("Test error")
        except ValueError:
            logger.exception("error_occurred")

        # Check error log file
        error_log = os.path.join(os.path.dirname(log_file), "test-service-error.log")
        assert os.path.exists(error_log)

        with open(error_log, "r") as f:
            log_entry = json.loads(f.read().strip())
            assert log_entry["event"] == "error_occurred"
            assert "ValueError: Test error" in log_entry["exception"]

    def test_debug_mode_logging(self, log_file):
        """Test logging in debug mode."""
        setup_logging(service_name="test-service", log_file=log_file, debug=True)
        logger = structlog.get_logger()

        with patch("sys.stdout") as mock_stdout:
            logger.debug("debug_message", test=123)
            # In debug mode, output should be colored and human-readable
            mock_stdout.write.assert_called()

    def test_log_rotation(self, log_file):
        """Test log file rotation."""
        setup_logging(service_name="test-service", log_file=log_file)
        logger = structlog.get_logger()

        # Write enough logs to trigger rotation
        large_data = "x" * 1024 * 1024  # 1MB
        for _ in range(15):  # Should create multiple log files
            logger.info("large_message", data=large_data)

        # Check rotated files exist
        log_dir = os.path.dirname(log_file)
        rotated_files = [f for f in os.listdir(log_dir) if f.startswith("test.log.")]
        assert len(rotated_files) > 0
        assert len(rotated_files) <= 5  # Max backup count

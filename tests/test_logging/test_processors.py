"""Tests for logging processors."""

import pytest
import structlog
from earnbase_common.logging.processors import add_service_info, filter_sensitive_data


@pytest.mark.unit
@pytest.mark.logging
class TestLoggingProcessors:
    """Test logging processors."""

    @pytest.fixture
    def logger(self):
        """Create test logger."""
        return structlog.get_logger()

    def test_add_service_info(self, logger):
        """Test add_service_info processor."""
        # Basic event dict
        event_dict = {"event": "test_event"}
        result = add_service_info(logger, "test", event_dict)

        # Should return unmodified dict (service info added by service)
        assert result == event_dict

    def test_filter_sensitive_data_basic(self, logger):
        """Test basic sensitive data filtering."""
        event_dict = {
            "event": "user_login",
            "username": "testuser",
            "password": "secret123",
            "token": "abc123xyz",
            "normal_field": "normal_value",
        }

        result = filter_sensitive_data(logger, "test", event_dict)

        # Check sensitive fields are filtered
        assert result["password"] == "***FILTERED***"
        assert result["token"] == "***FILTERED***"
        # Non-sensitive fields should remain unchanged
        assert result["username"] == "testuser"
        assert result["normal_field"] == "normal_value"

    def test_filter_sensitive_data_nested(self, logger):
        """Test filtering sensitive data in nested structures."""
        event_dict = {
            "event": "api_call",
            "request": {
                "headers": {
                    "authorization": "Bearer token123",
                    "content-type": "application/json",
                },
                "body": {"user": {"api_key": "key123", "name": "Test User"}},
            },
            "response": {"access_token": "new_token", "status": "success"},
        }

        result = filter_sensitive_data(logger, "test", event_dict)

        # Check nested sensitive fields are filtered
        assert result["request"]["headers"]["authorization"] == "***FILTERED***"
        assert result["request"]["body"]["user"]["api_key"] == "***FILTERED***"
        assert result["response"]["access_token"] == "***FILTERED***"
        # Non-sensitive fields should remain unchanged
        assert result["request"]["headers"]["content-type"] == "application/json"
        assert result["request"]["body"]["user"]["name"] == "Test User"
        assert result["response"]["status"] == "success"

    def test_filter_sensitive_data_in_lists(self, logger):
        """Test filtering sensitive data in lists."""
        event_dict = {
            "event": "bulk_operation",
            "items": [
                {"id": 1, "secret_key": "secret1"},
                {"id": 2, "secret_key": "secret2"},
                {"id": 3, "normal_key": "normal"},
            ],
            "tokens": ["token1", "token2"],
            "normal_list": ["a", "b", "c"],
        }

        result = filter_sensitive_data(logger, "test", event_dict)

        # Check sensitive data in lists is filtered
        assert result["items"][0]["secret_key"] == "***FILTERED***"
        assert result["items"][1]["secret_key"] == "***FILTERED***"
        assert result["items"][2]["normal_key"] == "normal"
        # Lists themselves are not filtered unless containing dicts
        assert result["normal_list"] == ["a", "b", "c"]

    def test_filter_sensitive_data_case_insensitive(self, logger):
        """Test case-insensitive filtering."""
        event_dict = {
            "PASSWORD": "secret1",
            "Api_Key": "key123",
            "user_TOKEN": "token123",
            "PRIVATE_KEY": "private123",
        }

        result = filter_sensitive_data(logger, "test", event_dict)

        # All variations should be filtered
        assert result["PASSWORD"] == "***FILTERED***"
        assert result["Api_Key"] == "***FILTERED***"
        assert result["user_TOKEN"] == "***FILTERED***"
        assert result["PRIVATE_KEY"] == "***FILTERED***"

    def test_filter_sensitive_data_empty_values(self, logger):
        """Test filtering with empty or None values."""
        event_dict = {
            "password": "",
            "token": None,
            "api_key": {},
            "secret": [],
            "normal": None,
        }

        result = filter_sensitive_data(logger, "test", event_dict)

        # Empty sensitive fields should still be filtered
        assert result["password"] == "***FILTERED***"
        assert result["token"] == "***FILTERED***"
        assert result["api_key"] == "***FILTERED***"
        assert result["secret"] == "***FILTERED***"
        # Empty normal fields should remain unchanged
        assert result["normal"] is None

    def test_filter_sensitive_data_complex_nested(self, logger):
        """Test filtering in complex nested structures."""
        event_dict = {
            "level1": {
                "level2": {"level3": {"password": "deep_secret", "normal": "value"}},
                "list_of_dicts": [
                    {"token": "t1", "data": "d1"},
                    {"token": "t2", "data": "d2"},
                ],
            },
            "mixed_list": [{"api_key": "k1"}, "normal_string", {"normal_key": "value"}],
        }

        result = filter_sensitive_data(logger, "test", event_dict)

        # Check deep nested filtering
        assert result["level1"]["level2"]["level3"]["password"] == "***FILTERED***"
        assert result["level1"]["level2"]["level3"]["normal"] == "value"

        # Check list of dicts
        assert result["level1"]["list_of_dicts"][0]["token"] == "***FILTERED***"
        assert result["level1"]["list_of_dicts"][0]["data"] == "d1"
        assert result["level1"]["list_of_dicts"][1]["token"] == "***FILTERED***"

        # Check mixed list
        assert result["mixed_list"][0]["api_key"] == "***FILTERED***"
        assert result["mixed_list"][1] == "normal_string"
        assert result["mixed_list"][2]["normal_key"] == "value"

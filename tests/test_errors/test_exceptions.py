"""Tests for exceptions."""

import pytest
from earnbase_common.errors.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InternalError,
    NotFoundError,
    ValidationError,
)


@pytest.mark.unit
@pytest.mark.errors
class TestExceptions:
    """Test exceptions."""

    def test_api_error(self):
        """Test APIError."""
        error = APIError(
            message="Test error",
            code="TEST_ERROR",
            status_code=418,
            details={"test": "details"},
        )
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.status_code == 418
        assert error.details == {"test": "details"}

    def test_authentication_error(self):
        """Test AuthenticationError."""
        # Test with default values
        error = AuthenticationError()
        assert error.message == "Authentication failed"
        assert error.code == "AUTHENTICATION_ERROR"
        assert error.status_code == 401
        assert error.details == {}

        # Test with custom values
        error = AuthenticationError(
            message="Invalid token",
            code="INVALID_TOKEN",
            details={"token": "expired"},
        )
        assert error.message == "Invalid token"
        assert error.code == "INVALID_TOKEN"
        assert error.status_code == 401
        assert error.details == {"token": "expired"}

    def test_authorization_error(self):
        """Test AuthorizationError."""
        # Test with default values
        error = AuthorizationError()
        assert error.message == "Permission denied"
        assert error.code == "AUTHORIZATION_ERROR"
        assert error.status_code == 403
        assert error.details == {}

        # Test with custom values
        error = AuthorizationError(
            message="Insufficient permissions",
            code="INSUFFICIENT_PERMISSIONS",
            details={"required": ["admin"]},
        )
        assert error.message == "Insufficient permissions"
        assert error.code == "INSUFFICIENT_PERMISSIONS"
        assert error.status_code == 403
        assert error.details == {"required": ["admin"]}

    def test_validation_error(self):
        """Test ValidationError."""
        # Test with default values
        error = ValidationError()
        assert error.message == "Validation failed"
        assert error.code == "VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.details == {}

        # Test with custom values
        error = ValidationError(
            message="Invalid input",
            code="INVALID_INPUT",
            details={"field": "email", "error": "invalid format"},
        )
        assert error.message == "Invalid input"
        assert error.code == "INVALID_INPUT"
        assert error.status_code == 400
        assert error.details == {"field": "email", "error": "invalid format"}

    def test_not_found_error(self):
        """Test NotFoundError."""
        # Test with default values
        error = NotFoundError()
        assert error.message == "Resource not found"
        assert error.code == "NOT_FOUND"
        assert error.status_code == 404
        assert error.details == {}

        # Test with custom values
        error = NotFoundError(
            message="User not found",
            code="USER_NOT_FOUND",
            details={"user_id": "123"},
        )
        assert error.message == "User not found"
        assert error.code == "USER_NOT_FOUND"
        assert error.status_code == 404
        assert error.details == {"user_id": "123"}

    def test_conflict_error(self):
        """Test ConflictError."""
        # Test with default values
        error = ConflictError()
        assert error.message == "Resource conflict"
        assert error.code == "CONFLICT"
        assert error.status_code == 409
        assert error.details == {}

        # Test with custom values
        error = ConflictError(
            message="Email already exists",
            code="EMAIL_EXISTS",
            details={"email": "test@example.com"},
        )
        assert error.message == "Email already exists"
        assert error.code == "EMAIL_EXISTS"
        assert error.status_code == 409
        assert error.details == {"email": "test@example.com"}

    def test_internal_error(self):
        """Test InternalError."""
        # Test with default values
        error = InternalError()
        assert error.message == "Internal server error"
        assert error.code == "INTERNAL_ERROR"
        assert error.status_code == 500
        assert error.details == {}

        # Test with custom values
        error = InternalError(
            message="Database connection failed",
            code="DB_ERROR",
            details={"error": "connection timeout"},
        )
        assert error.message == "Database connection failed"
        assert error.code == "DB_ERROR"
        assert error.status_code == 500
        assert error.details == {"error": "connection timeout"}

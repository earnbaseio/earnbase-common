"""Tests for error response model."""

import pytest
from earnbase_common.responses import ErrorResponse


@pytest.mark.unit
@pytest.mark.responses
class TestErrorResponse:
    """Test ErrorResponse."""

    def test_error_response_creation(self):
        """Test creating error response."""
        # Test minimal response
        response = ErrorResponse(
            success=False,
            error="Something went wrong",
            message="Something went wrong",
            code="ERR_001",
            details=None,
            errors=None,
        )
        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.details is None
        assert response.errors is None

        # Test with details
        details = {"field": "username", "code": "invalid"}
        response = ErrorResponse(
            success=False,
            error="Validation failed",
            message="Validation failed",
            code="ERR_001",
            details=details,
            errors=None,
        )
        assert response.error == "Validation failed"
        assert response.details == details
        assert response.errors is None

        # Test with multiple errors
        errors = [
            {"field": "username", "message": "Required"},
            {"field": "email", "message": "Invalid format"},
        ]
        response = ErrorResponse(
            success=False,
            error="Multiple validation errors",
            message="Multiple validation errors",
            code="ERR_001",
            details=None,
            errors=errors,
        )
        assert response.error == "Multiple validation errors"
        assert response.errors == errors

    def test_error_response_immutable_success(self):
        """Test success field is always False."""
        # Cannot set success to True
        response = ErrorResponse(
            success=False,
            error="Error",
            message="Error",
            code="ERR_001",
            details=None,
            errors=None,
        )
        assert response.success is False

        # Cannot modify success after creation
        with pytest.raises(TypeError):
            response.success = True

    def test_error_response_validation(self):
        """Test error response validation."""
        # error is required
        with pytest.raises(ValueError):
            ErrorResponse(
                success=False,
                message="Error message",
                code="ERR_001",
                details=None,
                errors=None,
                error="",
            )

        # details and errors are optional
        response = ErrorResponse(
            success=False,
            error="Error message",
            message="Error message",
            code="ERR_001",
            details=None,
            errors=None,
        )
        assert response.dict() == {
            "success": False,
            "error": "Error message",
            "details": None,
            "errors": None,
            "message": "Error message",
            "code": "ERR_001",
        }

    def test_error_response_with_code(self):
        """Test error response with code."""
        details = {"field": "id", "code": "not_found"}
        errors = [
            {"field": "name", "message": "Required"},
            {"field": "age", "message": "Must be positive"},
        ]
        response = ErrorResponse(
            success=False,
            error="Not found",
            code="ERR_404",
            message="Resource not found",
            details=details,
            errors=errors,
        )
        assert response.error == "Not found"
        assert response.code == "ERR_404"
        assert response.message == "Resource not found"
        assert response.details == details
        assert response.errors == errors

    def test_error_response_serialization(self):
        """Test error response serialization."""
        details = {"field": "id", "code": "not_found"}
        errors = [
            {"field": "name", "message": "Required"},
            {"field": "age", "message": "Must be positive"},
        ]
        response = ErrorResponse(
            success=False,
            error="Validation failed",
            message="Multiple validation errors",
            code="ERR_400",
            details=details,
            errors=errors,
        )

        # Test dict serialization
        data = response.dict()
        assert isinstance(data, dict)
        assert data["success"] is False
        assert data["error"] == "Validation failed"
        assert data["details"] == details
        assert data["errors"] == errors
        assert data["code"] == "ERR_400"
        assert data["message"] == "Multiple validation errors"

        # Test JSON serialization
        json_str = response.json()
        assert isinstance(json_str, str)
        assert '"success": false' in json_str
        assert '"error": "Validation failed"' in json_str
        assert '"details":' in json_str
        assert '"errors":' in json_str

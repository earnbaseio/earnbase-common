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
        response = ErrorResponse(error="Something went wrong")
        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.details is None
        assert response.errors is None

        # Test with details
        details = {"field": "username", "code": "invalid"}
        response = ErrorResponse(error="Validation failed", details=details)
        assert response.error == "Validation failed"
        assert response.details == details

        # Test with multiple errors
        errors = [
            {"field": "username", "message": "Required"},
            {"field": "email", "message": "Invalid format"},
        ]
        response = ErrorResponse(error="Multiple validation errors", errors=errors)
        assert response.error == "Multiple validation errors"
        assert response.errors == errors

    def test_error_response_immutable_success(self):
        """Test success field is always False."""
        # Cannot set success to True
        response = ErrorResponse(error="Error", success=True)
        assert response.success is False

        # Cannot modify success after creation
        with pytest.raises(TypeError):
            response.success = True

    def test_error_response_validation(self):
        """Test error response validation."""
        # error is required
        with pytest.raises(ValueError):
            ErrorResponse()

        # details and errors are optional
        response = ErrorResponse(error="Error message")
        assert response.dict() == {
            "success": False,
            "error": "Error message",
            "details": None,
            "errors": None,
            "message": None,
            "code": None,
        }

    def test_error_response_with_code(self):
        """Test error response with code."""
        response = ErrorResponse(
            error="Not found", code="ERR_404", message="Resource not found"
        )
        assert response.error == "Not found"
        assert response.code == "ERR_404"
        assert response.message == "Resource not found"

    def test_error_response_serialization(self):
        """Test error response serialization."""
        details = {"field": "id", "code": "not_found"}
        errors = [
            {"field": "name", "message": "Required"},
            {"field": "age", "message": "Must be positive"},
        ]
        response = ErrorResponse(
            error="Validation failed",
            details=details,
            errors=errors,
            code="ERR_400",
            message="Multiple validation errors",
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

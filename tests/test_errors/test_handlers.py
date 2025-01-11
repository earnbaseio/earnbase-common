"""Tests for error handlers."""

import json
from unittest.mock import MagicMock

import pytest
from earnbase_common.errors.exceptions import APIError, ValidationError
from earnbase_common.errors.handlers import (
    api_error_handler,
    create_error_response,
    register_error_handlers,
    validation_error_handler,
)
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError


@pytest.mark.unit
@pytest.mark.errors
class TestErrorHandlers:
    """Test error handlers."""

    def test_create_error_response(self):
        """Test create error response."""
        error = APIError(message="Test error", code="TEST_ERROR", status_code=400)
        response = create_error_response(
            status_code=error.status_code,
            message=error.message,
            code=error.code,
            details=error.details,
        )

        assert isinstance(response, dict)
        assert response["error"]["code"] == error.code
        assert response["error"]["message"] == error.message

    @pytest.mark.asyncio
    async def test_api_error_handler_with_api_error(self):
        """Test API error handler with API error."""
        error = APIError(message="Test error", code="TEST_ERROR", status_code=400)
        request = MagicMock()
        request.state.request_id = "test-id"
        response = await api_error_handler(request, error)

        assert response.status_code == error.status_code
        data = json.loads(response.body)
        assert data["error"]["code"] == error.code
        assert data["error"]["message"] == error.message

    @pytest.mark.asyncio
    async def test_api_error_handler_with_generic_error(self):
        """Test API error handler with generic error."""
        error = Exception("Test error")
        request = MagicMock()
        request.state.request_id = "test-id"
        response = await api_error_handler(request, error)

        assert response.status_code == 500
        data = json.loads(response.body)
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert data["error"]["message"] == str(error)

    @pytest.mark.asyncio
    async def test_validation_error_handler_with_pydantic_error(self):
        """Test validation error handler with Pydantic validation error."""

        class TestModel(BaseModel):
            name: str
            age: int

        try:
            TestModel.model_validate({"name": 123, "age": "invalid"})
        except PydanticValidationError as error:
            request = MagicMock()
            request.state.request_id = "test-id"
            response = await validation_error_handler(request, error)

            assert response.status_code == 400
            data = json.loads(response.body)
            assert data["error"]["code"] == "VALIDATION_ERROR"
            assert data["error"]["message"] == "Validation failed"
            assert "fields" in data["error"]["details"]

    @pytest.mark.asyncio
    async def test_validation_error_handler_with_other_error(self):
        """Test validation error handler with other validation error."""
        error = ValidationError(message="Test error")
        request = MagicMock()
        request.state.request_id = "test-id"
        response = await validation_error_handler(request, error)

        assert response.status_code == error.status_code
        data = json.loads(response.body)
        assert data["error"]["code"] == error.code
        assert data["error"]["message"] == error.message

    def test_register_error_handlers(self):
        """Test register error handlers."""
        app = MagicMock()
        register_error_handlers(app)

        app.add_exception_handler.assert_any_call(APIError, api_error_handler)
        app.add_exception_handler.assert_any_call(Exception, api_error_handler)
        app.add_exception_handler.assert_any_call(
            PydanticValidationError, validation_error_handler
        )
        app.add_exception_handler.assert_any_call(ValidationError, api_error_handler)

"""Tests for base response models."""

import pytest
from earnbase_common.responses import BaseResponse, SuccessResponse


@pytest.mark.unit
@pytest.mark.responses
class TestBaseResponse:
    """Test BaseResponse."""

    def test_base_response_creation(self):
        """Test creating base response."""
        # Test minimal response
        response = BaseResponse(success=True)
        assert response.success is True
        assert response.message is None
        assert response.code is None

        # Test full response
        response = BaseResponse(
            success=False, message="Operation failed", code="ERR_001"
        )
        assert response.success is False
        assert response.message == "Operation failed"
        assert response.code == "ERR_001"

    def test_base_response_validation(self):
        """Test base response validation."""
        # success is required
        with pytest.raises(ValueError):
            BaseResponse()

        # message and code are optional
        response = BaseResponse(success=True)
        assert response.dict() == {"success": True, "message": None, "code": None}

    def test_base_response_serialization(self):
        """Test base response serialization."""
        response = BaseResponse(success=True, message="Success", code="OK_001")

        # Test dict serialization
        data = response.dict()
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["message"] == "Success"
        assert data["code"] == "OK_001"

        # Test JSON serialization
        json_str = response.json()
        assert isinstance(json_str, str)
        assert '"success": true' in json_str
        assert '"message": "Success"' in json_str
        assert '"code": "OK_001"' in json_str


@pytest.mark.unit
@pytest.mark.responses
class TestSuccessResponse:
    """Test SuccessResponse."""

    def test_success_response_creation(self):
        """Test creating success response."""
        # Test minimal response
        response = SuccessResponse()
        assert response.success is True
        assert response.data is None
        assert response.meta is None
        assert response.message is None
        assert response.code is None

        # Test with data
        data = {"id": 1, "name": "Test"}
        response = SuccessResponse(data=data)
        assert response.success is True
        assert response.data == data

        # Test with metadata
        meta = {"total": 100, "page": 1}
        response = SuccessResponse(data=data, meta=meta)
        assert response.meta == meta

    def test_success_response_immutable_success(self):
        """Test success field is always True."""
        # Cannot set success to False
        response = SuccessResponse(success=False)
        assert response.success is True

        # Cannot modify success after creation
        with pytest.raises(TypeError):
            response.success = False

    def test_success_response_with_message(self):
        """Test success response with message."""
        response = SuccessResponse(
            message="Operation completed", code="OK_001", data={"status": "done"}
        )
        assert response.message == "Operation completed"
        assert response.code == "OK_001"
        assert response.data == {"status": "done"}

    def test_success_response_serialization(self):
        """Test success response serialization."""
        data = {"id": 1, "name": "Test"}
        meta = {"total": 100}
        response = SuccessResponse(
            data=data, meta=meta, message="Success", code="OK_001"
        )

        # Test dict serialization
        result = response.dict()
        assert result["success"] is True
        assert result["data"] == data
        assert result["meta"] == meta
        assert result["message"] == "Success"
        assert result["code"] == "OK_001"

        # Test JSON serialization
        json_str = response.json()
        assert isinstance(json_str, str)
        assert '"success": true' in json_str
        assert '"data":' in json_str
        assert '"meta":' in json_str

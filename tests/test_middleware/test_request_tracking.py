"""Tests for request tracking middleware."""

import re
import time
from unittest.mock import patch

import pytest
from earnbase_common.middleware import RequestTrackingMiddleware
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


@pytest.mark.unit
@pytest.mark.middleware
class TestRequestTrackingMiddleware:
    """Test RequestTrackingMiddleware."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        app.add_middleware(RequestTrackingMiddleware)

        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        @app.get("/with-request")
        def test_with_request(request: Request):
            return {
                "request_id": request.state.request_id,
                "start_time": request.state.start_time,
            }

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_request_id_added(self, client):
        """Test request ID is added to response headers."""
        response = client.get("/test")
        assert response.status_code == 200

        # Check request ID header
        request_id = response.headers.get("X-Request-ID")
        assert request_id is not None
        # Should be a valid UUID
        assert re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            request_id,
        )

    def test_request_state_populated(self, client):
        """Test request state is populated."""
        response = client.get("/with-request")
        assert response.status_code == 200
        data = response.json()

        # Check request ID and start time are set
        assert "request_id" in data
        assert "start_time" in data
        assert isinstance(data["start_time"], float)

    @patch("earnbase_common.middleware.request_tracking.logger")
    def test_request_logging(self, mock_logger, client):
        """Test request details are logged."""
        response = client.get("/test", headers={"User-Agent": "test-agent"})
        assert response.status_code == 200

        # Verify logger was called with correct info
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert call_args[0][0] == "request_processed"

        log_data = call_args[1]["extra"]
        assert "request_id" in log_data
        assert log_data["method"] == "GET"
        assert log_data["url"].endswith("/test")
        assert log_data["status_code"] == 200
        assert isinstance(log_data["duration"], float)
        assert log_data["user_agent"] == "test-agent"

    def test_request_timing(self, client):
        """Test request timing calculation."""
        start_time = time.time()
        response = client.get("/with-request")
        end_time = time.time()

        data = response.json()
        request_start_time = data["start_time"]

        # Request start time should be between our measurements
        assert start_time <= request_start_time <= end_time

    def test_multiple_requests(self, client):
        """Test handling multiple requests."""
        # Make multiple requests and collect request IDs
        request_ids = set()
        for _ in range(5):
            response = client.get("/test")
            request_ids.add(response.headers["X-Request-ID"])

        # Each request should have unique ID
        assert len(request_ids) == 5

    def test_error_response_tracking(self, client):
        """Test request tracking for error responses."""
        with patch("earnbase_common.middleware.request_tracking.logger") as mock_logger:
            response = client.get("/nonexistent")
            assert response.status_code == 404

            # Should still log request
            mock_logger.info.assert_called_once()
            log_data = mock_logger.info.call_args[1]["extra"]
            assert log_data["status_code"] == 404

    def test_request_tracking_with_different_methods(self, app, client):
        """Test request tracking with different HTTP methods."""

        @app.post("/test")
        def test_post():
            return {"message": "post"}

        with patch("earnbase_common.middleware.request_tracking.logger") as mock_logger:
            # Test POST request
            response = client.post("/test")
            assert response.status_code == 200

            # Verify logged with correct method
            log_data = mock_logger.info.call_args[1]["extra"]
            assert log_data["method"] == "POST"

    def test_client_info_logging(self, client):
        """Test client information logging."""
        with patch("earnbase_common.middleware.request_tracking.logger") as mock_logger:
            response = client.get(
                "/test",
                headers={
                    "User-Agent": "test-browser",
                    "X-Forwarded-For": "203.0.113.195",
                },
            )
            assert response.status_code == 200

            # Check client info in logs
            log_data = mock_logger.info.call_args[1]["extra"]
            assert log_data["user_agent"] == "test-browser"
            assert log_data["client_host"] is not None

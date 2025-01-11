"""Tests for security headers middleware."""

import pytest
from earnbase_common.middleware import SecurityHeadersMiddleware
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient


@pytest.mark.unit
@pytest.mark.middleware
class TestSecurityHeadersMiddleware:
    """Test SecurityHeadersMiddleware."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_security_headers_added(self, client):
        """Test security headers are added to response."""
        response = client.get("/test")
        assert response.status_code == 200

        # Check all security headers are present
        headers = response.headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-XSS-Protection"] == "1; mode=block"
        assert (
            headers["Strict-Transport-Security"]
            == "max-age=31536000; includeSubDomains"
        )

        # Check Content-Security-Policy
        csp = headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "img-src 'self' data: https://fastapi.tiangolo.com" in csp
        assert "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net" in csp
        assert (
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net"
            in csp
        )
        assert "connect-src 'self'" in csp

    def test_security_headers_with_error_response(self, client):
        """Test security headers are added even for error responses."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

        # Headers should still be present
        headers = response.headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-XSS-Protection"] == "1; mode=block"

    def test_security_headers_with_custom_response(self, app, client):
        """Test security headers with custom response."""

        @app.get("/custom")
        def custom_response():
            response = Response(content="Custom response")
            response.headers["Custom-Header"] = "test"
            return response

        response = client.get("/custom")
        assert response.status_code == 200

        # Custom headers should be preserved
        assert response.headers["Custom-Header"] == "test"

        # Security headers should be added
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_security_headers_with_different_methods(self, app, client):
        """Test security headers with different HTTP methods."""

        @app.post("/test")
        def test_post():
            return {"message": "post"}

        @app.put("/test")
        def test_put():
            return {"message": "put"}

        # Test POST
        response = client.post("/test")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        # Test PUT
        response = client.put("/test")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_security_headers_order(self, client):
        """Test security headers are added in consistent order."""
        response1 = client.get("/test")
        response2 = client.get("/test")

        # Headers should be present in same order
        headers1 = list(response1.headers.items())
        headers2 = list(response2.headers.items())

        # Find indices of security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
        ]
        indices1 = [i for i, (k, _) in enumerate(headers1) if k in security_headers]
        indices2 = [i for i, (k, _) in enumerate(headers2) if k in security_headers]

        assert indices1 == indices2  # Order should be consistent

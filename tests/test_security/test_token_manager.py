"""Tests for TokenManager."""

from datetime import datetime, timedelta

import pytest
from earnbase_common.errors import ValidationError
from earnbase_common.security import JWTConfig, TokenManager
from earnbase_common.value_objects import Token


@pytest.mark.unit
@pytest.mark.security
class TestTokenManager:
    """Test TokenManager."""

    @pytest.fixture
    def sample_token_data(self):
        """Create sample token data."""
        return {"user_id": "test-123", "username": "testuser", "roles": ["user"]}

    def test_token_creation(self, token_manager, sample_token_data, mock_datetime):
        """Test creating tokens."""
        # Test access token
        access_token = token_manager.create_token(
            data=sample_token_data, token_type="access"
        )
        assert isinstance(access_token, Token)
        assert access_token.token_type == "access"
        assert access_token.expires_at == mock_datetime + timedelta(minutes=30)
        assert not access_token.is_expired()

        # Test refresh token
        refresh_token = token_manager.create_token(
            data=sample_token_data, token_type="refresh"
        )
        assert isinstance(refresh_token, Token)
        assert refresh_token.token_type == "refresh"
        assert refresh_token.expires_at == mock_datetime + timedelta(days=7)
        assert not refresh_token.is_expired()

    def test_token_verification(self, token_manager, sample_token_data):
        """Test verifying tokens."""
        # Create and verify access token
        access_token = token_manager.create_token(
            data=sample_token_data, token_type="access"
        )
        payload = token_manager.verify_token(
            token=access_token.value, expected_type="access"
        )
        assert payload["user_id"] == sample_token_data["user_id"]
        assert payload["username"] == sample_token_data["username"]
        assert payload["roles"] == sample_token_data["roles"]
        assert payload["type"] == "access"

    def test_token_expiration(self, token_manager, sample_token_data, mock_datetime):
        """Test token expiration."""
        # Create token with custom expiry
        token = token_manager.create_token(
            data=sample_token_data,
            token_type="access",
            expires_delta=timedelta(minutes=-1),  # Expired token
        )

        # Verify should fail for expired token
        with pytest.raises(ValidationError) as exc:
            token_manager.verify_token(token.value)
        assert "expired" in str(exc.value).lower()

    def test_invalid_token_type(self, token_manager, sample_token_data):
        """Test invalid token type handling."""
        # Create token with invalid type
        with pytest.raises(ValidationError) as exc:
            token_manager.create_token(data=sample_token_data, token_type="invalid")
        assert "Invalid token type" in str(exc.value)

    def test_token_type_verification(self, token_manager, sample_token_data):
        """Test token type verification."""
        # Create access token
        access_token = token_manager.create_token(
            data=sample_token_data, token_type="access"
        )

        # Verify with wrong type should fail
        with pytest.raises(ValidationError) as exc:
            token_manager.verify_token(
                token=access_token.value, expected_type="refresh"
            )
        assert "Invalid token type" in str(exc.value)

    def test_invalid_token_format(self, token_manager):
        """Test invalid token format handling."""
        invalid_tokens = [
            "",  # Empty token
            "invalid-token",  # Non-JWT format
            "header.payload",  # Missing signature
            "header.payload.invalid",  # Invalid signature
        ]

        for token in invalid_tokens:
            with pytest.raises(ValidationError) as exc:
                token_manager.verify_token(token)
            assert "Invalid token" in str(exc.value)

    def test_custom_jwt_config(self, sample_token_data):
        """Test custom JWT configuration."""
        custom_config = JWTConfig(
            secret_key="custom-secret",
            algorithm="HS512",
            access_token_expire_minutes=15,
            refresh_token_expire_days=14,
        )
        custom_manager = TokenManager(config=custom_config)

        # Create token with custom config
        token = custom_manager.create_token(data=sample_token_data, token_type="access")

        # Verify token with same config should succeed
        payload = custom_manager.verify_token(token.value)
        assert payload["user_id"] == sample_token_data["user_id"]

        # Verify token with different config should fail
        different_manager = TokenManager(
            config=JWTConfig(secret_key="different-secret")
        )
        with pytest.raises(ValidationError):
            different_manager.verify_token(token.value)

    def test_token_metadata(self, token_manager, sample_token_data):
        """Test token metadata handling."""
        metadata = {"device": "mobile", "ip": "127.0.0.1"}
        token = token_manager.create_token(
            data={**sample_token_data, **metadata}, token_type="access"
        )

        payload = token_manager.verify_token(token.value)
        assert payload["device"] == metadata["device"]
        assert payload["ip"] == metadata["ip"]

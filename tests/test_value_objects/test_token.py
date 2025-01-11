"""Tests for Token value object."""

from datetime import datetime, timedelta

import pytest
from earnbase_common.value_objects import Token


@pytest.mark.unit
@pytest.mark.value_objects
class TestToken:
    """Test Token value object."""

    @pytest.fixture
    def sample_token(self, mock_datetime):
        """Create sample token."""
        return Token(
            value="test-token-value",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type="access",
            metadata={"user_id": "123"},
        )

    def test_token_creation(self, sample_token, mock_datetime):
        """Test creating token."""
        assert isinstance(sample_token, Token)
        assert sample_token.value == "test-token-value"
        assert sample_token.expires_at == mock_datetime + timedelta(minutes=30)
        assert sample_token.token_type == "access"
        assert sample_token.metadata == {"user_id": "123"}

    def test_token_expiration(self, mock_datetime):
        """Test token expiration check."""
        # Create expired token
        expired_token = Token(
            value="expired-token",
            expires_at=mock_datetime - timedelta(minutes=1),
            token_type="access",
        )
        assert expired_token.is_expired()

        # Create valid token
        valid_token = Token(
            value="valid-token",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type="access",
        )
        assert not valid_token.is_expired()

    def test_token_string_representation(self, sample_token):
        """Test token string representation."""
        token_str = str(sample_token)
        assert "access token" in token_str
        assert "expires" in token_str

    def test_token_comparison(self, mock_datetime):
        """Test token comparison."""
        token1 = Token(
            value="token1",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type="access",
        )
        token2 = Token(
            value="token1",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type="access",
        )
        token3 = Token(
            value="token3",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type="access",
        )

        assert token1 == token2
        assert token1 != token3
        assert hash(token1) == hash(token2)
        assert hash(token1) != hash(token3)

    def test_token_immutability(self, sample_token):
        """Test that token attributes cannot be changed after creation."""
        with pytest.raises(AttributeError):
            sample_token.value = "new-value"
        with pytest.raises(AttributeError):
            sample_token.expires_at = datetime.utcnow()
        with pytest.raises(AttributeError):
            sample_token.token_type = "refresh"
        with pytest.raises(AttributeError):
            sample_token.metadata = {}

    @pytest.mark.parametrize(
        "token_type", ["access", "refresh", "verification", "reset"]
    )
    def test_valid_token_types(self, token_type, mock_datetime):
        """Test creating tokens with different valid types."""
        token = Token(
            value=f"{token_type}-token",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type=token_type,
        )
        assert token.token_type == token_type

    def test_optional_metadata(self, mock_datetime):
        """Test token creation with optional metadata."""
        # Without metadata
        token1 = Token(
            value="token1",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type="access",
        )
        assert token1.metadata is None

        # With metadata
        metadata = {"user_id": "123", "roles": ["admin"]}
        token2 = Token(
            value="token2",
            expires_at=mock_datetime + timedelta(minutes=30),
            token_type="access",
            metadata=metadata,
        )
        assert token2.metadata == metadata

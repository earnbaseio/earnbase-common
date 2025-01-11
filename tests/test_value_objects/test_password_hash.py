"""Tests for PasswordHash value object."""

import pytest
from earnbase_common.value_objects import PasswordHash


@pytest.mark.unit
@pytest.mark.value_objects
class TestPasswordHash:
    """Test PasswordHash value object."""

    @pytest.fixture
    def sample_hash(self):
        """Create sample password hash."""
        return PasswordHash(value="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY")

    def test_password_hash_creation(self, sample_hash):
        """Test creating password hash."""
        assert isinstance(sample_hash, PasswordHash)
        assert sample_hash.value == "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY"

    def test_password_hash_string_masking(self, sample_hash):
        """Test that password hash is masked in string representation."""
        assert str(sample_hash) == "********"
        assert repr(sample_hash) != sample_hash.value
        assert "********" in repr(sample_hash)

    def test_password_hash_comparison(self):
        """Test password hash comparison."""
        hash1 = PasswordHash(value="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY")
        hash2 = PasswordHash(value="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY")
        hash3 = PasswordHash(value="$2b$12$DifferentHashValue123456789")

        assert hash1 == hash2
        assert hash1 != hash3
        assert hash(hash1) == hash(hash2)
        assert hash(hash1) != hash(hash3)

    def test_password_hash_immutability(self, sample_hash):
        """Test that password hash value cannot be changed after creation."""
        with pytest.raises(AttributeError):
            sample_hash.value = "$2b$12$NewHashValue123456789"

    def test_empty_password_hash(self):
        """Test that empty password hash is not allowed."""
        with pytest.raises(ValueError):
            PasswordHash(value="")

"""Tests for password utilities."""

import pytest
from earnbase_common.security import hash_password, verify_password


@pytest.mark.unit
@pytest.mark.security
class TestPassword:
    """Test password utilities."""

    @pytest.fixture
    def sample_password(self):
        """Create sample password."""
        return "MySecurePassword123!"

    def test_password_hashing(self, sample_password):
        """Test password hashing."""
        # Hash should be different from original password
        hashed = hash_password(sample_password)
        assert hashed != sample_password
        assert len(hashed) > 0

        # Multiple hashes of same password should be different
        hashed2 = hash_password(sample_password)
        assert hashed != hashed2  # Different salts

    def test_password_verification(self, sample_password):
        """Test password verification."""
        hashed = hash_password(sample_password)

        # Correct password should verify
        assert verify_password(sample_password, hashed)

        # Wrong password should not verify
        assert not verify_password("WrongPassword123!", hashed)

    def test_empty_password(self):
        """Test empty password handling."""
        with pytest.raises(ValueError):
            hash_password("")

        with pytest.raises(ValueError):
            verify_password("", "some-hash")

    def test_invalid_hash_format(self, sample_password):
        """Test invalid hash format handling."""
        invalid_hashes = [
            "",  # Empty hash
            "invalid-hash",  # Non-bcrypt format
            "$2b$",  # Incomplete format
            "not-a-hash-at-all",  # Random string
        ]

        for invalid_hash in invalid_hashes:
            assert not verify_password(sample_password, invalid_hash)

    def test_password_encoding(self):
        """Test password encoding handling."""
        password = "Password123!@#"

        # Test with different string types
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    @pytest.mark.parametrize(
        "password",
        [
            "SimplePass123!",
            "Complex@Pass#456",
            "VeryLongPassword123!@#",
            "Short1!",
            "12345678!@#$%^&*()",
            "абвгд123!@#",  # Non-ASCII characters
        ],
    )
    def test_various_password_formats(self, password):
        """Test hashing and verification with various password formats."""
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_hash_consistency(self, sample_password):
        """Test hash consistency across multiple verifications."""
        hashed = hash_password(sample_password)

        # Multiple verifications should give same result
        for _ in range(5):
            assert verify_password(sample_password, hashed)

    def test_timing_attack_resistance(self):
        """Test timing attack resistance."""
        import time

        password = "MySecurePassword123!"
        hashed = hash_password(password)

        # Measure time for correct password
        start = time.perf_counter()
        verify_password(password, hashed)
        correct_time = time.perf_counter() - start

        # Measure time for wrong password of same length
        start = time.perf_counter()
        verify_password("DifferentPass123!", hashed)
        wrong_time = time.perf_counter() - start

        # Times should be similar (within reasonable margin)
        assert abs(correct_time - wrong_time) < 0.1

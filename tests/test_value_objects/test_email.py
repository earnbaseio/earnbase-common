"""Tests for Email value object."""

import pytest
from earnbase_common.errors import ValidationError
from earnbase_common.value_objects import Email


@pytest.mark.unit
@pytest.mark.value_objects
class TestEmail:
    """Test Email value object."""

    def test_valid_email_creation(self, sample_email):
        """Test creating email with valid format."""
        assert isinstance(sample_email, Email)
        assert sample_email.value == "test@example.com"
        assert str(sample_email) == "test@example.com"

    def test_invalid_email_format(self):
        """Test creating email with invalid format."""
        invalid_emails = [
            "",  # Empty
            "invalid",  # No @ symbol
            "@nodomain",  # No local part
            "no@tld",  # No TLD
            "spaces in@email.com",  # Spaces in local part
            "multiple@@at.com",  # Multiple @ symbols
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError) as exc:
                Email(value=email)
            assert "Invalid email format" in str(exc.value)

    @pytest.mark.parametrize(
        "email_str",
        [
            "user@example.com",
            "user.name@example.co.uk",
            "user+tag@example.com",
            "12345@example.com",
            "user@subdomain.example.com",
        ],
    )
    def test_valid_email_formats(self, email_str):
        """Test various valid email formats."""
        email = Email(value=email_str)
        assert isinstance(email, Email)
        assert email.value == email_str
        assert str(email) == email_str

    def test_email_immutability(self, sample_email):
        """Test that email value cannot be changed after creation."""
        with pytest.raises(AttributeError):
            sample_email.value = "new@example.com"

    def test_email_comparison(self):
        """Test email comparison."""
        email1 = Email(value="test@example.com")
        email2 = Email(value="test@example.com")
        email3 = Email(value="different@example.com")

        assert email1 == email2
        assert email1 != email3
        assert hash(email1) == hash(email2)
        assert hash(email1) != hash(email3)

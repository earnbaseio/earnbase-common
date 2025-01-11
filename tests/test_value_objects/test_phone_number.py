"""Tests for PhoneNumber value object."""

import pytest
from earnbase_common.errors import ValidationError
from earnbase_common.value_objects import PhoneNumber


@pytest.mark.unit
@pytest.mark.value_objects
class TestPhoneNumber:
    """Test PhoneNumber value object."""

    def test_valid_phone_creation(self, sample_phone):
        """Test creating phone number with valid format."""
        assert isinstance(sample_phone, PhoneNumber)
        assert sample_phone.value == "1234567890"
        assert sample_phone.country_code == "1"
        assert str(sample_phone) == "+11234567890"

    def test_invalid_phone_format(self):
        """Test creating phone number with invalid format."""
        invalid_phones = [
            ("", "1"),  # Empty number
            ("123", "1"),  # Too short
            ("12345678901234567", "1"),  # Too long
            ("abcd1234567", "1"),  # Contains letters
            ("123 456 7890", "1"),  # Contains spaces
            ("1234567890", ""),  # Empty country code
            ("1234567890", "123"),  # Invalid country code
        ]

        for number, country_code in invalid_phones:
            with pytest.raises(ValidationError) as exc:
                PhoneNumber(value=number, country_code=country_code)
            assert "Invalid phone" in str(exc.value)

    @pytest.mark.parametrize(
        "number,country_code,expected",
        [
            ("1234567890", "1", "+11234567890"),
            ("9876543210", "44", "+449876543210"),
            ("5555555555", "81", "+815555555555"),
            ("9999999999", "86", "+869999999999"),
        ],
    )
    def test_valid_phone_formats(self, number, country_code, expected):
        """Test various valid phone number formats."""
        phone = PhoneNumber(value=number, country_code=country_code)
        assert isinstance(phone, PhoneNumber)
        assert phone.value == number
        assert phone.country_code == country_code
        assert str(phone) == expected

    def test_phone_immutability(self, sample_phone):
        """Test that phone number attributes cannot be changed after creation."""
        with pytest.raises(AttributeError):
            sample_phone.value = "9876543210"
        with pytest.raises(AttributeError):
            sample_phone.country_code = "44"

    def test_phone_comparison(self):
        """Test phone number comparison."""
        phone1 = PhoneNumber(value="1234567890", country_code="1")
        phone2 = PhoneNumber(value="1234567890", country_code="1")
        phone3 = PhoneNumber(value="9876543210", country_code="1")
        phone4 = PhoneNumber(value="1234567890", country_code="44")

        assert phone1 == phone2
        assert phone1 != phone3
        assert phone1 != phone4
        assert hash(phone1) == hash(phone2)
        assert hash(phone1) != hash(phone3)
        assert hash(phone1) != hash(phone4)

    def test_phone_validation_rules(self):
        """Test specific validation rules for phone numbers."""
        # Test minimum length
        with pytest.raises(ValidationError):
            PhoneNumber(value="12345", country_code="1")

        # Test maximum length
        with pytest.raises(ValidationError):
            PhoneNumber(value="12345678901234567", country_code="1")

        # Test numeric only
        with pytest.raises(ValidationError):
            PhoneNumber(value="123abc4567", country_code="1")

        # Test country code format
        with pytest.raises(ValidationError):
            PhoneNumber(value="1234567890", country_code="abc")

"""Tests for Address value object."""

import pytest
from earnbase_common.errors import ValidationError
from earnbase_common.value_objects import Address


@pytest.mark.unit
@pytest.mark.value_objects
class TestAddress:
    """Test Address value object."""

    def test_valid_address_creation(self, sample_address):
        """Test creating address with valid values."""
        assert isinstance(sample_address, Address)
        assert sample_address.street == "123 Test St"
        assert sample_address.city == "Test City"
        assert sample_address.state == "TC"
        assert sample_address.country == "Test Country"
        assert sample_address.postal_code == "12345"
        assert str(sample_address) == "123 Test St, Test City, TC 12345, Test Country"

    def test_invalid_address_format(self):
        """Test creating address with invalid format."""
        invalid_addresses = [
            {
                "street": "",  # Empty street
                "city": "Test City",
                "state": "TC",
                "country": "Test Country",
                "postal_code": "12345",
            },
            {
                "street": "123 Test St",
                "city": "",  # Empty city
                "state": "TC",
                "country": "Test Country",
                "postal_code": "12345",
            },
            {
                "street": "123 Test St",
                "city": "Test City",
                "state": "",  # Empty state
                "country": "Test Country",
                "postal_code": "12345",
            },
            {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TC",
                "country": "",  # Empty country
                "postal_code": "12345",
            },
            {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TC",
                "country": "Test Country",
                "postal_code": "",  # Empty postal code
            },
        ]

        for address_data in invalid_addresses:
            with pytest.raises(ValidationError) as exc:
                Address(**address_data)
            assert "field required" in str(exc.value).lower()

    @pytest.mark.parametrize(
        "address_data,expected_str",
        [
            (
                {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "country": "USA",
                    "postal_code": "10001",
                },
                "123 Main St, New York, NY 10001, USA",
            ),
            (
                {
                    "street": "10 Downing Street",
                    "city": "London",
                    "state": "England",
                    "country": "UK",
                    "postal_code": "SW1A 2AA",
                },
                "10 Downing Street, London, England SW1A 2AA, UK",
            ),
        ],
    )
    def test_valid_address_formats(self, address_data, expected_str):
        """Test various valid address formats."""
        address = Address(**address_data)
        assert isinstance(address, Address)
        for field, value in address_data.items():
            assert getattr(address, field) == value
        assert str(address) == expected_str

    def test_address_immutability(self, sample_address):
        """Test that address attributes cannot be changed after creation."""
        with pytest.raises(AttributeError):
            sample_address.street = "456 New St"
        with pytest.raises(AttributeError):
            sample_address.city = "New City"
        with pytest.raises(AttributeError):
            sample_address.state = "NC"
        with pytest.raises(AttributeError):
            sample_address.country = "New Country"
        with pytest.raises(AttributeError):
            sample_address.postal_code = "54321"

    def test_address_comparison(self):
        """Test address comparison."""
        address1 = Address(
            street="123 Test St",
            city="Test City",
            state="TC",
            country="Test Country",
            postal_code="12345",
        )
        address2 = Address(
            street="123 Test St",
            city="Test City",
            state="TC",
            country="Test Country",
            postal_code="12345",
        )
        address3 = Address(
            street="456 Other St",
            city="Other City",
            state="OC",
            country="Other Country",
            postal_code="67890",
        )

        assert address1 == address2
        assert address1 != address3
        assert hash(address1) == hash(address2)
        assert hash(address1) != hash(address3)

    def test_address_field_validation(self):
        """Test field-specific validation rules."""
        # Test maximum length validation
        long_string = "a" * 256  # Assuming max length is 255
        with pytest.raises(ValidationError):
            Address(
                street=long_string,
                city="Test City",
                state="TC",
                country="Test Country",
                postal_code="12345",
            )

        # Test postal code format (if implemented)
        with pytest.raises(ValidationError):
            Address(
                street="123 Test St",
                city="Test City",
                state="TC",
                country="Test Country",
                postal_code="invalid-postal-code",
            )

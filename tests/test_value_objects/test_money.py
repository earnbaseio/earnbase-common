"""Tests for Money value object."""

import pytest
from earnbase_common.errors import ValidationError
from earnbase_common.value_objects import Money


@pytest.mark.unit
@pytest.mark.value_objects
class TestMoney:
    """Test Money value object."""

    def test_valid_money_creation(self, sample_money):
        """Test creating money with valid values."""
        assert isinstance(sample_money, Money)
        assert sample_money.amount == 99.99
        assert sample_money.currency == "USD"
        assert str(sample_money) == "99.99 USD"

    def test_invalid_money_format(self):
        """Test creating money with invalid format."""
        invalid_money = [
            (-100, "USD"),  # Negative amount
            (0, ""),  # Empty currency
            (100, "US"),  # Invalid currency code (too short)
            (100, "USDD"),  # Invalid currency code (too long)
            (100, "123"),  # Invalid currency code (numeric)
            (100, "usd"),  # Invalid currency code (lowercase)
        ]

        for amount, currency in invalid_money:
            with pytest.raises(ValidationError) as exc:
                Money(amount=amount, currency=currency)
            assert "Invalid" in str(exc.value)

    @pytest.mark.parametrize(
        "amount,currency,expected",
        [
            (100, "USD", "100.0 USD"),
            (99.99, "EUR", "99.99 EUR"),
            (1000.50, "GBP", "1000.5 GBP"),
            (0.01, "JPY", "0.01 JPY"),
        ],
    )
    def test_valid_money_formats(self, amount, currency, expected):
        """Test various valid money formats."""
        money = Money(amount=amount, currency=currency)
        assert isinstance(money, Money)
        assert money.amount == amount
        assert money.currency == currency
        assert str(money) == expected

    def test_money_immutability(self, sample_money):
        """Test that money attributes cannot be changed after creation."""
        with pytest.raises(AttributeError):
            sample_money.amount = 200
        with pytest.raises(AttributeError):
            sample_money.currency = "EUR"

    def test_money_comparison(self):
        """Test money comparison."""
        money1 = Money(amount=100, currency="USD")
        money2 = Money(amount=100, currency="USD")
        money3 = Money(amount=200, currency="USD")
        money4 = Money(amount=100, currency="EUR")

        assert money1 == money2
        assert money1 != money3
        assert money1 != money4
        assert hash(money1) == hash(money2)
        assert hash(money1) != hash(money3)
        assert hash(money1) != hash(money4)

    def test_money_arithmetic(self):
        """Test money arithmetic operations."""
        money1 = Money(amount=100, currency="USD")
        money2 = Money(amount=50, currency="USD")
        money3 = Money(amount=100, currency="EUR")

        # Same currency operations
        assert Money(amount=150, currency="USD") == money1 + money2
        assert Money(amount=50, currency="USD") == money1 - money2
        assert Money(amount=5000, currency="USD") == money1 * 50
        assert Money(amount=20, currency="USD") == money1 / 5

        # Different currency operations should raise error
        with pytest.raises(ValueError):
            money1 + money3
        with pytest.raises(ValueError):
            money1 - money3

    def test_money_zero_division(self):
        """Test division by zero."""
        money = Money(amount=100, currency="USD")
        with pytest.raises(ZeroDivisionError):
            money / 0

    def test_money_negative_amount(self):
        """Test negative amount handling."""
        with pytest.raises(ValidationError):
            Money(amount=-100, currency="USD")

    def test_money_rounding(self):
        """Test money rounding behavior."""
        money = Money(amount=100.12345, currency="USD")
        assert money.amount == 100.12  # Should round to 2 decimal places

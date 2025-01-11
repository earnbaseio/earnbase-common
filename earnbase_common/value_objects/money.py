"""Money value object."""

import re
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class Money(BaseModel):
    """Money value object."""

    amount: Decimal
    currency: str

    model_config = ConfigDict(frozen=True)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if not re.match(r"^[A-Z]{3}$", v):
            raise ValueError("Invalid currency code")
        return v

    def __add__(self, other: "Money") -> "Money":
        """Add money values."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money objects")
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract money values."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money objects")
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.amount} {self.currency}"

    def __eq__(self, other: object) -> bool:
        """Compare money values."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        """Hash money value."""
        return hash((self.amount, self.currency))

"""Value objects module."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class Email(BaseModel):
    """Email value object."""

    value: str

    model_config = ConfigDict(frozen=True)

    @field_validator("value")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class PhoneNumber(BaseModel):
    """Phone number value object."""

    value: str
    country_code: str

    model_config = ConfigDict(frozen=True)

    @field_validator("value")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        pattern = r"^\d{10}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid phone number format")
        return v


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


class Address(BaseModel):
    """Address value object."""

    street: str
    city: str
    state: str
    country: str
    postal_code: str
    unit: Optional[str] = None

    model_config = ConfigDict(frozen=True)


class Token(BaseModel):
    """Token value object."""

    value: str
    expires_at: datetime
    token_type: str
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(frozen=True)

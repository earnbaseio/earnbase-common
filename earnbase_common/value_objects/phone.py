"""Phone number value object."""

import re

from pydantic import BaseModel, ConfigDict, field_validator


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

    def __str__(self) -> str:
        """Return string representation."""
        return f"+{self.country_code}{self.value}"

    def __eq__(self, other: object) -> bool:
        """Compare phone numbers."""
        if not isinstance(other, PhoneNumber):
            return False
        return self.value == other.value and self.country_code == other.country_code

    def __hash__(self) -> int:
        """Hash phone number value."""
        return hash((self.value, self.country_code))

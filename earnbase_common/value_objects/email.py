"""Email value object."""

import re

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

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Compare email addresses."""
        if not isinstance(other, Email):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """Hash email value."""
        return hash(self.value)

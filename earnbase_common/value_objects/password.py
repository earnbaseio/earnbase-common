"""Password hash value object."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PasswordHash(BaseModel):
    """Password hash value object."""

    value: str = Field(alias="_hash", description="Password hash value")

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        strict=True,
    )

    @model_validator(mode="before")
    @classmethod
    def validate_hash(cls, data: Any) -> Any:
        """Validate hash value."""
        value = data.get("_hash") or data.get("value")
        if not value:
            raise ValueError("Hash value cannot be empty")
        return data

    def __str__(self) -> str:
        """Return string representation."""
        return "********"

    def __repr__(self) -> str:
        """Return string representation."""
        return "PasswordHash(********)"

    def __eq__(self, other: object) -> bool:
        """Compare hash values."""
        if not isinstance(other, PasswordHash):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """Hash password hash value."""
        return hash(self.value)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to use alias."""
        kwargs["by_alias"] = True
        return super().model_dump(**kwargs)

"""Password hash value object."""

from pydantic import BaseModel, ConfigDict, field_validator


class PasswordHash(BaseModel):
    """Password hash value object."""

    _hash: str

    model_config = ConfigDict(frozen=True)

    @field_validator("_hash")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        """Validate hash value."""
        if not v:
            raise ValueError("Hash value cannot be empty")
        return v

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
        return self._hash == other._hash

    def __hash__(self) -> int:
        """Hash password hash value."""
        return hash(self._hash)

    @property
    def value(self) -> str:
        """Get hash value."""
        return self._hash

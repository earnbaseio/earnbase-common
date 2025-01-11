"""Token value object."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Token value object."""

    value: str
    expires_at: datetime
    token_type: str
    refresh_token: Optional[str] = None

    model_config = ConfigDict(frozen=True)

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.token_type} {self.value}"

    def __eq__(self, other: object) -> bool:
        """Compare token values."""
        if not isinstance(other, Token):
            return False
        return (
            self.value == other.value
            and self.expires_at == other.expires_at
            and self.token_type == other.token_type
            and self.refresh_token == other.refresh_token
        )

    def __hash__(self) -> int:
        """Hash token value."""
        return hash(
            (
                self.value,
                self.expires_at,
                self.token_type,
                self.refresh_token,
            )
        )

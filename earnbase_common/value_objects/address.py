"""Address value object."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class Address(BaseModel):
    """Address value object."""

    street: str
    city: str
    state: str
    country: str
    postal_code: str
    unit: Optional[str] = None

    model_config = ConfigDict(frozen=True)

    def __str__(self) -> str:
        """Return string representation."""
        address = f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"
        if self.unit:
            address = f"Unit {self.unit}, {address}"
        return address

    def __eq__(self, other: object) -> bool:
        """Compare address values."""
        if not isinstance(other, Address):
            return False
        return (
            self.street == other.street
            and self.city == other.city
            and self.state == other.state
            and self.country == other.country
            and self.postal_code == other.postal_code
            and self.unit == other.unit
        )

    def __hash__(self) -> int:
        """Hash address value."""
        return hash(
            (
                self.street,
                self.city,
                self.state,
                self.country,
                self.postal_code,
                self.unit,
            )
        )

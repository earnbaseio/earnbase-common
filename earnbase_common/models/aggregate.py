"""Aggregate root base class."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .domain_event import DomainEvent


class AggregateRoot(BaseModel):
    """Base class for aggregate roots."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    version: int = 1
    _events: List[DomainEvent] = []

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    def add_event(self, event: DomainEvent) -> None:
        """Add domain event."""
        self._events.append(event)

    def clear_events(self) -> None:
        """Clear domain events."""
        self._events = []

    @property
    def events(self) -> List[DomainEvent]:
        """Get domain events."""
        return self._events.copy()

    def increment_version(self) -> None:
        """Increment version."""
        object.__setattr__(self, "version", self.version + 1)
        object.__setattr__(self, "updated_at", datetime.utcnow())

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}(id={self.id}, version={self.version})"

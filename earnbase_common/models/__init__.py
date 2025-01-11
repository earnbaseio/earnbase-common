"""Base models for the application."""

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base model with common functionality."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True, json_encoders={datetime: lambda v: v.isoformat()}
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump()


class DomainEvent(BaseModel):
    """Base class for domain events."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = Field(default="")  # Empty string as default
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"

    def __init__(self, **data: Any) -> None:
        """Initialize domain event."""
        if "event_type" not in data:
            data["event_type"] = self.__class__.__name__
        super().__init__(**data)


class AggregateRoot(BaseModel):
    """Base class for aggregate roots."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)

    def __init__(self, **data: Any) -> None:
        """Initialize aggregate root."""
        super().__init__(**data)
        self._events: list[DomainEvent] = []

    def add_event(self, event: DomainEvent) -> None:
        """Add domain event."""
        self._events.append(event)

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return all events."""
        events = self._events.copy()
        self._events.clear()
        return events

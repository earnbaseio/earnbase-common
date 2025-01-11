"""Base aggregate root model."""

import json
from datetime import datetime
from typing import Any, Dict, List

from earnbase_common.models.domain_event import DomainEvent
from pydantic import BaseModel, Field


class AggregateRoot(BaseModel):
    """Base aggregate root model."""

    id: str = Field(description="Aggregate ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Created timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Updated timestamp"
    )
    version: int = Field(default=1, description="Aggregate version")

    def __init__(self, **data: Any):
        """Initialize aggregate root."""
        super().__init__(**data)
        self._events: List[DomainEvent] = []

    def add_event(self, event: DomainEvent) -> None:
        """Add domain event."""
        self._events.append(event)

    def clear_events(self) -> None:
        """Clear domain events."""
        self._events = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return json.loads(self.model_dump_json())

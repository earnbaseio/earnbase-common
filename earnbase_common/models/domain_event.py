"""Domain event base class."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """Base class for domain events."""

    aggregate_id: str = Field(description="Aggregate ID")
    event_type: str = Field(description="Event type")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().model_dump()
        if isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()
        return data

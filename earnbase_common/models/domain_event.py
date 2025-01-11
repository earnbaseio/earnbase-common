"""Domain event base class."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel):
    """Base class for domain events."""

    id: UUID = Field(default_factory=uuid4)
    event_type: str
    aggregate_id: str
    aggregate_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(frozen=True)

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.event_type}(id={self.id}, aggregate_id={self.aggregate_id})"

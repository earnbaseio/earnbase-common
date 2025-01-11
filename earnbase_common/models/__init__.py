"""Domain models module."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from earnbase_common.models.aggregate import AggregateRoot
from earnbase_common.models.domain_event import DomainEvent
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base model with common functionality."""

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uuid: str(uuid),
        },
    )


class Entity(BaseModel):
    """Base entity model."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}(id={self.id})"


__all__ = [
    "BaseModel",
    "Entity",
    "AggregateRoot",
    "DomainEvent",
]

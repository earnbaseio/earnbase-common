"""Tests for aggregate root."""

from datetime import datetime
from uuid import UUID

import pytest
from earnbase_common.models import AggregateRoot, DomainEvent


class TestEvent(DomainEvent):
    """Test event class."""

    data: str


class TestAggregate(AggregateRoot):
    """Test aggregate class."""

    name: str


@pytest.mark.unit
@pytest.mark.models
class TestAggregateRoot:
    """Test aggregate root functionality."""

    def test_aggregate_creation_with_defaults(self):
        """Test aggregate creation with default values."""
        aggregate = TestAggregate(name="test")

        assert aggregate.name == "test"
        assert isinstance(aggregate.id, str)
        UUID(aggregate.id)  # Validate UUID format
        assert isinstance(aggregate.created_at, datetime)
        assert isinstance(aggregate.updated_at, datetime)
        assert aggregate.version == 1
        assert hasattr(aggregate, "_events")
        assert len(aggregate._events) == 0

    def test_aggregate_creation_with_custom_values(self):
        """Test aggregate creation with custom values."""
        aggregate_id = "custom-id"
        created_at = datetime(2024, 1, 1)
        updated_at = datetime(2024, 1, 2)
        version = 2

        aggregate = TestAggregate(
            name="test",
            id=aggregate_id,
            created_at=created_at,
            updated_at=updated_at,
            version=version,
        )

        assert aggregate.name == "test"
        assert aggregate.id == aggregate_id
        assert aggregate.created_at == created_at
        assert aggregate.updated_at == updated_at
        assert aggregate.version == version

    def test_add_event(self):
        """Test adding domain events."""
        aggregate = TestAggregate(name="test", id="test-id")
        event1 = TestEvent(
            aggregate_id="test-id", event_type="test_event", data="event 1"
        )
        event2 = TestEvent(
            aggregate_id="test-id", event_type="test_event", data="event 2"
        )

        # Add events
        aggregate.add_event(event1)
        aggregate.add_event(event2)

        assert len(aggregate._events) == 2
        assert aggregate._events[0] == event1
        assert aggregate._events[1] == event2

    def test_clear_events(self):
        """Test clearing domain events."""
        aggregate = TestAggregate(name="test")
        event1 = TestEvent(
            aggregate_id="test-id", event_type="test_event", data="event 1"
        )
        event2 = TestEvent(
            aggregate_id="test-id", event_type="test_event", data="event 2"
        )

        # Add events
        aggregate.add_event(event1)
        aggregate.add_event(event2)

        # Clear events
        aggregate.clear_events()
        assert len(aggregate._events) == 0

    def test_to_dict(self):
        """Test aggregate serialization to dictionary."""
        created_at = datetime(2024, 1, 1)
        updated_at = datetime(2024, 1, 2)

        aggregate = TestAggregate(
            name="test",
            id="test-id",
            created_at=created_at,
            updated_at=updated_at,
            version=1,
        )

        data = aggregate.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "test"
        assert data["id"] == "test-id"
        assert data["created_at"] == created_at.isoformat()
        assert data["updated_at"] == updated_at.isoformat()
        assert data["version"] == 1

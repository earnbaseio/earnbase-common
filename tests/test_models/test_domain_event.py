"""Tests for domain event."""

from datetime import datetime
from uuid import UUID

import pytest
from earnbase_common.models import DomainEvent


class TestDomainEventImpl(DomainEvent):
    """Test domain event implementation."""

    data: str


@pytest.mark.unit
@pytest.mark.models
class TestDomainEvent:
    """Test domain event functionality."""

    def test_event_creation_with_defaults(self):
        """Test event creation with default values."""
        event = TestDomainEventImpl(data="test data")

        assert event.data == "test data"
        assert event.event_type == "TestDomainEventImpl"
        assert isinstance(event.event_id, str)
        UUID(event.event_id)  # Validate UUID format
        assert isinstance(event.timestamp, datetime)
        assert event.version == "1.0"

    def test_event_creation_with_custom_values(self):
        """Test event creation with custom values."""
        event_id = "custom-id"
        event_type = "CustomEvent"
        timestamp = datetime(2024, 1, 1)
        version = "2.0"

        event = TestDomainEventImpl(
            data="test data",
            event_id=event_id,
            event_type=event_type,
            timestamp=timestamp,
            version=version,
        )

        assert event.data == "test data"
        assert event.event_id == event_id
        assert event.event_type == event_type
        assert event.timestamp == timestamp
        assert event.version == version

    def test_event_to_dict(self):
        """Test event serialization to dictionary."""
        timestamp = datetime(2024, 1, 1)
        event = TestDomainEventImpl(
            data="test data",
            event_id="test-id",
            event_type="TestEvent",
            timestamp=timestamp,
            version="1.0",
        )

        data = event.to_dict()
        assert isinstance(data, dict)
        assert data["data"] == "test data"
        assert data["event_id"] == "test-id"
        assert data["event_type"] == "TestEvent"
        assert data["timestamp"] == timestamp.isoformat()
        assert data["version"] == "1.0"

    def test_event_type_default(self):
        """Test event_type defaults to class name."""
        event = TestDomainEventImpl(data="test data")
        assert event.event_type == "TestDomainEventImpl"

        # Override event_type
        event = TestDomainEventImpl(data="test data", event_type="CustomType")
        assert event.event_type == "CustomType"

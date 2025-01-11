"""Tests for base model."""

from datetime import datetime

import pytest
from earnbase_common.models import BaseModel


class TestModel(BaseModel):
    """Test model class."""

    name: str
    age: int
    created_at: datetime = datetime.now()


@pytest.mark.unit
@pytest.mark.models
class TestBaseModel:
    """Test base model functionality."""

    def test_model_creation(self):
        """Test model creation with valid data."""
        data = {"name": "Test User", "age": 25, "created_at": datetime(2024, 1, 1)}
        model = TestModel(**data)
        assert model.name == data["name"]
        assert model.age == data["age"]
        assert model.created_at == data["created_at"]

    def test_model_validation(self):
        """Test model validation."""
        with pytest.raises(ValueError):
            TestModel(name="Test", age=25)  # age should be int

    def test_to_dict(self):
        """Test conversion to dictionary."""
        created_at = datetime.now()
        model = TestModel(name="Test", age=25, created_at=created_at)
        data = model.to_dict()

        assert isinstance(data, dict)
        assert data["name"] == "Test"
        assert data["age"] == 25
        assert data["created_at"] == created_at.isoformat()

    def test_json_serialization(self):
        """Test JSON serialization of datetime."""
        created_at = datetime.now()
        model = TestModel(name="Test", age=25, created_at=created_at)
        json_data = model.model_dump_json()

        assert created_at.isoformat() in json_data
        assert '"name":"Test"' in json_data
        assert '"age":25' in json_data

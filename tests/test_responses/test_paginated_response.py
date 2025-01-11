"""Tests for paginated response models."""

import pytest
from earnbase_common.responses import PaginatedResponse
from earnbase_common.responses.base import PaginationMetadata


@pytest.mark.unit
@pytest.mark.responses
class TestPaginationMetadata:
    """Test PaginationMetadata."""

    def test_pagination_metadata_creation(self):
        """Test creating pagination metadata."""
        # Test with defaults
        meta = PaginationMetadata()
        assert meta.page == 1
        assert meta.per_page == 10
        assert meta.total == 0
        assert meta.total_pages == 0

        # Test with custom values
        meta = PaginationMetadata(page=2, per_page=20, total=100, total_pages=5)
        assert meta.page == 2
        assert meta.per_page == 20
        assert meta.total == 100
        assert meta.total_pages == 5

    def test_pagination_metadata_validation(self):
        """Test pagination metadata validation."""
        # Test invalid page number
        with pytest.raises(ValueError):
            PaginationMetadata(page=0)
        with pytest.raises(ValueError):
            PaginationMetadata(page=-1)

        # Test invalid per_page
        with pytest.raises(ValueError):
            PaginationMetadata(per_page=0)
        with pytest.raises(ValueError):
            PaginationMetadata(per_page=-1)

        # Test invalid total
        with pytest.raises(ValueError):
            PaginationMetadata(total=-1)

        # Test invalid total_pages
        with pytest.raises(ValueError):
            PaginationMetadata(total_pages=-1)

    def test_pagination_metadata_serialization(self):
        """Test pagination metadata serialization."""
        meta = PaginationMetadata(page=2, per_page=20, total=100, total_pages=5)

        # Test dict serialization
        data = meta.dict()
        assert isinstance(data, dict)
        assert data["page"] == 2
        assert data["per_page"] == 20
        assert data["total"] == 100
        assert data["total_pages"] == 5

        # Test JSON serialization
        json_str = meta.json()
        assert isinstance(json_str, str)
        assert '"page": 2' in json_str
        assert '"per_page": 20' in json_str
        assert '"total": 100' in json_str
        assert '"total_pages": 5' in json_str


@pytest.mark.unit
@pytest.mark.responses
class TestPaginatedResponse:
    """Test PaginatedResponse."""

    def test_paginated_response_creation(self):
        """Test creating paginated response."""
        # Test with empty data
        meta = PaginationMetadata()
        response = PaginatedResponse(data=[], meta=meta)
        assert response.data == []
        assert response.meta == meta

        # Test with data
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        meta = PaginationMetadata(page=1, per_page=3, total=10, total_pages=4)
        response = PaginatedResponse(data=data, meta=meta)
        assert response.data == data
        assert response.meta == meta

    def test_paginated_response_validation(self):
        """Test paginated response validation."""
        # data and meta are required
        with pytest.raises(ValueError):
            PaginatedResponse()

        with pytest.raises(ValueError):
            PaginatedResponse(data=[])

        with pytest.raises(ValueError):
            PaginatedResponse(meta=PaginationMetadata())

    def test_paginated_response_with_objects(self):
        """Test paginated response with complex objects."""

        class User:
            def __init__(self, id: int, name: str):
                self.id = id
                self.name = name

            def dict(self):
                return {"id": self.id, "name": self.name}

        users = [User(1, "Alice"), User(2, "Bob"), User(3, "Charlie")]
        meta = PaginationMetadata(page=1, per_page=3, total=3, total_pages=1)

        response = PaginatedResponse(data=[u.dict() for u in users], meta=meta)
        assert len(response.data) == 3
        assert response.data[0]["name"] == "Alice"
        assert response.data[2]["name"] == "Charlie"

    def test_paginated_response_serialization(self):
        """Test paginated response serialization."""
        data = [{"id": i} for i in range(1, 4)]
        meta = PaginationMetadata(page=1, per_page=3, total=10, total_pages=4)
        response = PaginatedResponse(data=data, meta=meta)

        # Test dict serialization
        result = response.dict()
        assert isinstance(result, dict)
        assert result["data"] == data
        assert result["meta"]["page"] == 1
        assert result["meta"]["total"] == 10

        # Test JSON serialization
        json_str = response.json()
        assert isinstance(json_str, str)
        assert '"data":' in json_str
        assert '"meta":' in json_str
        assert '"page": 1' in json_str
        assert '"total": 10' in json_str

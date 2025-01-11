"""Common test fixtures."""

from datetime import datetime, timedelta

import pytest
from earnbase_common.security import JWTConfig, SecurityPolicy, TokenManager
from earnbase_common.value_objects import Address, Email, Money, PhoneNumber


@pytest.fixture
def security_policy():
    """Create test security policy."""
    return SecurityPolicy()


@pytest.fixture
def token_manager():
    """Create test token manager."""
    return TokenManager(
        config=JWTConfig(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )
    )


@pytest.fixture
def sample_user_data():
    """Create sample user data."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "phone": "1234567890",
        "country_code": "1",
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_order_data():
    """Create sample order data."""
    return {
        "id": "test-order-123",
        "user_id": "test-user-123",
        "items": [
            {"id": "item-1", "price": 99.99, "currency": "USD"},
            {"id": "item-2", "price": 49.99, "currency": "USD"},
        ],
        "total": 149.98,
        "currency": "USD",
        "created_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_address_data():
    """Create sample address data."""
    return {
        "street": "123 Test St",
        "city": "Test City",
        "state": "TC",
        "country": "Test Country",
        "postal_code": "12345",
    }


@pytest.fixture
def sample_email():
    """Create sample email object."""
    return Email(value="test@example.com")


@pytest.fixture
def sample_phone():
    """Create sample phone object."""
    return PhoneNumber(value="1234567890", country_code="1")


@pytest.fixture
def sample_money():
    """Create sample money object."""
    return Money(amount=99.99, currency="USD")


@pytest.fixture
def sample_address():
    """Create sample address object."""
    return Address(
        street="123 Test St",
        city="Test City",
        state="TC",
        country="Test Country",
        postal_code="12345",
    )


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime for consistent testing."""
    FAKE_TIME = datetime(2024, 1, 1, 12, 0, 0)

    class MockDatetime:
        @classmethod
        def utcnow(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, "utcnow", MockDatetime.utcnow)
    return FAKE_TIME

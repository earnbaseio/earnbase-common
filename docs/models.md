# Models

## Overview

The models module provides base classes for domain modeling using Pydantic with features like:
- Base model with common functionality
- Domain events for event-driven architecture
- Aggregate roots for DDD (Domain-Driven Design)
- Automatic timestamps and versioning
- UUID generation

## Features

### Base Model

```python
from earnbase_common.models import BaseModel
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """User model."""
    
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime
    
    # Inherited features:
    # - JSON serialization
    # - Dictionary conversion
    # - Datetime ISO format encoding
    
# Usage
user = User(
    id="123",
    email="user@example.com",
    created_at=datetime.utcnow()
)

# Convert to dict
user_dict = user.to_dict()
```

### Domain Events

```python
from earnbase_common.models import DomainEvent
from typing import Dict, Any

class UserCreated(DomainEvent):
    """Event emitted when a user is created."""
    
    user_id: str
    email: str
    
    # Automatic fields:
    # - event_id: UUID
    # - event_type: Class name
    # - timestamp: UTC now
    # - version: "1.0"

# Usage
event = UserCreated(
    user_id="123",
    email="user@example.com"
)

print(event.to_dict())
{
    "event_id": "550e8400-e29b-41d4-a716-446655440000",
    "event_type": "UserCreated",
    "timestamp": "2024-01-11T10:30:45.123Z",
    "version": "1.0",
    "user_id": "123",
    "email": "user@example.com"
}
```

### Aggregate Root

```python
from earnbase_common.models import AggregateRoot, DomainEvent
from typing import List, Optional

class OrderCreated(DomainEvent):
    """Order created event."""
    order_id: str
    total_amount: float

class OrderItem(BaseModel):
    """Order item model."""
    product_id: str
    quantity: int
    price: float

class Order(AggregateRoot):
    """Order aggregate root."""
    
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    status: str = "pending"
    
    # Automatic fields:
    # - id: UUID
    # - created_at: UTC now
    # - updated_at: UTC now
    # - version: 1
    
    def add_item(self, item: OrderItem) -> None:
        """Add item to order."""
        self.items.append(item)
        self.total_amount += item.price * item.quantity
        self.version += 1
        self.updated_at = datetime.utcnow()
        
        # Add domain event
        self.add_event(OrderCreated(
            order_id=self.id,
            total_amount=self.total_amount
        ))

# Usage
order = Order(
    customer_id="123",
    items=[],
    total_amount=0
)

# Add item and track changes
order.add_item(OrderItem(
    product_id="456",
    quantity=2,
    price=9.99
))

# Get and clear events
events = order.clear_events()
```

## Best Practices

### 1. Model Validation

```python
from pydantic import Field, validator
from decimal import Decimal

class Product(BaseModel):
    """Product model with validation."""
    
    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate product name."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

### 2. Value Objects

```python
from pydantic import EmailStr
from typing import NewType

# Simple value objects
UserId = NewType("UserId", str)
OrderId = NewType("OrderId", str)

# Complex value objects
class Email(BaseModel):
    """Email value object."""
    value: EmailStr
    verified: bool = False
    
    def __str__(self) -> str:
        return self.value

class Money(BaseModel):
    """Money value object."""
    amount: Decimal
    currency: str = "USD"
    
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(
            amount=self.amount + other.amount,
            currency=self.currency
        )
```

### 3. Event Sourcing

```python
class EventSourced(AggregateRoot):
    """Base class for event-sourced aggregates."""
    
    def apply_event(self, event: DomainEvent) -> None:
        """Apply event to aggregate."""
        method = f"apply_{event.event_type}"
        if hasattr(self, method):
            getattr(self, method)(event)
    
    def load_from_history(
        self,
        events: List[DomainEvent]
    ) -> None:
        """Load aggregate from event history."""
        for event in events:
            self.apply_event(event)
            self.version += 1
```

## Future Features

### 1. Schema Evolution

```python
class VersionedModel(BaseModel):
    """Model with schema versioning."""
    
    def migrate_from(
        self,
        old_version: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Migrate data from old version."""
        pass
    
    def migrate_to(
        self,
        new_version: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Migrate data to new version."""
        pass
```

### 2. Model Relationships

```python
class Relationship:
    """Define model relationships."""
    
    def __init__(
        self,
        model: Type[BaseModel],
        lazy: bool = True
    ):
        """Initialize relationship."""
        pass

class User(BaseModel):
    """User model with relationships."""
    
    id: str
    orders: Relationship["Order"]
    profile: Relationship["Profile"]
```

### 3. Change Tracking

```python
class TrackedModel(BaseModel):
    """Model with change tracking."""
    
    def get_changes(self) -> Dict[str, Any]:
        """Get changed fields."""
        pass
    
    def has_changes(self) -> bool:
        """Check if model has changes."""
        pass
    
    def reset_changes(self) -> None:
        """Reset change tracking."""
        pass
```

### 4. Model Inheritance

```python
class InheritanceModel(BaseModel):
    """Model with inheritance support."""
    
    type: str = Field(discriminator=True)
    
    @classmethod
    def get_concrete_model(
        cls,
        type: str
    ) -> Type[BaseModel]:
        """Get concrete model class."""
        pass
```

### 5. Model Validation Rules

```python
class ValidationRule:
    """Custom validation rule."""
    
    def validate(
        self,
        value: Any,
        field: str
    ) -> None:
        """Validate value."""
        pass

class BusinessRule:
    """Business rule validator."""
    
    def validate(
        self,
        model: BaseModel
    ) -> None:
        """Validate business rule."""
        pass
``` 
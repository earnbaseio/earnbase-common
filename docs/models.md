# Models

## Overview

The models module provides base classes for implementing Domain-Driven Design (DDD) patterns using Pydantic models. It includes support for entities, aggregate roots, and domain events.

## Features

### Base Models

All models are built on Pydantic with enhanced functionality:

```python
from earnbase_common.models import BaseModel
from datetime import datetime
from typing import Optional

class User(BaseModel):
    name: str
    email: str
    created_at: datetime
    status: Optional[str] = None

# Models are immutable by default
user = User(
    name="John",
    email="john@example.com",
    created_at=datetime.utcnow()
)
```

### Aggregate Root

Base class for aggregate roots with event management:

```python
from earnbase_common.models import AggregateRoot, DomainEvent
from uuid import UUID
from datetime import datetime

class OrderCreated(DomainEvent):
    order_id: str
    total_amount: float

class Order(AggregateRoot):
    customer_id: str
    total: float
    status: str = "pending"

    def place(self) -> None:
        """Place the order."""
        self.status = "placed"
        
        # Add domain event
        self.add_event(
            OrderCreated(
                event_type="OrderCreated",
                aggregate_id=str(self.id),
                aggregate_type="Order",
                order_id=str(self.id),
                total_amount=self.total
            )
        )
        
        # Update version
        self.increment_version()

# Create and place order
order = Order(customer_id="123", total=100.0)
order.place()

# Access events
print(order.events)  # [OrderCreated(...)]
print(order.version)  # 2
```

### Domain Events

Base class for domain events:

```python
from earnbase_common.models import DomainEvent
from datetime import datetime
from typing import Optional, Dict, Any

class UserCreated(DomainEvent):
    user_id: str
    email: str
    metadata: Optional[Dict[str, Any]] = None

# Create event
event = UserCreated(
    event_type="UserCreated",
    aggregate_id="user-123",
    aggregate_type="User",
    user_id="user-123",
    email="user@example.com",
    metadata={"source": "api"}
)

print(event.timestamp)  # 2024-01-12T00:00:00Z
print(event.version)    # 1
```

## Key Features

### 1. Immutability

All models are immutable by default:

```python
from earnbase_common.models import BaseModel

class Product(BaseModel):
    name: str
    price: float

product = Product(name="Phone", price=999.99)
# This will raise an error:
# product.price = 899.99
```

### 2. Event Sourcing

Support for event sourcing pattern:

```python
class Account(AggregateRoot):
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        """Deposit money."""
        self.balance += amount
        self.add_event(
            MoneyDeposited(
                event_type="MoneyDeposited",
                aggregate_id=str(self.id),
                aggregate_type="Account",
                amount=amount
            )
        )
        self.increment_version()

    def withdraw(self, amount: float) -> None:
        """Withdraw money."""
        if amount > self.balance:
            raise ValueError("Insufficient funds")
            
        self.balance -= amount
        self.add_event(
            MoneyWithdrawn(
                event_type="MoneyWithdrawn",
                aggregate_id=str(self.id),
                aggregate_type="Account",
                amount=amount
            )
        )
        self.increment_version()
```

### 3. Version Control

Automatic version management:

```python
class Document(AggregateRoot):
    content: str

    def update_content(self, new_content: str) -> None:
        """Update document content."""
        self.content = new_content
        self.add_event(
            ContentUpdated(
                event_type="ContentUpdated",
                aggregate_id=str(self.id),
                aggregate_type="Document",
                new_content=new_content
            )
        )
        self.increment_version()

doc = Document(content="Initial content")
print(doc.version)  # 1

doc.update_content("Updated content")
print(doc.version)  # 2
print(doc.updated_at)  # 2024-01-12T00:00:00Z
```

## Best Practices

1. **Model Design**:
   - Keep models focused and cohesive
   - Use value objects for complex attributes
   - Follow DDD principles
   - Keep aggregates small

2. **Event Design**:
   - Make events immutable
   - Include all relevant data
   - Use meaningful event names
   - Version events appropriately

3. **Aggregate Design**:
   - Maintain consistency boundaries
   - Handle concurrency with versions
   - Keep event history clean
   - Use meaningful aggregate IDs

4. **Performance**:
   - Be mindful of event payload size
   - Clear events after processing
   - Use appropriate data types
   - Consider event storage strategy

## Examples

### 1. E-commerce Order

```python
from earnbase_common.models import AggregateRoot, DomainEvent
from typing import List, Optional
from decimal import Decimal

class OrderItem:
    product_id: str
    quantity: int
    price: Decimal

class Order(AggregateRoot):
    customer_id: str
    items: List[OrderItem]
    total: Decimal
    status: str = "draft"
    shipping_address: Optional[str] = None

    def add_item(self, item: OrderItem) -> None:
        """Add item to order."""
        self.items.append(item)
        self.total += item.price * item.quantity
        
        self.add_event(
            ItemAdded(
                event_type="ItemAdded",
                aggregate_id=str(self.id),
                aggregate_type="Order",
                item=item
            )
        )
        self.increment_version()

    def checkout(self, shipping_address: str) -> None:
        """Checkout order."""
        if not self.items:
            raise ValueError("Order is empty")
            
        self.shipping_address = shipping_address
        self.status = "pending"
        
        self.add_event(
            OrderCheckedOut(
                event_type="OrderCheckedOut",
                aggregate_id=str(self.id),
                aggregate_type="Order",
                shipping_address=shipping_address
            )
        )
        self.increment_version()
```

### 2. User Management

```python
class User(AggregateRoot):
    email: str
    status: str = "active"
    login_attempts: int = 0

    def deactivate(self, reason: str) -> None:
        """Deactivate user."""
        if self.status == "inactive":
            raise ValueError("User already inactive")
            
        self.status = "inactive"
        
        self.add_event(
            UserDeactivated(
                event_type="UserDeactivated",
                aggregate_id=str(self.id),
                aggregate_type="User",
                reason=reason
            )
        )
        self.increment_version()

    def record_login_attempt(self, success: bool) -> None:
        """Record login attempt."""
        if not success:
            self.login_attempts += 1
            
            if self.login_attempts >= 3:
                self.status = "locked"
                
                self.add_event(
                    UserLocked(
                        event_type="UserLocked",
                        aggregate_id=str(self.id),
                        aggregate_type="User",
                        attempts=self.login_attempts
                    )
                )
                
        else:
            self.login_attempts = 0
            
        self.increment_version()
```

### 3. Content Management

```python
class Article(AggregateRoot):
    title: str
    content: str
    status: str = "draft"
    published_at: Optional[datetime] = None

    def publish(self) -> None:
        """Publish article."""
        if self.status == "published":
            raise ValueError("Article already published")
            
        self.status = "published"
        self.published_at = datetime.utcnow()
        
        self.add_event(
            ArticlePublished(
                event_type="ArticlePublished",
                aggregate_id=str(self.id),
                aggregate_type="Article",
                published_at=self.published_at
            )
        )
        self.increment_version()

    def update_content(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> None:
        """Update article content."""
        if title:
            self.title = title
        if content:
            self.content = content
            
        self.add_event(
            ContentUpdated(
                event_type="ContentUpdated",
                aggregate_id=str(self.id),
                aggregate_type="Article",
                title=title,
                content=content
            )
        )
        self.increment_version()
```
``` 
# Value Objects

## Overview

The value objects module provides immutable value objects for common domain concepts. These objects encapsulate validation logic, comparison operations, and string representation for values like email addresses, phone numbers, money amounts, and physical addresses.

## Features

### Email

The `Email` value object handles email validation and formatting:

```python
from earnbase_common.value_objects import Email

# Create and validate email
email = Email(value="user@example.com")
print(str(email))  # user@example.com

# Invalid email will raise ValueError
try:
    invalid = Email(value="invalid-email")
except ValueError as e:
    print(e)  # Invalid email format

# Comparison
email1 = Email(value="user@example.com")
email2 = Email(value="USER@EXAMPLE.COM")
print(email1 == email2)  # True (case-insensitive)
```

### Money

The `Money` value object handles currency amounts with validation:

```python
from earnbase_common.value_objects import Money
from decimal import Decimal

# Create money objects
price = Money(amount=Decimal("99.99"), currency="USD")
discount = Money(amount=Decimal("10.00"), currency="USD")

# Arithmetic operations
final_price = price - discount
print(str(final_price))  # 89.99 USD

# Cannot mix currencies
try:
    eur = Money(amount=Decimal("100"), currency="EUR")
    total = price + eur
except ValueError as e:
    print(e)  # Cannot add different currencies

# Invalid currency code
try:
    invalid = Money(amount=Decimal("50"), currency="US")
except ValueError as e:
    print(e)  # Invalid currency code
```

### Phone Number

The `PhoneNumber` value object handles phone numbers with country codes:

```python
from earnbase_common.value_objects import PhoneNumber

# Create phone number
phone = PhoneNumber(
    value="1234567890",
    country_code="84"
)
print(str(phone))  # +841234567890

# Invalid format
try:
    invalid = PhoneNumber(
        value="123",
        country_code="84"
    )
except ValueError as e:
    print(e)  # Invalid phone number format

# Comparison
phone1 = PhoneNumber(value="1234567890", country_code="84")
phone2 = PhoneNumber(value="1234567890", country_code="84")
print(phone1 == phone2)  # True
```

### Address

The `Address` value object handles physical addresses:

```python
from earnbase_common.value_objects import Address

# Create address with unit
home = Address(
    street="123 Main St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105",
    unit="4B"
)
print(str(home))
# Unit 4B, 123 Main St, San Francisco, CA 94105, USA

# Create address without unit
office = Address(
    street="456 Market St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105"
)
print(str(office))
# 456 Market St, San Francisco, CA 94105, USA

# Comparison
addr1 = Address(
    street="123 Main St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105"
)
addr2 = Address(
    street="123 Main St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105"
)
print(addr1 == addr2)  # True
```

## Key Features

### 1. Immutability

- All value objects are immutable
- Frozen Pydantic models
- Safe for use as dictionary keys
- Thread-safe operations

### 2. Validation

- Format validation
- Pattern matching
- Currency code validation
- Phone number format checking

### 3. Operations

- String representation
- Equality comparison
- Hash computation
- Arithmetic (for Money)

### 4. Type Safety

- Pydantic validation
- Type hints
- Runtime type checking
- Safe comparisons

## Best Practices

1. **Value Object Usage**:
   - Use for domain values
   - Keep immutable
   - Validate on creation
   - Compare by value

2. **Validation**:
   - Use strict patterns
   - Handle edge cases
   - Provide clear errors
   - Normalize values

3. **Comparison**:
   - Implement __eq__
   - Implement __hash__
   - Type-safe comparisons
   - Handle case sensitivity

4. **String Representation**:
   - Clear formatting
   - Consistent style
   - Include all parts
   - Handle optional fields

## Examples

### 1. User Profile

```python
from earnbase_common.value_objects import (
    Email,
    PhoneNumber,
    Address
)
from pydantic import BaseModel

class UserProfile(BaseModel):
    """User profile with value objects."""
    
    email: Email
    phone: PhoneNumber
    address: Address

# Create profile
profile = UserProfile(
    email=Email(value="user@example.com"),
    phone=PhoneNumber(
        value="1234567890",
        country_code="84"
    ),
    address=Address(
        street="123 Main St",
        city="San Francisco",
        state="CA",
        country="USA",
        postal_code="94105"
    )
)

# Access values
print(str(profile.email))    # user@example.com
print(str(profile.phone))    # +841234567890
print(str(profile.address))  # 123 Main St, San Francisco, CA 94105, USA
```

### 2. Order System

```python
from earnbase_common.value_objects import Money, Address
from decimal import Decimal
from typing import List

class OrderItem:
    """Order item with money values."""
    
    def __init__(
        self,
        product_id: str,
        quantity: int,
        price: Money
    ):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    @property
    def total(self) -> Money:
        """Calculate total price."""
        return Money(
            amount=self.price.amount * self.quantity,
            currency=self.price.currency
        )

class Order:
    """Order with money and address."""
    
    def __init__(
        self,
        items: List[OrderItem],
        shipping_address: Address
    ):
        self.items = items
        self.shipping_address = shipping_address
    
    @property
    def total(self) -> Money:
        """Calculate order total."""
        if not self.items:
            return Money(amount=Decimal("0"), currency="USD")
            
        total = self.items[0].total
        for item in self.items[1:]:
            total = total + item.total
            
        return total

# Create order
items = [
    OrderItem(
        product_id="123",
        quantity=2,
        price=Money(amount=Decimal("10.99"), currency="USD")
    ),
    OrderItem(
        product_id="456",
        quantity=1,
        price=Money(amount=Decimal("29.99"), currency="USD")
    )
]

order = Order(
    items=items,
    shipping_address=Address(
        street="123 Main St",
        city="San Francisco",
        state="CA",
        country="USA",
        postal_code="94105"
    )
)

print(str(order.total))  # 51.97 USD
```

### 3. Contact List

```python
from earnbase_common.value_objects import (
    Email,
    PhoneNumber
)
from typing import Dict, Set

class ContactList:
    """Contact list with value objects."""
    
    def __init__(self):
        self.emails: Dict[str, Set[Email]] = {}
        self.phones: Dict[str, Set[PhoneNumber]] = {}
    
    def add_contact(
        self,
        name: str,
        email: Email,
        phone: PhoneNumber
    ) -> None:
        """Add contact with email and phone."""
        # Add email
        if name not in self.emails:
            self.emails[name] = set()
        self.emails[name].add(email)
        
        # Add phone
        if name not in self.phones:
            self.phones[name] = set()
        self.phones[name].add(phone)
    
    def get_emails(self, name: str) -> Set[Email]:
        """Get all emails for contact."""
        return self.emails.get(name, set())
    
    def get_phones(self, name: str) -> Set[PhoneNumber]:
        """Get all phones for contact."""
        return self.phones.get(name, set())

# Use contact list
contacts = ContactList()

# Add contact
contacts.add_contact(
    name="John Doe",
    email=Email(value="john@example.com"),
    phone=PhoneNumber(value="1234567890", country_code="84")
)

contacts.add_contact(
    name="John Doe",
    email=Email(value="john.doe@company.com"),
    phone=PhoneNumber(value="9876543210", country_code="84")
)

# Get contact info
emails = contacts.get_emails("John Doe")
phones = contacts.get_phones("John Doe")

print([str(e) for e in emails])
# ['john@example.com', 'john.doe@company.com']

print([str(p) for p in phones])
# ['+841234567890', '+849876543210']
``` 
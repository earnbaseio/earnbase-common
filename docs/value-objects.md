# Value Objects

## Overview

The Value Objects module provides immutable value objects for common domain concepts with built-in validation:
- Email addresses
- Password hashes
- Tokens
- Phone numbers
- Money amounts
- Addresses

## Features

### Email

```python
from earnbase_common.value_objects import Email

# Create and validate email
try:
    email = Email(value="user@example.com")
    print(str(email))  # user@example.com
except ValidationError as e:
    print(f"Invalid email: {e}")

# Invalid email will raise ValidationError
try:
    email = Email(value="invalid-email")  # Raises ValidationError
except ValidationError as e:
    print(f"Invalid email: {e}")
```

### Password Hash

```python
from earnbase_common.value_objects import PasswordHash

# Create password hash
hash = PasswordHash(value="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY")
print(str(hash))  # ******** (hash is never exposed in string representation)

# Compare password hashes
hash1 = PasswordHash(value="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY")
hash2 = PasswordHash(value="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY")
assert hash1 == hash2  # True
```

### Token

```python
from earnbase_common.value_objects import Token
from datetime import datetime, timedelta

# Create access token
access_token = Token(
    value="eyJhbGciOiJIUzI1NiIs...",
    expires_at=datetime.utcnow() + timedelta(minutes=30),
    token_type="access",
    metadata={"user_id": "123"}
)

# Check expiration
if not access_token.is_expired():
    print(f"Token valid until {access_token.expires_at}")
else:
    print("Token expired")

print(str(access_token))  # access token (expires: 2024-01-11 15:30:00)
```

### Phone Number

```python
from earnbase_common.value_objects import PhoneNumber

# Create and validate phone number
try:
    phone = PhoneNumber(
        value="1234567890",
        country_code="1"
    )
    print(str(phone))  # +11234567890
except ValidationError as e:
    print(f"Invalid phone number: {e}")

# Invalid phone number will raise ValidationError
try:
    phone = PhoneNumber(
        value="invalid",
        country_code="1"
    )  # Raises ValidationError
except ValidationError as e:
    print(f"Invalid phone number: {e}")
```

### Money

```python
from earnbase_common.value_objects import Money

# Create and validate money amount
try:
    amount = Money(
        amount=99.99,
        currency="USD"
    )
    print(str(amount))  # 99.99 USD
except ValidationError as e:
    print(f"Invalid money amount: {e}")

# Invalid currency will raise ValidationError
try:
    amount = Money(
        amount=99.99,
        currency="invalid"
    )  # Raises ValidationError
except ValidationError as e:
    print(f"Invalid currency: {e}")
```

### Address

```python
from earnbase_common.value_objects import Address

# Create address
address = Address(
    street="123 Main St",
    city="San Francisco",
    state="CA",
    country="USA",
    postal_code="94105"
)

print(str(address))  # 123 Main St, San Francisco, CA 94105, USA
```

## Best Practices

### 1. Immutability

```python
from earnbase_common.value_objects import Email
from pydantic import BaseModel

class User(BaseModel):
    """User entity."""
    
    id: str
    email: Email  # Use value object instead of raw string
    
    def update_email(self, new_email: str) -> None:
        """Update email address."""
        # Create new Email object to validate
        self.email = Email(value=new_email)
```

### 2. Validation

```python
from earnbase_common.value_objects import PhoneNumber, Money
from typing import List

class Order(BaseModel):
    """Order entity."""
    
    id: str
    contact_phone: PhoneNumber
    items: List[str]
    total: Money
    
    def validate_order(self) -> List[str]:
        """Validate order."""
        errors = []
        
        # Phone number and money amount validation handled by value objects
        if len(self.items) == 0:
            errors.append("Order must have at least one item")
            
        return errors
```

### 3. Domain Logic

```python
from earnbase_common.value_objects import Money
from typing import List

class ShoppingCart:
    """Shopping cart."""
    
    def __init__(self):
        self.items: List[tuple[str, Money]] = []
    
    def add_item(self, item_id: str, price: Money) -> None:
        """Add item to cart."""
        self.items.append((item_id, price))
    
    def get_total(self, currency: str = "USD") -> Money:
        """Calculate total in specified currency."""
        total = sum(price.amount for _, price in self.items if price.currency == currency)
        return Money(amount=total, currency=currency)
```

## Future Features

### 1. Date Range

```python
from earnbase_common.value_objects import DateRange
from datetime import date

class DateRange(BaseModel):
    """Date range value object."""
    
    start_date: date
    end_date: date
    
    def validate_range(cls, v: "DateRange") -> "DateRange":
        """Validate date range."""
        if v.end_date < v.start_date:
            raise ValidationError("End date must be after start date")
        return v
    
    def duration_days(self) -> int:
        """Calculate duration in days."""
        return (self.end_date - self.start_date).days
    
    def overlaps(self, other: "DateRange") -> bool:
        """Check if ranges overlap."""
        return (
            self.start_date <= other.end_date and
            self.end_date >= other.start_date
        )
```

### 2. Percentage

```python
from earnbase_common.value_objects import Percentage

class Percentage(BaseModel):
    """Percentage value object."""
    
    value: float
    
    def validate_percentage(cls, v: float) -> float:
        """Validate percentage value."""
        if not 0 <= v <= 100:
            raise ValidationError("Percentage must be between 0 and 100")
        return v
    
    def to_decimal(self) -> float:
        """Convert to decimal."""
        return self.value / 100
    
    def of(self, amount: float) -> float:
        """Calculate percentage of amount."""
        return amount * self.to_decimal()
```

### 3. Version

```python
from earnbase_common.value_objects import Version

class Version(BaseModel):
    """Version value object."""
    
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def bump_major(self) -> "Version":
        """Bump major version."""
        return Version(
            major=self.major + 1,
            minor=0,
            patch=0
        )
    
    def bump_minor(self) -> "Version":
        """Bump minor version."""
        return Version(
            major=self.major,
            minor=self.minor + 1,
            patch=0
        )
```

### 4. Color

```python
from earnbase_common.value_objects import Color

class Color(BaseModel):
    """Color value object."""
    
    hex_value: str
    
    def validate_hex(cls, v: str) -> str:
        """Validate hex color."""
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValidationError("Invalid hex color")
        return v
    
    def to_rgb(self) -> tuple[int, int, int]:
        """Convert to RGB."""
        pass
    
    def to_hsl(self) -> tuple[float, float, float]:
        """Convert to HSL."""
        pass
```

### 5. Geographic Point

```python
from earnbase_common.value_objects import GeoPoint

class GeoPoint(BaseModel):
    """Geographic point value object."""
    
    latitude: float
    longitude: float
    
    def validate_coordinates(cls, v: "GeoPoint") -> "GeoPoint":
        """Validate coordinates."""
        if not -90 <= v.latitude <= 90:
            raise ValidationError("Invalid latitude")
        if not -180 <= v.longitude <= 180:
            raise ValidationError("Invalid longitude")
        return v
    
    def distance_to(self, other: "GeoPoint") -> float:
        """Calculate distance to another point."""
        pass
    
    def is_within_radius(
        self,
        center: "GeoPoint",
        radius_km: float
    ) -> bool:
        """Check if point is within radius of center."""
        pass
``` 
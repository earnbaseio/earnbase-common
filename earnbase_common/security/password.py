"""Password hashing and verification."""

import re
from typing import Optional

import bcrypt
from earnbase_common.errors import ValidationError
from earnbase_common.value_objects import PasswordHash

from .policy import SecurityPolicy, security_policy


class PasswordHasher:
    """Password hashing and verification."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        """Initialize password hasher."""
        self.policy = policy or security_policy

    def validate_password(self, password: str) -> None:
        """Validate password against policy."""
        if len(password) < self.policy.PASSWORD_MIN_LENGTH:
            raise ValidationError(
                f"Password must be at least {self.policy.PASSWORD_MIN_LENGTH} characters long"
            )

        for pattern, message in self.policy.PASSWORD_PATTERNS.values():
            if not re.search(pattern, password):
                raise ValidationError(message)

    async def hash(self, password: str) -> PasswordHash:
        """Hash password."""
        self.validate_password(password)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return PasswordHash(_hash=hashed.decode())

    async def verify(self, password: str, hash_value: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode(), hash_value.encode())
        except ValueError:
            return False

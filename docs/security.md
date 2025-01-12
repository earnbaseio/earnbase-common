# Security

## Overview

The security module provides comprehensive security utilities including JWT token management, password hashing, and security policy configuration. It implements industry best practices for authentication, authorization, and data protection.

## Features

### JWT Token Management

The `TokenManager` class provides JWT token creation and verification:

```python
from earnbase_common.security import JWTConfig, TokenManager
from datetime import timedelta

# Configure JWT
config = JWTConfig(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)

# Create token manager
manager = TokenManager(config)

# Create access token
token = manager.create_token(
    data={"user_id": "123", "role": "admin"},
    token_type="access"
)
print(token.value)      # JWT string
print(token.expires_at) # Expiration datetime

# Create refresh token
refresh = manager.create_token(
    data={"user_id": "123"},
    token_type="refresh"
)

# Custom expiration
custom_token = manager.create_token(
    data={"user_id": "123"},
    token_type="access",
    expires_delta=timedelta(hours=1)
)

# Verify token
try:
    payload = manager.verify_token(
        token.value,
        expected_type="access"
    )
    user_id = payload["user_id"]
except ValidationError as e:
    print(e)  # Token has expired or is invalid
```

### Password Management

The `PasswordHasher` class handles secure password hashing and validation:

```python
from earnbase_common.security import PasswordHasher

# Create password hasher
hasher = PasswordHasher()

# Hash password with policy validation
try:
    hash_value = await hasher.hash("Weak")
except ValidationError as e:
    print(e)  # Password must be at least 8 characters long

# Hash valid password
hash_value = await hasher.hash("StrongP@ssw0rd")
print(hash_value.value)  # Bcrypt hash

# Verify password
is_valid = await hasher.verify(
    "StrongP@ssw0rd",
    hash_value.value
)
print(is_valid)  # True
```

### Security Policy

The `SecurityPolicy` class defines security standards and constraints:

```python
from earnbase_common.security import SecurityPolicy

# Create custom policy
policy = SecurityPolicy(
    PASSWORD_MIN_LENGTH=10,
    MAX_LOGIN_ATTEMPTS=3,
    ACCESS_TOKEN_EXPIRE_MINUTES=15
)

# Password patterns
patterns = policy.PASSWORD_PATTERNS
print(patterns["uppercase"])  # (r"[A-Z]", "Must contain uppercase letter")

# Account policies
max_attempts = policy.MAX_LOGIN_ATTEMPTS        # 5
lockout_time = policy.ACCOUNT_LOCKOUT_MINUTES  # 15

# Token policies
access_expire = policy.ACCESS_TOKEN_EXPIRE_MINUTES      # 30
refresh_expire = policy.REFRESH_TOKEN_EXPIRE_DAYS       # 7
verify_expire = policy.VERIFICATION_TOKEN_EXPIRE_HOURS  # 24
reset_expire = policy.RESET_TOKEN_EXPIRE_HOURS         # 24

# Session policies
max_sessions = policy.MAX_SESSIONS_PER_USER          # 5
idle_timeout = policy.SESSION_IDLE_TIMEOUT_MINUTES   # 60
```

## Key Features

### 1. JWT Management

- Token creation and verification
- Access and refresh tokens
- Custom expiration times
- Token type validation
- Secure signing algorithms

### 2. Password Security

- Bcrypt hashing
- Policy validation
- Pattern matching
- Secure verification
- Salt generation

### 3. Security Policies

- Password requirements
- Account lockout
- Token expiration
- Session management
- Configurable settings

## Best Practices

1. **Token Management**:
   - Use short-lived access tokens
   - Implement refresh token rotation
   - Validate token types
   - Handle expiration gracefully

2. **Password Security**:
   - Enforce strong password policies
   - Use secure hashing algorithms
   - Implement rate limiting
   - Handle validation errors

3. **Security Configuration**:
   - Customize for your needs
   - Follow industry standards
   - Regular policy reviews
   - Monitor security metrics

4. **Error Handling**:
   - Validate inputs thoroughly
   - Provide clear error messages
   - Log security events
   - Handle edge cases

## Examples

### 1. Authentication Flow

```python
from earnbase_common.security import (
    JWTConfig,
    TokenManager,
    PasswordHasher
)
from earnbase_common.errors import ValidationError

class AuthService:
    def __init__(self):
        self.token_manager = TokenManager(
            JWTConfig(secret_key="your-secret-key")
        )
        self.password_hasher = PasswordHasher()

    async def register(self, email: str, password: str):
        """Register new user."""
        try:
            # Hash password
            hash_value = await self.password_hasher.hash(password)
            
            # Create user with hashed password
            user = await create_user(email, hash_value.value)
            
            # Generate tokens
            access_token = self.token_manager.create_token(
                data={"user_id": user.id},
                token_type="access"
            )
            
            refresh_token = self.token_manager.create_token(
                data={"user_id": user.id},
                token_type="refresh"
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            
        except ValidationError as e:
            raise ValueError(f"Registration failed: {str(e)}")

    async def login(self, email: str, password: str):
        """Login user."""
        # Get user
        user = await get_user_by_email(email)
        if not user:
            raise ValueError("User not found")
            
        # Verify password
        is_valid = await self.password_hasher.verify(
            password,
            user.password_hash
        )
        if not is_valid:
            raise ValueError("Invalid password")
            
        # Generate tokens
        return {
            "access_token": self.token_manager.create_token(
                data={"user_id": user.id},
                token_type="access"
            ),
            "refresh_token": self.token_manager.create_token(
                data={"user_id": user.id},
                token_type="refresh"
            )
        }
```

### 2. Password Reset

```python
from earnbase_common.security import TokenManager, PasswordHasher
from datetime import timedelta

class PasswordService:
    def __init__(self):
        self.token_manager = TokenManager(
            JWTConfig(secret_key="your-secret-key")
        )
        self.password_hasher = PasswordHasher()

    async def request_reset(self, email: str):
        """Request password reset."""
        user = await get_user_by_email(email)
        if not user:
            return  # Don't reveal user existence
            
        # Create reset token
        reset_token = self.token_manager.create_token(
            data={"user_id": user.id},
            token_type="reset",
            expires_delta=timedelta(hours=24)
        )
        
        # Send reset email
        await send_reset_email(
            email=user.email,
            token=reset_token.value
        )

    async def reset_password(
        self,
        token: str,
        new_password: str
    ):
        """Reset password with token."""
        try:
            # Verify token
            payload = self.token_manager.verify_token(
                token,
                expected_type="reset"
            )
            
            # Hash new password
            hash_value = await self.password_hasher.hash(
                new_password
            )
            
            # Update password
            await update_user_password(
                user_id=payload["user_id"],
                password_hash=hash_value.value
            )
            
        except ValidationError as e:
            raise ValueError(f"Password reset failed: {str(e)}")
```

### 3. Session Management

```python
from earnbase_common.security import TokenManager, SecurityPolicy
from datetime import datetime

class SessionManager:
    def __init__(self):
        self.token_manager = TokenManager(
            JWTConfig(secret_key="your-secret-key")
        )
        self.policy = SecurityPolicy()

    async def create_session(self, user_id: str):
        """Create new session."""
        # Check active sessions
        active_sessions = await count_user_sessions(user_id)
        if active_sessions >= self.policy.MAX_SESSIONS_PER_USER:
            raise ValueError("Maximum sessions reached")
            
        # Create session token
        session_token = self.token_manager.create_token(
            data={
                "user_id": user_id,
                "session_id": generate_session_id()
            },
            token_type="session"
        )
        
        # Store session
        await store_session(
            user_id=user_id,
            token=session_token.value,
            expires_at=session_token.expires_at
        )
        
        return session_token

    async def validate_session(self, token: str):
        """Validate session token."""
        try:
            # Verify token
            payload = self.token_manager.verify_token(
                token,
                expected_type="session"
            )
            
            # Check session exists
            session = await get_session(
                user_id=payload["user_id"],
                session_id=payload["session_id"]
            )
            if not session:
                raise ValidationError("Session not found")
                
            # Check idle timeout
            last_activity = session.last_activity
            idle_minutes = (datetime.utcnow() - last_activity).seconds / 60
            
            if idle_minutes > self.policy.SESSION_IDLE_TIMEOUT_MINUTES:
                await end_session(session.id)
                raise ValidationError("Session expired")
                
            # Update last activity
            await update_session_activity(session.id)
            
            return payload
            
        except ValidationError as e:
            raise ValueError(f"Session validation failed: {str(e)}")
``` 
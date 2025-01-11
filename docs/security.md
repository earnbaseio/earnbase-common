# Security

## Overview

The Security module provides comprehensive security features for FastAPI applications including:
- Token management (JWT)
- Password hashing and verification
- Security policies
- Session management

## Features

### Security Policies

```python
from earnbase_common.security import SecurityPolicy

# Default security policies
security_policy = SecurityPolicy(
    # Password policies
    PASSWORD_MIN_LENGTH=8,
    PASSWORD_PATTERNS={
        "uppercase": (r"[A-Z]", "Must contain uppercase letter"),
        "lowercase": (r"[a-z]", "Must contain lowercase letter"),
        "digit": (r"\d", "Must contain digit"),
        "special": (r"[!@#$%^&*(),.?\":{}|<>]", "Must contain special character"),
    },
    
    # Account policies
    MAX_LOGIN_ATTEMPTS=5,
    ACCOUNT_LOCKOUT_MINUTES=15,
    
    # Token policies
    ACCESS_TOKEN_EXPIRE_MINUTES=30,
    REFRESH_TOKEN_EXPIRE_DAYS=7,
    VERIFICATION_TOKEN_EXPIRE_HOURS=24,
    RESET_TOKEN_EXPIRE_HOURS=24,
    
    # Session policies
    MAX_SESSIONS_PER_USER=5,
    SESSION_IDLE_TIMEOUT_MINUTES=60,
)
```

### Token Management

```python
from earnbase_common.security import TokenManager, JWTConfig

# Initialize token manager
token_manager = TokenManager(
    config=JWTConfig(
        secret_key="your-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7
    )
)

# Create tokens
access_token = token_manager.create_token(
    data={"user_id": "123"},
    token_type="access"
)

refresh_token = token_manager.create_token(
    data={"user_id": "123"},
    token_type="refresh"
)

# Verify tokens
try:
    payload = token_manager.verify_token(
        token=access_token.value,
        expected_type="access"
    )
    user_id = payload["user_id"]
except ValidationError as e:
    print(f"Token validation failed: {e}")
```

### Password Management

```python
from earnbase_common.security import hash_password, verify_password

# Hash password
password = "MySecurePassword123!"
hashed = hash_password(password)

# Verify password
is_valid = verify_password(password, hashed)
```

## Best Practices

### 1. Token Management

```python
from earnbase_common.security import TokenManager
from datetime import timedelta

class AuthService:
    """Authentication service."""
    
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
    
    async def authenticate_user(self, username: str, password: str):
        """Authenticate user and generate tokens."""
        user = await self.verify_credentials(username, password)
        
        # Generate access token
        access_token = self.token_manager.create_token(
            data={
                "user_id": str(user.id),
                "username": user.username,
                "roles": user.roles
            },
            token_type="access"
        )
        
        # Generate refresh token with longer expiry
        refresh_token = self.token_manager.create_token(
            data={
                "user_id": str(user.id),
                "token_family": str(uuid4())  # For token rotation
            },
            token_type="refresh"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def refresh_tokens(self, refresh_token: str):
        """Refresh access token using refresh token."""
        # Verify refresh token
        payload = self.token_manager.verify_token(
            token=refresh_token,
            expected_type="refresh"
        )
        
        # Generate new access token
        new_access_token = self.token_manager.create_token(
            data={
                "user_id": payload["user_id"],
                "username": payload["username"],
                "roles": payload["roles"]
            },
            token_type="access"
        )
        
        return new_access_token
```

### 2. Password Security

```python
from earnbase_common.security import SecurityPolicy
import re

class PasswordValidator:
    """Password validation."""
    
    def __init__(self, security_policy: SecurityPolicy):
        self.policy = security_policy
    
    def validate_password(self, password: str) -> list[str]:
        """Validate password against security policy."""
        errors = []
        
        # Check length
        if len(password) < self.policy.PASSWORD_MIN_LENGTH:
            errors.append(
                f"Password must be at least {self.policy.PASSWORD_MIN_LENGTH} characters"
            )
        
        # Check patterns
        for pattern, (regex, message) in self.policy.PASSWORD_PATTERNS.items():
            if not re.search(regex, password):
                errors.append(message)
        
        return errors
```

### 3. Session Management

```python
from earnbase_common.security import SecurityPolicy
from datetime import datetime, timedelta

class SessionManager:
    """Session management."""
    
    def __init__(self, security_policy: SecurityPolicy):
        self.policy = security_policy
    
    async def create_session(self, user_id: str):
        """Create new session."""
        # Check active sessions
        active_sessions = await self.get_active_sessions(user_id)
        if len(active_sessions) >= self.policy.MAX_SESSIONS_PER_USER:
            # Remove oldest session
            await self.remove_session(active_sessions[0].id)
        
        # Create new session
        session = await self.store_session(
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(
                minutes=self.policy.SESSION_IDLE_TIMEOUT_MINUTES
            )
        )
        
        return session
    
    async def validate_session(self, session_id: str):
        """Validate session."""
        session = await self.get_session(session_id)
        
        # Check expiry
        if datetime.utcnow() > session.expires_at:
            await self.remove_session(session_id)
            return False
        
        # Update last activity
        await self.update_session_activity(session_id)
        return True
```

## Future Features

### 1. Multi-Factor Authentication

```python
from earnbase_common.security import MFAManager

class MFAManager:
    """Multi-factor authentication."""
    
    async def generate_totp_secret(self) -> str:
        """Generate TOTP secret."""
        pass
    
    async def verify_totp_code(
        self,
        secret: str,
        code: str
    ) -> bool:
        """Verify TOTP code."""
        pass
    
    async def generate_backup_codes(
        self,
        count: int = 10
    ) -> list[str]:
        """Generate backup codes."""
        pass
```

### 2. Rate Limiting

```python
from earnbase_common.security import RateLimiter

class RateLimiter:
    """Rate limiting."""
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        """Check rate limit."""
        pass
    
    async def increment_counter(
        self,
        key: str
    ) -> None:
        """Increment rate limit counter."""
        pass
```

### 3. IP Filtering

```python
from earnbase_common.security import IPFilter

class IPFilter:
    """IP filtering."""
    
    async def add_whitelist(
        self,
        ip_range: str
    ) -> None:
        """Add IP range to whitelist."""
        pass
    
    async def add_blacklist(
        self,
        ip_range: str
    ) -> None:
        """Add IP range to blacklist."""
        pass
    
    async def check_ip(
        self,
        ip: str
    ) -> bool:
        """Check if IP is allowed."""
        pass
```

### 4. Audit Logging

```python
from earnbase_common.security import AuditLogger

class AuditLogger:
    """Security audit logging."""
    
    async def log_auth_event(
        self,
        event_type: str,
        user_id: str,
        metadata: dict
    ) -> None:
        """Log authentication event."""
        pass
    
    async def log_access_event(
        self,
        resource: str,
        action: str,
        user_id: str,
        success: bool
    ) -> None:
        """Log resource access event."""
        pass
```

### 5. Security Headers

```python
from earnbase_common.security import SecurityHeaders

class SecurityHeaders:
    """Security headers management."""
    
    def get_security_headers(self) -> dict:
        """Get security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": self.get_csp_policy(),
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    def get_csp_policy(self) -> str:
        """Get Content Security Policy."""
        pass
``` 
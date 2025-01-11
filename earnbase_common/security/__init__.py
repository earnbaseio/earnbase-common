"""Security utilities."""

from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from earnbase_common.errors import ValidationError
from earnbase_common.value_objects import Token
from pydantic import BaseModel, ConfigDict

from .password import hash_password, verify_password

__all__ = [
    "SecurityPolicy",
    "JWTConfig",
    "TokenManager",
    "security_policy",
    "hash_password",
    "verify_password",
]


class SecurityPolicy(BaseModel):
    """Standard security policies."""

    # Password policies
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_PATTERNS: Dict[str, tuple[str, str]] = {
        "uppercase": (r"[A-Z]", "Must contain uppercase letter"),
        "lowercase": (r"[a-z]", "Must contain lowercase letter"),
        "digit": (r"\d", "Must contain digit"),
        "special": (r"[!@#$%^&*(),.?\":{}|<>]", "Must contain special character"),
    }

    # Account policies
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    # Token policies
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    RESET_TOKEN_EXPIRE_HOURS: int = 24

    # Session policies
    MAX_SESSIONS_PER_USER: int = 5
    SESSION_IDLE_TIMEOUT_MINUTES: int = 60

    model_config = ConfigDict(frozen=True)


# Global instances
security_policy = SecurityPolicy()


class JWTConfig(BaseModel):
    """JWT configuration."""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # Default value from SecurityPolicy
    refresh_token_expire_days: int = 7  # Default value from SecurityPolicy

    model_config = ConfigDict(frozen=True)


class TokenManager:
    """Standard token management."""

    def __init__(self, config: JWTConfig):
        """Initialize token manager."""
        self.config = config

    def create_token(
        self,
        data: dict,
        token_type: str,
        expires_delta: Optional[timedelta] = None,
    ) -> Token:
        """Create standard token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            if token_type == "access":
                expire = datetime.utcnow() + timedelta(
                    minutes=self.config.access_token_expire_minutes
                )
            elif token_type == "refresh":
                expire = datetime.utcnow() + timedelta(
                    days=self.config.refresh_token_expire_days
                )
            else:
                raise ValidationError(f"Invalid token type: {token_type}")

        to_encode = data.copy()
        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": token_type,
            }
        )

        encoded_jwt = jwt.encode(
            to_encode,
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

        return Token(
            value=encoded_jwt,
            expires_at=expire,
            token_type=token_type,
            metadata=data,
        )

    def verify_token(self, token: str, expected_type: Optional[str] = None) -> dict:
        """Verify standard token."""
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
            )

            if expected_type and payload.get("type") != expected_type:
                raise ValidationError(
                    f"Invalid token type. Expected {expected_type}, got {payload.get('type')}"
                )

            return payload
        except jwt.ExpiredSignatureError:
            raise ValidationError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValidationError("Invalid token")

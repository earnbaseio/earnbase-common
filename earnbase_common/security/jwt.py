"""JWT token management."""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from earnbase_common.errors import ValidationError
from earnbase_common.value_objects import Token
from pydantic import BaseModel, ConfigDict


class JWTConfig(BaseModel):
    """JWT configuration."""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

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

        return Token(value=encoded_jwt, expires_at=expire, token_type=token_type)

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

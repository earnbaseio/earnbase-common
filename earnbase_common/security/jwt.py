"""JWT utilities."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import jwt
from pydantic import BaseModel


class JWTConfig(BaseModel):
    """JWT configuration."""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


def create_token(
    data: Dict[str, Any],
    config: JWTConfig,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)


def decode_token(token: str, config: JWTConfig) -> Dict[str, Any]:
    """Decode JWT token."""
    return jwt.decode(token, config.secret_key, algorithms=[config.algorithm])

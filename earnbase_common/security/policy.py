"""Security policy configuration."""

from typing import Dict

from pydantic import BaseModel, ConfigDict


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


# Global instance
security_policy = SecurityPolicy()

"""Common errors module."""

from earnbase_common.errors.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    InternalError,
)
from earnbase_common.errors.handlers import register_error_handlers

__all__ = [
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "InternalError",
    "register_error_handlers",
]

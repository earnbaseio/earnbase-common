"""Common exceptions."""

from typing import Any, Dict, Optional


class APIError(Exception):
    """Base class for API errors."""

    def __init__(
        self,
        message: str,
        code: str = "ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error."""
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(APIError):
    """Authentication error."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTHENTICATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error."""
        super().__init__(
            message=message,
            code=code,
            status_code=401,
            details=details,
        )


class AuthorizationError(APIError):
    """Authorization error."""

    def __init__(
        self,
        message: str = "Permission denied",
        code: str = "AUTHORIZATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error."""
        super().__init__(
            message=message,
            code=code,
            status_code=403,
            details=details,
        )


class ValidationError(APIError):
    """Validation error."""

    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error."""
        super().__init__(
            message=message,
            code=code,
            status_code=400,
            details=details,
        )


class NotFoundError(APIError):
    """Not found error."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error."""
        super().__init__(
            message=message,
            code=code,
            status_code=404,
            details=details,
        )


class ConflictError(APIError):
    """Conflict error."""

    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error."""
        super().__init__(
            message=message,
            code=code,
            status_code=409,
            details=details,
        )


class InternalError(APIError):
    """Internal server error."""

    def __init__(
        self,
        message: str = "Internal server error",
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize error."""
        super().__init__(
            message=message,
            code=code,
            status_code=500,
            details=details,
        )

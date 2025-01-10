"""Error handlers module."""

from typing import Any, Callable, Dict, Optional

from earnbase_common.errors.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InternalError,
    NotFoundError,
    ValidationError,
)
from earnbase_common.logging import get_logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

logger = get_logger(__name__)

ExceptionHandler = Callable[[Request, Exception], JSONResponse]


def create_error_response(
    status_code: int,
    message: str,
    code: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create error response."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


async def api_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle API errors."""
    error = exc if isinstance(exc, APIError) else InternalError(str(exc))
    logger.error(
        "api_error",
        error_type=error.__class__.__name__,
        error_code=error.code,
        error_message=error.message,
        error_details=error.details,
        request_id=getattr(_request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=error.status_code,
        content=create_error_response(
            status_code=error.status_code,
            message=error.message,
            code=error.code,
            details=error.details,
        ),
    )


async def validation_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle validation errors."""
    if isinstance(exc, PydanticValidationError):
        details = {
            "fields": [
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
                for error in exc.errors()
            ]
        }
        logger.error(
            "validation_error",
            error_details=details,
            request_id=getattr(_request.state, "request_id", None),
        )
        return JSONResponse(
            status_code=400,
            content=create_error_response(
                status_code=400,
                message="Validation failed",
                code="VALIDATION_ERROR",
                details=details,
            ),
        )
    return await api_error_handler(_request, exc)


def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers."""
    # Register API error handlers
    app.add_exception_handler(Exception, api_error_handler)
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(AuthenticationError, api_error_handler)
    app.add_exception_handler(AuthorizationError, api_error_handler)
    app.add_exception_handler(ValidationError, api_error_handler)
    app.add_exception_handler(NotFoundError, api_error_handler)
    app.add_exception_handler(ConflictError, api_error_handler)
    app.add_exception_handler(InternalError, api_error_handler)

    # Register validation error handlers
    app.add_exception_handler(PydanticValidationError, validation_error_handler)

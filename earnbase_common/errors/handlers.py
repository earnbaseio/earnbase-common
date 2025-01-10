"""Error handlers module."""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from earnbase_common.errors.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    InternalError,
)
from earnbase_common.logging import get_logger

logger = get_logger(__name__)


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


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle API errors."""
    logger.error(
        "api_error",
        error_type=exc.__class__.__name__,
        error_code=exc.code,
        error_message=exc.message,
        error_details=exc.details,
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            code=exc.code,
            details=exc.details,
        ),
    )


async def validation_error_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
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
        request_id=getattr(request.state, "request_id", None),
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


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions."""
    logger.exception(
        "unhandled_error",
        error_type=exc.__class__.__name__,
        error_message=str(exc),
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            status_code=500,
            message="Internal server error",
            code="INTERNAL_ERROR",
        ),
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(AuthenticationError, api_error_handler)
    app.add_exception_handler(AuthorizationError, api_error_handler)
    app.add_exception_handler(ValidationError, api_error_handler)
    app.add_exception_handler(NotFoundError, api_error_handler)
    app.add_exception_handler(ConflictError, api_error_handler)
    app.add_exception_handler(InternalError, api_error_handler)
    app.add_exception_handler(PydanticValidationError, validation_error_handler)
    app.add_exception_handler(Exception, internal_error_handler)

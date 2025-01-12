"""Base response models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseResponse(BaseModel):
    """Base response model."""

    message: Optional[str] = Field(None, description="Response message")
    meta: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


class SuccessResponse(BaseResponse):
    """Success response model."""

    success: bool = Field(True, description="Request was successful")
    data: Optional[Any] = Field(None, description="Response data")

    
class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(False, description="Request failed")
    code: str = Field(..., description="Error code")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of errors")


class PaginationMetadata(BaseModel):
    """Pagination metadata."""

    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=10, description="Number of items per page")
    total: int = Field(default=0, description="Total number of items")
    total_pages: int = Field(default=0, description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"page": 1, "per_page": 10, "total": 100, "total_pages": 10}
        }
    )


class PaginatedResponse(BaseResponse):
    """Paginated response model."""

    data: List[Any] = Field(description="List of items")
    meta: PaginationMetadata = Field(description="Pagination metadata")

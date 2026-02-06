"""
Common Pydantic schemas used across the API.

These schemas provide standardized response formats and base models.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

# Type variable for generic response data
T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        from_attributes = True
        populate_by_name = True


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class IDMixin(BaseModel):
    """Mixin for ID field."""

    id: Optional[str] = Field(None, description="Document ID")


class SuccessResponse(BaseModel):
    """Standard success response wrapper."""

    success: bool = Field(default=True, description="Operation success status")
    message: Optional[str] = Field(None, description="Optional success message")


class DataResponse(BaseModel, Generic[T]):
    """Generic data response wrapper."""

    success: bool = Field(default=True, description="Operation success status")
    data: T = Field(..., description="Response data")


class ListResponse(BaseModel, Generic[T]):
    """Generic list response with pagination info."""

    success: bool = Field(default=True, description="Operation success status")
    data: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(default=0, description="Current offset")


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    path: Optional[str] = Field(None, description="Request path that caused the error")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    success: bool = Field(default=False, description="Operation success status")
    error: ErrorDetail = Field(..., description="Error details")


class HealthStatus(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Health status (healthy/unhealthy)")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment")


class ReadinessStatus(BaseModel):
    """Readiness check response schema."""

    status: str = Field(..., description="Readiness status")
    checks: dict = Field(..., description="Individual component check results")

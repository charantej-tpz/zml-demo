"""
Authentication schemas for request/response validation.

Provides typed Pydantic models for authentication endpoints.
"""

from typing import Optional

from pydantic import Field

from app.schemas.common import BaseSchema, SuccessResponse


class RegistrationRequest(BaseSchema):
    """Request schema for user registration."""

    token: str = Field(..., description="Authentication token for registration")


class RegistrationResponse(SuccessResponse):
    """Response schema for successful registration."""

    user_id: Optional[str] = Field(None, description="Created user ID")

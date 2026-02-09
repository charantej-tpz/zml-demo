"""
Medical info schemas.

Pydantic models for medical info request/response validation.
"""

from pydantic import BaseModel, Field


class MedicalInfoRequest(BaseModel):
    """Request schema for setting medical info."""

    height: float = Field(..., gt=0, description="Height in cm")
    weight: float = Field(..., gt=0, description="Weight in kg")


class MedicalInfoResponse(BaseModel):
    """Response schema for medical info."""

    user_id: str
    height: float
    weight: float

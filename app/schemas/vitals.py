"""
Vitals schemas for request/response validation.
"""

from pydantic import Field

from app.schemas.common import BaseSchema


class VitalUpdateRequest(BaseSchema):
    """Request schema for updating user vitals."""

    heartrate: int = Field(..., ge=0, le=300, description="Heart rate in bpm")
    blood_pressure: int = Field(..., ge=0, le=300, description="Systolic blood pressure in mmHg")

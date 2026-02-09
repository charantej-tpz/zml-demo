"""
Medical info API endpoints.

Provides endpoints for getting and setting user medical info.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.medical_info import IMedicalInfoService
from app.repositories.medical_info_repository import MedicalInfoRepository
from app.schemas.medical_info import MedicalInfoRequest, MedicalInfoResponse
from app.services.medical_info import MedicalInfoService

router = APIRouter(prefix="/medical-info", tags=["Medical Info"])


def get_medical_info_service() -> IMedicalInfoService:
    """
    Dependency provider for medical info service.

    Wires up: Firestore -> MedicalInfoRepository -> MedicalInfoService
    """
    repo = MedicalInfoRepository()
    return MedicalInfoService(repo)


@router.get("/{user_id}", response_model=MedicalInfoResponse)
async def get_medical_info(
    user_id: str,
    service: IMedicalInfoService = Depends(get_medical_info_service),
):
    """
    Get medical info for a user.

    Args:
        user_id: The user's ID.
        service: Injected medical info service.

    Returns:
        User's medical info (height, weight).
    """
    result = await service.get_medical_info(user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical info not found for user {user_id}",
        )
    return result


@router.post("/{user_id}", response_model=MedicalInfoResponse)
async def set_medical_info(
    user_id: str,
    request: MedicalInfoRequest,
    service: IMedicalInfoService = Depends(get_medical_info_service),
):
    """
    Set medical info for a user.

    Args:
        user_id: The user's ID.
        request: Medical info with height and weight.
        service: Injected medical info service.

    Returns:
        Saved medical info.
    """
    return await service.set_medical_info(
        user_id=user_id,
        height=request.height,
        weight=request.weight,
    )

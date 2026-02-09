"""
Vitals API endpoints.

Provides endpoints for updating user vitals.
"""

from fastapi import APIRouter, Depends

from app.db.realtime_db import RealtimeDBOperations
from app.interfaces.vitals import IVitalsService
from app.repositories.vitals_repository import VitalsRepository
from app.services.vitals import VitalsService

router = APIRouter(prefix="/vitals", tags=["Vitals"])


def get_vitals_service() -> IVitalsService:
    """
    Dependency provider for vitals service.

    Wires up the dependency chain:
    RealtimeDBOperations -> VitalsRepository -> VitalsService

    Returns:
        An implementation of IVitalsService.
    """
    rdb = RealtimeDBOperations(base_path="medical_dashboard")
    repo = VitalsRepository(rdb)
    return VitalsService(repo)


@router.post("/{user_id}")
async def update_vitals(
    user_id: str,
    vitals_service: IVitalsService = Depends(get_vitals_service),
):
    """
    Update user vitals with random values.

    Args:
        user_id: The user's ID.
        vitals_service: Injected vitals service.

    Returns:
        Update status response with generated values.
    """
    return await vitals_service.update_vitals(user_id=user_id)

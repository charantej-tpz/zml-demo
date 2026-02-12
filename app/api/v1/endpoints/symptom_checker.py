"""
Symptom Checker API endpoints.

Provides endpoints for initializing and submitting symptom checker conversations.
"""

from fastapi import APIRouter, Depends

from app.interfaces.symptom_checker import ISymptomCheckerService
from app.repositories.symptom_checker import SymptomCheckerRepository
from app.schemas.symptom_checker import SymptomCheckerSubmitInput
from app.services.symptom_checker import SymptomCheckerService

router = APIRouter(prefix="/symptom-checker", tags=["Symptom Checker"])


def get_symptom_checker_service() -> ISymptomCheckerService:
    """
    Dependency provider for symptom checker service.

    Wires up: Firestore -> SymptomCheckerRepository -> SymptomCheckerService
    """
    repo = SymptomCheckerRepository()
    return SymptomCheckerService(repo)


@router.post("/init")
def init_symptom_checker(service: ISymptomCheckerService = Depends(get_symptom_checker_service)):
    """
    Initialize the symptom checker.

    Args:
        service: Injected symptom checker service.

    Returns:
        Dictionary with the new conversation_id.
    """
    return service.init()


@router.post("/submit")
def submit_symptom_checker(
    input_value: SymptomCheckerSubmitInput,
    service: ISymptomCheckerService = Depends(get_symptom_checker_service),
):
    """
    Submit a message to the symptom checker and get a response.

    Args:
        input_value: Input containing conversation_id and symptoms list.
        service: Injected symptom checker service.

    Returns:
        Submission status response.
    """
    return service.submit(input_value.conversation_id, input_value.symptoms)

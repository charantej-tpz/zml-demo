"""
Authentication API endpoints.

Uses dependency injection to follow Dependency Inversion Principle.
The endpoint depends on IAuthenticationService abstraction, not concrete implementation.
"""

from fastapi import APIRouter, Depends

from app.db.firebase_admin import get_firebase_app
from app.interfaces.authentication import IAuthenticationService
from app.schemas.authentication import RegistrationRequest
from app.services.authentication import AuthenticationService

router = APIRouter(prefix="/authentication", tags=["Authentication"])


def get_auth_service() -> IAuthenticationService:
    """
    Dependency provider for authentication service.

    Returns:
        An implementation of IAuthenticationService.
    """
    firebase_app = get_firebase_app()
    return AuthenticationService(firebase_app)


@router.post("/register")
async def register_user(
    request: RegistrationRequest,
    auth_service: IAuthenticationService = Depends(get_auth_service),
):
    """
    Register a new user.

    Args:
        request: Registration request with token in body.
        auth_service: Injected authentication service.

    Returns:
        Decoded token with user information.
    """
    return await auth_service.register(request.token)


@router.post("/me")
async def get_me(
    request: RegistrationRequest,
    auth_service: IAuthenticationService = Depends(get_auth_service),
):
    """
    Get the current user's information.

    Args:
        request: Request with token in body.
        auth_service: Injected authentication service.

    Returns:
        Full decoded token with user information.
    """
    return await auth_service.get_me(request.token)

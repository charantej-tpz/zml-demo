"""
Custom exceptions and exception handlers for the API.

Provides consistent error responses across the application.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class APIException(Exception):
    """
    Base exception for all API errors.

    Attributes:
        status_code: HTTP status code for the response.
        detail: Human-readable error message.
        error_code: Machine-readable error code for client handling.
        headers: Optional headers to include in the response.
    """

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An unexpected error occurred",
        error_code: str = "INTERNAL_ERROR",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.headers = headers
        super().__init__(detail)


class NotFoundError(APIException):
    """Resource not found exception."""

    def __init__(
        self,
        detail: str = "Resource not found",
        error_code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
        )


class ValidationError(APIException):
    """Validation error exception."""

    def __init__(
        self,
        detail: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
        )


class UnauthorizedError(APIException):
    """Unauthorized access exception."""

    def __init__(
        self,
        detail: str = "Unauthorized",
        error_code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(APIException):
    """Forbidden access exception."""

    def __init__(
        self,
        detail: str = "Forbidden",
        error_code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
        )


class ConflictError(APIException):
    """Resource conflict exception."""

    def __init__(
        self,
        detail: str = "Resource conflict",
        error_code: str = "CONFLICT",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
        )


class DatabaseError(APIException):
    """Database operation error exception."""

    def __init__(
        self,
        detail: str = "Database operation failed",
        error_code: str = "DATABASE_ERROR",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
        )


class AuthenticationError(APIException):
    """Authentication/token verification error exception."""

    def __init__(
        self,
        detail: str = "Authentication failed",
        error_code: str = "AUTHENTICATION_ERROR",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredError(APIException):
    """Token expired exception."""

    def __init__(
        self,
        detail: str = "Token has expired",
        error_code: str = "TOKEN_EXPIRED",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(APIException):
    """Invalid token exception."""

    def __init__(
        self,
        detail: str = "Invalid token",
        error_code: str = "INVALID_TOKEN",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_error_response(
    status_code: int,
    detail: str,
    error_code: str,
    path: str,
) -> Dict[str, Any]:
    """Create a standardized error response body."""
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": detail,
            "path": path,
        },
    }


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle APIException and return a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=exc.error_code,
            path=str(request.url.path),
        ),
        headers=exc.headers,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions and return a JSON response."""
    import logging

    logger = logging.getLogger(__name__)
    logger.exception(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
            error_code="INTERNAL_ERROR",
            path=str(request.url.path),
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(APIException, api_exception_handler)
    # Optionally catch all unhandled exceptions in production
    # app.add_exception_handler(Exception, generic_exception_handler)

"""
Authentication service module.

Implements authentication business logic following SOLID principles:
- Single Responsibility: Only handles authentication operations
- Open/Closed: Extends IAuthenticationService, can be extended without modification
- Liskov Substitution: Can be replaced by any IAuthenticationService implementation
- Dependency Inversion: Firebase app is injected via constructor
"""

import logging

import firebase_admin
from firebase_admin import auth
from firebase_admin._auth_utils import InvalidIdTokenError

from app.core.exceptions import (
    APIException,
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
)
from app.interfaces.authentication import IAuthenticationService

logger = logging.getLogger(__name__)


class AuthenticationService(IAuthenticationService):
    """
    Concrete implementation of authentication service.

    Handles user registration and other authentication operations.
    """

    def __init__(self, firebase_app: firebase_admin.App) -> None:
        """
        Initialize the authentication service.

        Args:
            firebase_app: Initialized Firebase Admin app instance.
        """
        self._app = firebase_app

    async def register(self, token: str):
        """
        Register a new user with the provided token.

        Args:
            token: Firebase ID token to verify.

        Returns:
            Decoded token with user information.

        Raises:
            TokenExpiredError: If the token has expired.
            InvalidTokenError: If the token is invalid or malformed.
            AuthenticationError: If authentication fails for other reasons.
            APIException: If an unexpected error occurs.
        """
        try:
            logger.info("Processing registration request")

            decoded = auth.verify_id_token(token, app=self._app)
            uid = decoded["uid"]

            auth.set_custom_user_claims(uid, {"role": "Dawggy", "version": "1.0"})

            logger.info(f"User registered successfully: {uid}")
            return {
                "detail": "User registered successfully",
                "uid": uid,
            }

        except InvalidIdTokenError as e:
            error_msg = str(e).lower()
            if "expired" in error_msg:
                logger.warning(f"Expired token received: {e}")
                raise TokenExpiredError(
                    detail="The provided token has expired. Please re-authenticate."
                ) from e
            else:
                logger.warning(f"Invalid token received: {e}")
                raise InvalidTokenError(detail=f"Invalid token: {e}") from e

        except auth.UserNotFoundError as e:
            logger.error(f"User not found: {e}")
            raise AuthenticationError(detail="User not found in Firebase") from e

        except APIException:
            raise

        except Exception as e:
            logger.exception(f"Unexpected error during registration: {e}")
            raise APIException(
                detail=f"An unexpected error occurred during registration: {e}"
            ) from e

    async def get_me(self, token: str):
        """
        Get the current user's information from the token.

        Args:
            token: Firebase ID token to decode.

        Returns:
            Full decoded token with user information.

        Raises:
            TokenExpiredError: If the token has expired.
            InvalidTokenError: If the token is invalid or malformed.
            APIException: If an unexpected error occurs.
        """
        try:
            logger.info("Processing get_me request")

            decoded = auth.verify_id_token(token, app=self._app)

            logger.info(f"Token decoded successfully for user: {decoded.get('uid')}")
            return decoded

        except InvalidIdTokenError as e:
            error_msg = str(e).lower()
            if "expired" in error_msg:
                logger.warning(f"Expired token received: {e}")
                raise TokenExpiredError(
                    detail="The provided token has expired. Please re-authenticate."
                ) from e
            else:
                logger.warning(f"Invalid token received: {e}")
                raise InvalidTokenError(detail=f"Invalid token: {e}") from e

        except APIException:
            raise

        except Exception as e:
            logger.exception(f"Unexpected error during get_me: {e}")
            raise APIException(detail=f"An unexpected error occurred: {e}") from e

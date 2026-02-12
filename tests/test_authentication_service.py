"""
Unit tests for Authentication Service.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAuthenticationService:
    """Test suite for AuthenticationService."""

    @pytest.fixture
    def mock_firebase_app(self):
        """Mock Firebase Admin app."""
        mock = MagicMock()
        mock.project_id = "test-project"
        return mock

    @pytest.fixture
    def mock_auth_repo(self):
        """Mock authentication repository."""
        mock = AsyncMock()
        mock.register_user.return_value = None
        return mock

    @pytest.fixture
    def auth_service(self, mock_firebase_app, mock_auth_repo):
        """Create an AuthenticationService with mocked dependencies."""
        from app.services.authentication import AuthenticationService

        return AuthenticationService(mock_firebase_app, mock_auth_repo)

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service, mock_auth_repo):
        """Test successful user registration."""
        mock_token = "valid_token"
        mock_uid = "user123"
        mock_decoded = {"uid": mock_uid, "email": "test@example.com"}

        with patch("firebase_admin.auth.verify_id_token", return_value=mock_decoded):
            with patch("firebase_admin.auth.set_custom_user_claims") as mock_set_claims:
                result = await auth_service.register(mock_token)

                assert result["detail"] == "User registered successfully"
                assert result["uid"] == mock_uid
                mock_auth_repo.register_user.assert_called_once()
                mock_set_claims.assert_called_once_with(
                    mock_uid, {"role": "family_head", "version": "1.0"}
                )

    @pytest.mark.asyncio
    async def test_register_invalid_token(self, auth_service):
        """Test registration with invalid token raises InvalidTokenError."""
        from firebase_admin._auth_utils import InvalidIdTokenError

        mock_token = "invalid_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=InvalidIdTokenError("Invalid token"),
        ):
            from app.core.exceptions import InvalidTokenError

            with pytest.raises(InvalidTokenError):
                await auth_service.register(mock_token)

    @pytest.mark.asyncio
    async def test_register_expired_token(self, auth_service):
        """Test registration with expired token raises TokenExpiredError."""
        from firebase_admin._auth_utils import InvalidIdTokenError

        mock_token = "expired_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=InvalidIdTokenError("Token has expired"),
        ):
            from app.core.exceptions import TokenExpiredError

            with pytest.raises(TokenExpiredError):
                await auth_service.register(mock_token)

    @pytest.mark.asyncio
    async def test_register_user_not_found(self, auth_service):
        """Test registration when user not found raises AuthenticationError."""
        from firebase_admin import auth

        mock_token = "valid_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=auth.UserNotFoundError("User not found"),
        ):
            from app.core.exceptions import AuthenticationError

            with pytest.raises(AuthenticationError):
                await auth_service.register(mock_token)

    @pytest.mark.asyncio
    async def test_register_repository_error(self, auth_service, mock_auth_repo):
        """Test registration when repository fails raises APIException."""
        mock_token = "valid_token"
        mock_uid = "user123"
        mock_decoded = {"uid": mock_uid, "email": "test@example.com"}

        with patch("firebase_admin.auth.verify_id_token", return_value=mock_decoded):
            with patch("firebase_admin.auth.set_custom_user_claims"):
                mock_auth_repo.register_user.side_effect = Exception("Database error")

                from app.core.exceptions import APIException

                with pytest.raises(APIException):
                    await auth_service.register(mock_token)

    @pytest.mark.asyncio
    async def test_get_me_success(self, auth_service):
        """Test successful get_me request."""
        mock_token = "valid_token"
        mock_decoded = {
            "uid": "user123",
            "email": "test@example.com",
            "name": "Test User",
        }

        with patch("firebase_admin.auth.verify_id_token", return_value=mock_decoded):
            result = await auth_service.get_me(mock_token)

            assert result["uid"] == "user123"
            assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, auth_service):
        """Test get_me with invalid token raises InvalidTokenError."""
        from firebase_admin._auth_utils import InvalidIdTokenError

        mock_token = "invalid_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=InvalidIdTokenError("Invalid token"),
        ):
            from app.core.exceptions import InvalidTokenError

            with pytest.raises(InvalidTokenError):
                await auth_service.get_me(mock_token)

    @pytest.mark.asyncio
    async def test_get_me_expired_token(self, auth_service):
        """Test get_me with expired token raises TokenExpiredError."""
        from firebase_admin._auth_utils import InvalidIdTokenError

        mock_token = "expired_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=InvalidIdTokenError("Token has expired"),
        ):
            from app.core.exceptions import TokenExpiredError

            with pytest.raises(TokenExpiredError):
                await auth_service.get_me(mock_token)

    @pytest.mark.asyncio
    async def test_get_me_unexpected_error(self, auth_service):
        """Test get_me with unexpected error raises APIException."""
        mock_token = "valid_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=Exception("Unexpected error"),
        ):
            from app.core.exceptions import APIException

            with pytest.raises(APIException):
                await auth_service.get_me(mock_token)

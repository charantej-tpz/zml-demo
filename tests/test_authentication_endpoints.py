"""
Tests for authentication API endpoints.
"""

from unittest.mock import patch


class TestAuthenticationEndpoints:
    """Test suite for authentication endpoints."""

    def test_register_user_success(self, client):
        """Test successful user registration."""
        mock_token = "valid_firebase_token"
        mock_uid = "user123"
        mock_decoded = {"uid": mock_uid, "email": "test@example.com"}

        with patch("firebase_admin.auth.verify_id_token", return_value=mock_decoded):
            with patch("firebase_admin.auth.set_custom_user_claims") as mock_set_claims:
                with patch(
                    "app.repositories.authentication.AuthenticationRepository.register_user"
                ) as mock_repo_register:
                    mock_repo_register.return_value = None

                    response = client.post(
                        "/api/v1/authentication/register",
                        json={"token": mock_token},
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["detail"] == "User registered successfully"
                    assert data["uid"] == mock_uid
                    mock_set_claims.assert_called_once_with(
                        mock_uid, {"role": "family_head", "version": "1.0"}
                    )

    def test_register_user_invalid_token(self, client):
        """Test registration with invalid token returns 401."""
        from firebase_admin._auth_utils import InvalidIdTokenError

        mock_token = "invalid_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=InvalidIdTokenError("Invalid token"),
        ):
            response = client.post(
                "/api/v1/authentication/register",
                json={"token": mock_token},
            )

            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert data["error"]["code"] == "INVALID_TOKEN"

    def test_register_user_expired_token(self, client):
        """Test registration with expired token returns 401."""
        from firebase_admin._auth_utils import InvalidIdTokenError

        mock_token = "expired_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=InvalidIdTokenError("Token has expired"),
        ):
            response = client.post(
                "/api/v1/authentication/register",
                json={"token": mock_token},
            )

            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert data["error"]["code"] == "TOKEN_EXPIRED"

    def test_register_user_missing_token(self, client):
        """Test registration with missing token returns 422."""
        response = client.post(
            "/api/v1/authentication/register",
            json={},
        )

        assert response.status_code == 422

    def test_get_me_success(self, client):
        """Test successful get_me request."""
        mock_token = "valid_firebase_token"
        mock_decoded = {
            "uid": "user123",
            "email": "test@example.com",
            "name": "Test User",
        }

        with patch("firebase_admin.auth.verify_id_token", return_value=mock_decoded):
            response = client.post(
                "/api/v1/authentication/me",
                json={"token": mock_token},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["uid"] == "user123"
            assert data["email"] == "test@example.com"

    def test_get_me_invalid_token(self, client):
        """Test get_me with invalid token returns 401."""
        from firebase_admin._auth_utils import InvalidIdTokenError

        mock_token = "invalid_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=InvalidIdTokenError("Invalid token"),
        ):
            response = client.post(
                "/api/v1/authentication/me",
                json={"token": mock_token},
            )

            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert data["error"]["code"] == "INVALID_TOKEN"

    def test_get_me_unexpected_error(self, client):
        """Test get_me with unexpected error returns 500."""
        mock_token = "valid_token"

        with patch(
            "firebase_admin.auth.verify_id_token",
            side_effect=Exception("Unexpected error"),
        ):
            response = client.post(
                "/api/v1/authentication/me",
                json={"token": mock_token},
            )

            # Generic exceptions are not caught by the service and become 500
            assert response.status_code == 500

"""
Tests for medical info API endpoints.
"""

from unittest.mock import patch


class TestMedicalInfoEndpoints:
    """Test suite for medical info endpoints."""

    def test_get_medical_info_success(self, client):
        """Test successful retrieval of medical info."""
        user_id = "user123"
        mock_medical_info = {
            "user_id": user_id,
            "height": 175.5,
            "weight": 70.0,
        }

        with patch(
            "app.services.medical_info.MedicalInfoService.get_medical_info",
            return_value=mock_medical_info,
        ):
            response = client.get(f"/api/v1/medical-info/{user_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["height"] == 175.5
            assert data["weight"] == 70.0

    def test_get_medical_info_not_found(self, client):
        """Test 404 when medical info not found."""
        user_id = "nonexistent_user"

        with patch(
            "app.services.medical_info.MedicalInfoService.get_medical_info",
            return_value=None,
        ):
            response = client.get(f"/api/v1/medical-info/{user_id}")

            assert response.status_code == 404
            data = response.json()
            # FastAPI's HTTPException returns a detail field
            assert "detail" in data
            assert "not found" in data["detail"].lower()

    def test_set_medical_info_success(self, client):
        """Test successful setting of medical info."""
        user_id = "user123"
        request_data = {
            "height": 180.0,
            "weight": 75.5,
        }
        mock_response = {
            "user_id": user_id,
            "height": 180.0,
            "weight": 75.5,
        }

        with patch(
            "app.services.medical_info.MedicalInfoService.set_medical_info",
            return_value=mock_response,
        ):
            response = client.post(
                f"/api/v1/medical-info/{user_id}",
                json=request_data,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["height"] == 180.0
            assert data["weight"] == 75.5

    def test_set_medical_info_invalid_data(self, client):
        """Test validation error with invalid medical info data."""
        user_id = "user123"
        invalid_data = {
            "height": -10.0,  # Invalid: negative height
            "weight": 0,  # Invalid: zero weight
        }

        response = client.post(
            f"/api/v1/medical-info/{user_id}",
            json=invalid_data,
        )

        assert response.status_code == 422

    def test_set_medical_info_missing_height(self, client):
        """Test validation error when height is missing."""
        user_id = "user123"
        incomplete_data = {
            "weight": 75.0,
        }

        response = client.post(
            f"/api/v1/medical-info/{user_id}",
            json=incomplete_data,
        )

        assert response.status_code == 422

    def test_set_medical_info_missing_weight(self, client):
        """Test validation error when weight is missing."""
        user_id = "user123"
        incomplete_data = {
            "height": 175.0,
        }

        response = client.post(
            f"/api/v1/medical-info/{user_id}",
            json=incomplete_data,
        )

        assert response.status_code == 422

    def test_set_medical_info_service_error(self, client):
        """Test error handling when service raises a DatabaseError."""
        user_id = "user123"
        request_data = {
            "height": 175.0,
            "weight": 70.0,
        }

        from app.core.exceptions import DatabaseError

        with patch(
            "app.services.medical_info.MedicalInfoService.set_medical_info",
            side_effect=DatabaseError(detail="Database error"),
        ):
            response = client.post(
                f"/api/v1/medical-info/{user_id}",
                json=request_data,
            )

            # DatabaseError is handled by exception handlers
            assert response.status_code == 500

    def test_medical_info_different_users(self, client):
        """Test medical info operations for different users."""
        users = [
            {"user_id": "user1", "height": 170.0, "weight": 65.0},
            {"user_id": "user2", "height": 180.0, "weight": 80.0},
            {"user_id": "user3", "height": 165.0, "weight": 55.0},
        ]

        for user in users:
            with patch(
                "app.services.medical_info.MedicalInfoService.get_medical_info",
                return_value=user,
            ):
                response = client.get(f"/api/v1/medical-info/{user['user_id']}")

                assert response.status_code == 200
                data = response.json()
                assert data["user_id"] == user["user_id"]
                assert data["height"] == user["height"]
                assert data["weight"] == user["weight"]

"""
Tests for vitals API endpoints.
"""

from unittest.mock import patch


class TestVitalsEndpoints:
    """Test suite for vitals endpoints."""

    def test_update_vitals_success(self, client):
        """Test successful vitals update."""
        user_id = "user123"
        mock_response = {
            "status": "updated",
            "user_id": user_id,
            "heartrate": 75,
            "blood_pressure": 120,
        }

        with patch(
            "app.services.vitals.VitalsService.update_vitals",
            return_value=mock_response,
        ):
            response = client.post(f"/api/v1/vitals/{user_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"
            assert data["user_id"] == user_id
            assert "heartrate" in data
            assert "blood_pressure" in data

    def test_update_vitals_different_users(self, client):
        """Test vitals update for different users."""
        for user_id in ["user1", "user2", "user3"]:
            mock_response = {
                "status": "updated",
                "user_id": user_id,
                "heartrate": 80,
                "blood_pressure": 125,
            }

            with patch(
                "app.services.vitals.VitalsService.update_vitals",
                return_value=mock_response,
            ):
                response = client.post(f"/api/v1/vitals/{user_id}")

                assert response.status_code == 200
                data = response.json()
                assert data["user_id"] == user_id

    def test_update_vitals_service_error(self, client):
        """Test vitals update when service raises a DatabaseError."""
        user_id = "user123"

        from app.core.exceptions import DatabaseError

        with patch(
            "app.services.vitals.VitalsService.update_vitals",
            side_effect=DatabaseError(detail="Database error"),
        ):
            response = client.post(f"/api/v1/vitals/{user_id}")

            # DatabaseError is handled by exception handlers
            assert response.status_code == 500

    def test_update_vitals_with_special_characters_in_user_id(self, client):
        """Test vitals update with user IDs containing special characters."""
        user_id = "user-123_test.name"
        mock_response = {
            "status": "updated",
            "user_id": user_id,
            "heartrate": 72,
            "blood_pressure": 118,
        }

        with patch(
            "app.services.vitals.VitalsService.update_vitals",
            return_value=mock_response,
        ):
            response = client.post(f"/api/v1/vitals/{user_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id

    def test_update_vitals_generates_random_values(self, client):
        """Test that vitals update generates random values within expected ranges."""
        user_id = "user123"

        with patch("app.services.vitals.random.randint") as mock_randint:
            mock_randint.return_value = 75  # Controlled random value

            with patch(
                "app.repositories.vitals_repository.VitalsRepository.update_user_vitals"
            ) as mock_update:
                mock_update.return_value = None

                response = client.post(f"/api/v1/vitals/{user_id}")

                assert response.status_code == 200
                # Verify random was called twice (for heartrate and blood_pressure)
                assert mock_randint.call_count == 2
                mock_randint.assert_any_call(1, 1000)

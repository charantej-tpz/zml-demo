"""
Tests for symptom checker API endpoints.
"""

from unittest.mock import patch


class TestSymptomCheckerEndpoints:
    """Test suite for symptom checker endpoints."""

    # -------------------------------------------------------------------------
    # /init endpoint tests
    # -------------------------------------------------------------------------

    def test_init_success(self, client):
        """Test successful symptom checker initialization."""
        mock_response = {"conversation_id": "conv-123"}

        with patch(
            "app.services.symptom_checker.SymptomCheckerService.init",
            return_value=mock_response,
        ):
            response = client.post("/api/v1/symptom-checker/init")

            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == "conv-123"

    def test_init_returns_conversation_id(self, client):
        """Test that init endpoint returns a conversation_id."""
        mock_response = {"conversation_id": "test-conv-id"}

        with patch(
            "app.services.symptom_checker.SymptomCheckerService.init",
            return_value=mock_response,
        ):
            response = client.post("/api/v1/symptom-checker/init")

            assert response.status_code == 200
            data = response.json()
            assert "conversation_id" in data

    def test_init_service_error(self, client):
        """Test init endpoint when service raises a DatabaseError."""
        from app.core.exceptions import DatabaseError

        with patch(
            "app.services.symptom_checker.SymptomCheckerService.init",
            side_effect=DatabaseError(detail="Database error"),
        ):
            response = client.post("/api/v1/symptom-checker/init")

            # DatabaseError is handled by exception handlers
            assert response.status_code == 500

    # -------------------------------------------------------------------------
    # /submit endpoint tests
    # -------------------------------------------------------------------------

    def test_submit_success(self, client):
        """Test successful symptom submission."""
        mock_response = {"detail": "Symptoms submitted successfully."}
        request_data = {
            "conversation_id": "conv-123",
            "symptoms": ["headache", "fever"],
        }

        with patch(
            "app.services.symptom_checker.SymptomCheckerService.submit",
            return_value=mock_response,
        ):
            response = client.post(
                "/api/v1/symptom-checker/submit",
                json=request_data,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["detail"] == "Symptoms submitted successfully."

    def test_submit_missing_conversation_id(self, client):
        """Test validation error when conversation_id is missing."""
        incomplete_data = {
            "symptoms": ["headache"],
        }

        response = client.post(
            "/api/v1/symptom-checker/submit",
            json=incomplete_data,
        )

        assert response.status_code == 422

    def test_submit_missing_symptoms(self, client):
        """Test validation error when symptoms list is missing."""
        incomplete_data = {
            "conversation_id": "conv-123",
        }

        response = client.post(
            "/api/v1/symptom-checker/submit",
            json=incomplete_data,
        )

        assert response.status_code == 422

    def test_submit_invalid_data(self, client):
        """Test validation error with completely invalid data."""
        response = client.post(
            "/api/v1/symptom-checker/submit",
            json={},
        )

        assert response.status_code == 422

    def test_submit_service_error(self, client):
        """Test submit endpoint when service raises a DatabaseError."""
        from app.core.exceptions import DatabaseError

        request_data = {
            "conversation_id": "conv-123",
            "symptoms": ["headache"],
        }

        with patch(
            "app.services.symptom_checker.SymptomCheckerService.submit",
            side_effect=DatabaseError(detail="Database error"),
        ):
            response = client.post(
                "/api/v1/symptom-checker/submit",
                json=request_data,
            )

            # DatabaseError is handled by exception handlers
            assert response.status_code == 500

    def test_submit_api_exception(self, client):
        """Test submit endpoint when service raises an APIException."""
        from app.core.exceptions import APIException

        request_data = {
            "conversation_id": "conv-123",
            "symptoms": ["headache"],
        }

        with patch(
            "app.services.symptom_checker.SymptomCheckerService.submit",
            side_effect=APIException(detail="Agent error"),
        ):
            response = client.post(
                "/api/v1/symptom-checker/submit",
                json=request_data,
            )

            # APIException is handled by exception handlers
            assert response.status_code == 500

    def test_submit_different_symptoms(self, client):
        """Test symptom submission with different symptom lists."""
        test_cases = [
            {"conversation_id": "conv-1", "symptoms": ["headache"]},
            {"conversation_id": "conv-2", "symptoms": ["fever", "cough", "fatigue"]},
            {"conversation_id": "conv-3", "symptoms": ["nausea", "dizziness"]},
        ]

        for request_data in test_cases:
            mock_response = {"detail": "Symptoms submitted successfully."}

            with patch(
                "app.services.symptom_checker.SymptomCheckerService.submit",
                return_value=mock_response,
            ):
                response = client.post(
                    "/api/v1/symptom-checker/submit",
                    json=request_data,
                )

                assert response.status_code == 200
                data = response.json()
                assert data["detail"] == "Symptoms submitted successfully."

    def test_submit_empty_symptoms_list(self, client):
        """Test symptom submission with an empty symptoms list."""
        mock_response = {"detail": "Symptoms submitted successfully."}
        request_data = {
            "conversation_id": "conv-123",
            "symptoms": [],
        }

        with patch(
            "app.services.symptom_checker.SymptomCheckerService.submit",
            return_value=mock_response,
        ):
            response = client.post(
                "/api/v1/symptom-checker/submit",
                json=request_data,
            )

            assert response.status_code == 200

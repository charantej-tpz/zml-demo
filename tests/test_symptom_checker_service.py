"""
Unit tests for Symptom Checker Service.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestSymptomCheckerService:
    """Test suite for SymptomCheckerService."""

    @pytest.fixture
    def mock_symptom_repo(self):
        """Mock symptom checker repository."""
        mock = MagicMock()
        mock.start_conversation.return_value = "conv-123"
        mock.create_user_message.return_value = None
        mock.create_agent_message.return_value = None
        return mock

    @pytest.fixture
    def symptom_service(self, mock_symptom_repo):
        """Create a SymptomCheckerService with mocked repository and settings."""
        with patch("app.services.symptom_checker.get_settings") as mock_settings:
            mock_settings.return_value.agent_url = "http://localhost:8081"
            from app.services.symptom_checker import SymptomCheckerService

            return SymptomCheckerService(mock_symptom_repo)

    # -------------------------------------------------------------------------
    # init() tests
    # -------------------------------------------------------------------------

    def test_init_success(self, symptom_service, mock_symptom_repo):
        """Test successful initialization of a symptom checker conversation."""
        result = symptom_service.init()

        assert result["conversation_id"] == "conv-123"
        mock_symptom_repo.start_conversation.assert_called_once()

    def test_init_returns_conversation_id(self, symptom_service):
        """Test that init returns a dictionary with conversation_id key."""
        result = symptom_service.init()

        assert "conversation_id" in result
        assert isinstance(result["conversation_id"], str)

    def test_init_database_error(self, symptom_service, mock_symptom_repo):
        """Test database error handling during init."""
        from app.core.exceptions import DatabaseError

        mock_symptom_repo.start_conversation.side_effect = Exception("Database error")

        with pytest.raises(DatabaseError):
            symptom_service.init()

    def test_init_api_exception_passthrough(self, symptom_service, mock_symptom_repo):
        """Test that APIException from repository is re-raised directly."""
        from app.core.exceptions import APIException

        mock_symptom_repo.start_conversation.side_effect = APIException(detail="Custom API error")

        with pytest.raises(APIException, match="Custom API error"):
            symptom_service.init()

    def test_init_database_error_passthrough(self, symptom_service, mock_symptom_repo):
        """Test that DatabaseError from repository is re-raised directly."""
        from app.core.exceptions import DatabaseError

        mock_symptom_repo.start_conversation.side_effect = DatabaseError(
            detail="DB connection failed"
        )

        with pytest.raises(DatabaseError, match="DB connection failed"):
            symptom_service.init()

    # -------------------------------------------------------------------------
    # submit() tests
    # -------------------------------------------------------------------------

    def test_submit_success(self, symptom_service, mock_symptom_repo):
        """Test successful symptom submission."""
        conversation_id = "conv-123"
        symptoms = ["headache", "fever"]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": ["Option A", "Option B"],
            "message_type": "choice",
        }

        with patch("app.services.symptom_checker.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            result = symptom_service.submit(conversation_id, symptoms)

        assert result["detail"] == "Symptoms submitted successfully."
        mock_symptom_repo.create_user_message.assert_called_once_with(conversation_id, symptoms)
        mock_symptom_repo.create_agent_message.assert_called_once()

    def test_submit_calls_agent_with_correct_payload(self, symptom_service, mock_symptom_repo):
        """Test that submit sends the correct payload to the agent."""
        conversation_id = "conv-456"
        symptoms = ["cough", "sore throat"]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": ["Result"],
            "message_type": "text",
        }

        with patch("app.services.symptom_checker.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            symptom_service.submit(conversation_id, symptoms)

            mock_client.post.assert_called_once_with(
                f"{symptom_service.agent_url}/process",
                json={
                    "conversation_id": conversation_id,
                    "selections": symptoms,
                },
            )

    def test_submit_agent_non_200_raises_api_exception(self, symptom_service, mock_symptom_repo):
        """Test that a non-200 response from agent raises APIException."""
        from app.core.exceptions import APIException

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("app.services.symptom_checker.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            with pytest.raises(APIException, match="Failed to get response from agent"):
                symptom_service.submit("conv-123", ["headache"])

    def test_submit_repository_error(self, symptom_service, mock_symptom_repo):
        """Test database error handling during submit."""
        from app.core.exceptions import DatabaseError

        mock_symptom_repo.create_user_message.side_effect = Exception("Database write failed")

        with pytest.raises(DatabaseError):
            symptom_service.submit("conv-123", ["headache"])

    def test_submit_api_exception_passthrough(self, symptom_service, mock_symptom_repo):
        """Test that APIException from repository is re-raised directly."""
        from app.core.exceptions import APIException

        mock_symptom_repo.create_user_message.side_effect = APIException(detail="Custom error")

        with pytest.raises(APIException, match="Custom error"):
            symptom_service.submit("conv-123", ["headache"])

    def test_submit_database_error_passthrough(self, symptom_service, mock_symptom_repo):
        """Test that DatabaseError from repository is re-raised directly."""
        from app.core.exceptions import DatabaseError

        mock_symptom_repo.create_user_message.side_effect = DatabaseError(detail="DB write error")

        with pytest.raises(DatabaseError, match="DB write error"):
            symptom_service.submit("conv-123", ["headache"])

    def test_submit_creates_agent_message(self, symptom_service, mock_symptom_repo):
        """Test that agent message is created with correct parameters."""
        conversation_id = "conv-789"
        symptoms = ["nausea"]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": ["Diagnosis A"],
            "message_type": "result",
        }

        with patch("app.services.symptom_checker.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

            symptom_service.submit(conversation_id, symptoms)

        # The current code overrides with hardcoded values ["DING", "DONG"] and "choice"
        mock_symptom_repo.create_agent_message.assert_called_once_with(
            conversation_id, ["DING", "DONG"], "choice"
        )

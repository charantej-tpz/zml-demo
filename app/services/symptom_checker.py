import logging
from typing import Any, Dict

import httpx

from app.config.settings import get_settings
from app.core.exceptions import APIException, DatabaseError
from app.interfaces.symptom_checker import ISymptomCheckerService
from app.repositories.symptom_checker import SymptomCheckerRepository

logger = logging.getLogger(__name__)


class SymptomCheckerService(ISymptomCheckerService):
    """Concrete implementation of symptom checker service."""

    def __init__(self, repo: SymptomCheckerRepository) -> None:
        """Initialize the service with repository."""
        self.repo = repo
        self.agent_url = get_settings().agent_url

    def init(self) -> Dict[str, Any]:
        """Start a new symptom checker conversation.

        Returns:
            Dictionary with the new conversation_id.

        Raises:
            DatabaseError: If database operation fails.
        """
        try:
            logger.info("Initializing new symptom checker conversation")
            conversation_id = self.repo.start_conversation()
            logger.info(f"Symptom checker conversation started: {conversation_id}")
            return {"conversation_id": conversation_id}
        except APIException:
            raise
        except Exception as e:
            logger.exception(f"Error initializing symptom checker: {e}")
            raise DatabaseError(detail=f"Failed to initialize symptom checker: {e}") from e

    def submit(self, conversation_id: str, symptoms: list[str]) -> Dict[str, Any]:
        """Submit and get Symptom from Agent.

        Args:
            conversation_id: The conversation ID to submit to.
            symptoms: List of symptom strings.

        Returns:
            Dictionary with submission status detail.

        Raises:
            APIException: If the agent response is invalid.
            DatabaseError: If database operation fails.
        """
        try:
            logger.info(f"Submitting symptoms for conversation: {conversation_id}")
            self.repo.create_user_message(conversation_id, symptoms)
            payload = {"conversation_id": conversation_id, "selections": symptoms}
            with httpx.Client(timeout=None) as client:
                response = client.post(f"{self.agent_url}/process", json=payload)
            if response.status_code != 200:
                raise APIException(detail="Failed to get response from agent.")

            agent_response = response.json()
            message = agent_response.get("content")
            response_type = agent_response.get("message_type")
            message = ["DING", "DONG"]
            response_type = "choice"

            if not message or not response_type:
                raise APIException(detail="Invalid response from agent.")

            self.repo.create_agent_message(conversation_id, message, response_type)
            logger.info(f"Symptoms submitted successfully for conversation: {conversation_id}")
            return {"detail": "Symptoms submitted successfully."}
        except APIException:
            raise
        except Exception as e:
            logger.exception(f"Error submitting symptoms for conversation {conversation_id}: {e}")
            raise DatabaseError(detail=f"Failed to submit symptoms: {e}") from e

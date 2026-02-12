import logging
from typing import Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import Client

from app.core.exceptions import DatabaseError
from app.db.firestore import get_firestore_client
from app.interfaces.repositories.symptom_checker import ISymptomCheckerRepository

logger = logging.getLogger(__name__)


COLLECTION_NAME = "conversations"
SUB_COLLECTION_NAME = "messages"


class SymptomCheckerRepository(ISymptomCheckerRepository):
    """Concrete implementation of symptom checker repository."""

    def __init__(self, db: Optional[Client] = None) -> None:
        """Initialize the repository."""
        self._db = db

    @property
    def db(self) -> Client:
        """Get Firestore client."""
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def start_conversation(self) -> str:
        """Start a new conversation and return its ID."""
        try:
            new_conversation_ref = self.db.collection(COLLECTION_NAME).document()
            new_conversation_ref.set(
                {"created_at": firestore.SERVER_TIMESTAMP, "title": "Symptom Checker Conversation"}
            )
            return new_conversation_ref.id
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            raise DatabaseError(detail=f"Failed to start conversation: {e}") from e

    def create_user_message(self, conversation_id: str, message: list[str]) -> None:
        """Add a user message to the conversation."""
        try:
            conversation_ref = self.db.collection(COLLECTION_NAME).document(conversation_id)
            if not conversation_ref:
                raise DatabaseError(
                    detail=f"Conversation with ID {conversation_id} does not exist."
                )
            message_ref = conversation_ref.collection(SUB_COLLECTION_NAME).document()
            message_ref.set(
                {
                    "actor": "user",
                    "type": "symptoms",
                    "content": message,
                    "created_at": firestore.SERVER_TIMESTAMP,
                }
            )
        except Exception as e:
            logger.error(f"Error adding user message: {e}")
            raise DatabaseError(detail=f"Failed to add user message: {e}") from e

    def create_agent_message(
        self, conversation_id: str, message: list[str], response_type: str
    ) -> None:
        """Add an agent message to the conversation."""
        try:
            conversation_ref = self.db.collection(COLLECTION_NAME).document(conversation_id)
            if not conversation_ref:
                raise DatabaseError(
                    detail=f"Conversation with ID {conversation_id} does not exist."
                )
            message_ref = conversation_ref.collection(SUB_COLLECTION_NAME).document()
            message_ref.set(
                {
                    "actor": "agent",
                    "type": response_type,
                    "content": message,
                    "created_at": firestore.SERVER_TIMESTAMP,
                }
            )
        except Exception as e:
            logger.error(f"Error adding agent message: {e}")
            raise DatabaseError(detail=f"Failed to add agent message: {e}") from e

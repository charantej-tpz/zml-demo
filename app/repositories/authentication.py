import logging
from typing import Any, Dict, Optional

from google.cloud.firestore_v1 import Client

from app.core.exceptions import DatabaseError
from app.db.firestore import get_firestore_client
from app.interfaces.repositories.authentication import IAuthenticationRepository

logger = logging.getLogger(__name__)


COLLECTION_NAME = "users"


class AuthenticationRepository(IAuthenticationRepository):
    """Concrete implementation of authentication repository."""

    def __init__(self, db: Optional[Client] = None) -> None:
        """Initialize the repository."""
        self._db = db

    @property
    def db(self) -> Client:
        """Get Firestore client."""
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    async def register_user(self, uid: str, data: Dict[str, Any]) -> None:
        """Register a new user with the User Data."""
        try:
            logger.info(f"Registering user with data: {data}")
            self.db.collection(COLLECTION_NAME).document(uid).set(data, merge=True)
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise DatabaseError(detail=f"Failed to register user: {e}") from e

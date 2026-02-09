"""
Medical info repository implementation.

Handles medical info data operations in Firestore.
"""

import logging
from typing import Any, Dict, List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import Client

from app.core.exceptions import DatabaseError
from app.db.firestore import get_firestore_client
from app.interfaces.repositories.medical_info import IMedicalInfoRepository

logger = logging.getLogger(__name__)

# Collection name for medical info (separate from Firebase Auth users)
COLLECTION_NAME = "medical_info"


class MedicalInfoRepository(IMedicalInfoRepository):
    """
    Concrete implementation of medical info repository.

    Uses Firestore for storage.
    Collection: medical_info/{user_id}
    """

    def __init__(self, db: Optional[Client] = None) -> None:
        """Initialize the repository."""
        self._db = db

    @property
    def db(self) -> Client:
        """Get Firestore client."""
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get medical info by user ID."""
        try:
            doc = self.db.collection(COLLECTION_NAME).document(id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting medical info for {id}: {e}")
            raise DatabaseError(detail=f"Failed to get medical info: {e}") from e

    async def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all medical info records."""
        try:
            docs = self.db.collection(COLLECTION_NAME).limit(limit).stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                if data:
                    data["user_id"] = doc.id
                    results.append(data)
            return results
        except Exception as e:
            logger.error(f"Error getting all medical info: {e}")
            raise DatabaseError(detail=f"Failed to get medical info: {e}") from e

    async def create(self, data: Dict[str, Any], id: Optional[str] = None) -> str:
        """Create/set medical info for a user."""
        try:
            if not id:
                raise ValueError("User ID is required")
            # Add timestamps
            data_with_timestamps = {
                **data,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
            self.db.collection(COLLECTION_NAME).document(id).set(
                data_with_timestamps, merge=True
            )
            return id
        except Exception as e:
            logger.error(f"Error creating medical info: {e}")
            raise DatabaseError(detail=f"Failed to create medical info: {e}") from e

    async def update(self, id: str, data: Dict[str, Any]) -> None:
        """Update medical info for a user."""
        try:
            # Add updated_at timestamp
            data_with_timestamp = {
                **data,
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
            self.db.collection(COLLECTION_NAME).document(id).update(data_with_timestamp)
        except Exception as e:
            logger.error(f"Error updating medical info for {id}: {e}")
            raise DatabaseError(detail=f"Failed to update medical info: {e}") from e

    async def delete(self, id: str) -> None:
        """Delete medical info for a user."""
        try:
            self.db.collection(COLLECTION_NAME).document(id).delete()
        except Exception as e:
            logger.error(f"Error deleting medical info for {id}: {e}")
            raise DatabaseError(detail=f"Failed to delete medical info: {e}") from e

    async def exists(self, id: str) -> bool:
        """Check if medical info exists for a user."""
        try:
            doc = self.db.collection(COLLECTION_NAME).document(id).get()
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking medical info for {id}: {e}")
            raise DatabaseError(detail=f"Failed to check medical info: {e}") from e

    async def get_user_medical_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get medical info for a specific user."""
        return await self.get_by_id(user_id)

    async def set_user_medical_info(self, user_id: str, data: Dict[str, Any]) -> None:
        """Set medical info for a specific user."""
        await self.create(data, user_id)

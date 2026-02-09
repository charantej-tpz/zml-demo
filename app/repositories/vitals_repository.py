"""
Vitals repository implementation.

Handles vitals data operations in Firebase Realtime Database.
"""

import logging
from typing import Any, Dict, List, Optional

from firebase_admin import db as firebase_rdb

from app.core.exceptions import DatabaseError
from app.db.realtime_db import RealtimeDBOperations
from app.interfaces.repositories.vitals import IVitalsRepository

logger = logging.getLogger(__name__)


class VitalsRepository(IVitalsRepository):
    """
    Concrete implementation of vitals repository.

    Uses Firebase Realtime Database for storage.
    Path structure: medical_dashboard/users/{user_id}/vitals
    """

    def __init__(self, rdb: RealtimeDBOperations) -> None:
        """
        Initialize the vitals repository.

        Args:
            rdb: Realtime database operations instance.
        """
        self.rdb = rdb

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get vitals record by user ID."""
        try:
            return self.rdb.get(f"users/{id}/vitals")
        except Exception as e:
            logger.error(f"Error getting vitals for {id}: {e}")
            raise DatabaseError(detail=f"Failed to get vitals: {e}") from e

    async def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all vitals records."""
        try:
            data = self.rdb.get("users")
            if not data:
                return []

            results = []
            for user_id, user_data in list(data.items())[:limit]:
                if isinstance(user_data, dict) and "vitals" in user_data:
                    vitals = user_data["vitals"]
                    vitals["user_id"] = user_id
                    results.append(vitals)
            return results
        except Exception as e:
            logger.error(f"Error getting all vitals: {e}")
            raise DatabaseError(detail=f"Failed to get vitals: {e}") from e

    async def create(self, data: Dict[str, Any], id: Optional[str] = None) -> str:
        """Create vitals record for a user."""
        try:
            if not id:
                raise ValueError("User ID is required for vitals")
            # Add timestamps
            data_with_timestamps = {
                **data,
                "created_at": firebase_rdb.ServerValue.TIMESTAMP,
                "updated_at": firebase_rdb.ServerValue.TIMESTAMP,
            }
            self.rdb.set(f"users/{id}/vitals", data_with_timestamps)
            return id
        except Exception as e:
            logger.error(f"Error creating vitals: {e}")
            raise DatabaseError(detail=f"Failed to create vitals: {e}") from e

    async def update(self, id: str, data: Dict[str, Any]) -> None:
        """Update vitals record for a user."""
        try:
            # Add updated_at timestamp
            data_with_timestamp = {
                **data,
                "updated_at": firebase_db.ServerValue.TIMESTAMP,
            }
            self.rdb.update(f"users/{id}/vitals", data_with_timestamp)
        except Exception as e:
            logger.error(f"Error updating vitals for {id}: {e}")
            raise DatabaseError(detail=f"Failed to update vitals: {e}") from e

    async def delete(self, id: str) -> None:
        """Delete vitals record for a user."""
        try:
            self.rdb.delete(f"users/{id}/vitals")
        except Exception as e:
            logger.error(f"Error deleting vitals for {id}: {e}")
            raise DatabaseError(detail=f"Failed to delete vitals: {e}") from e

    async def exists(self, id: str) -> bool:
        """Check if vitals exist for a user."""
        try:
            data = self.rdb.get(f"users/{id}/vitals")
            return data is not None
        except Exception as e:
            logger.error(f"Error checking vitals existence for {id}: {e}")
            raise DatabaseError(detail=f"Failed to check vitals: {e}") from e

    async def update_user_vitals(self, user_id: str, vitals_data: Dict[str, Any]) -> None:
        """Update vitals for a specific user."""
        await self.update(user_id, vitals_data)

    async def get_user_vitals(self, user_id: str) -> Dict[str, Any]:
        """Get vitals for a specific user."""
        result = await self.get_by_id(user_id)
        return result or {}

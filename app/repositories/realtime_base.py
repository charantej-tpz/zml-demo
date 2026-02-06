"""
Base repository for Firebase Realtime Database operations.

Provides a similar interface to the Firestore BaseRepository but tailored
for the Realtime Database's JSON tree structure.
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from app.core.exceptions import DatabaseError, NotFoundError
from app.db.realtime_db import RealtimeDBOperations

logger = logging.getLogger(__name__)

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


class RealtimeBaseRepository(Generic[T]):
    """
    Base repository for Realtime Database operations.

    Extend this class to create specific repositories for your data paths.

    Example:
        class UserRepository(RealtimeBaseRepository[User]):
            base_path = "users"
            model_class = User
    """

    base_path: str = ""
    model_class: Type[T]

    def __init__(self) -> None:
        """Initialize the repository with database operations."""
        self._db = RealtimeDBOperations(self.base_path)

    def _dict_to_model(self, key: str, data: Dict[str, Any]) -> T:
        """
        Convert a dictionary to a Pydantic model.

        Args:
            key: The record key/ID.
            data: The record data.

        Returns:
            Pydantic model instance.
        """
        data["id"] = key
        return self.model_class(**data)

    async def get_by_id(self, record_id: str) -> Optional[T]:
        """
        Get a record by ID.

        Args:
            record_id: Record ID/key.

        Returns:
            Model instance or None if not found.
        """
        try:
            data = self._db.get(record_id)
            if data is None:
                return None
            return self._dict_to_model(record_id, data)
        except Exception as e:
            logger.error(f"Error getting record {record_id}: {e}")
            raise DatabaseError(f"Failed to get record: {e}")

    async def get_by_id_or_raise(self, record_id: str) -> T:
        """
        Get a record by ID or raise NotFoundError.

        Args:
            record_id: Record ID/key.

        Returns:
            Model instance.

        Raises:
            NotFoundError: If record not found.
        """
        result = await self.get_by_id(record_id)
        if result is None:
            raise NotFoundError(f"Record with ID {record_id} not found in {self.base_path}")
        return result

    async def get_all(self, limit: int = 100) -> List[T]:
        """
        Get all records in the path.

        Note: Realtime Database doesn't have native limit on get(),
        so we fetch all and slice in Python for simplicity.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of model instances.
        """
        try:
            data = self._db.get()
            if data is None:
                return []

            records = []
            for key, value in list(data.items())[:limit]:
                if isinstance(value, dict):
                    records.append(self._dict_to_model(key, value))

            return records
        except Exception as e:
            logger.error(f"Error getting all records: {e}")
            raise DatabaseError(f"Failed to get records: {e}")

    async def create(self, data: Dict[str, Any], record_id: Optional[str] = None) -> str:
        """
        Create a new record.

        Args:
            data: Record data.
            record_id: Optional record ID. If None, auto-generates one.

        Returns:
            Record ID/key.
        """
        try:
            # Remove 'id' from data if present (it's the key, not a field)
            data = {k: v for k, v in data.items() if k != "id"}

            if record_id:
                self._db.set(record_id, data)
                return record_id
            else:
                return self._db.push("", data)
        except Exception as e:
            logger.error(f"Error creating record: {e}")
            raise DatabaseError(f"Failed to create record: {e}")

    async def update(self, record_id: str, data: Dict[str, Any]) -> None:
        """
        Update an existing record.

        Args:
            record_id: Record ID/key.
            data: Fields to update.
        """
        try:
            # Remove 'id' from data if present
            data = {k: v for k, v in data.items() if k != "id"}
            self._db.update(record_id, data)
        except Exception as e:
            logger.error(f"Error updating record {record_id}: {e}")
            raise DatabaseError(f"Failed to update record: {e}")

    async def delete(self, record_id: str) -> None:
        """
        Delete a record.

        Args:
            record_id: Record ID/key.
        """
        try:
            self._db.delete(record_id)
        except Exception as e:
            logger.error(f"Error deleting record {record_id}: {e}")
            raise DatabaseError(f"Failed to delete record: {e}")

    async def query_by_field(
        self,
        field: str,
        value: Any,
        limit: int = 100,
    ) -> List[T]:
        """
        Query records by a field value.

        Note: For this to work efficiently, you should set up indexing
        rules in your Firebase Realtime Database.

        Args:
            field: Field name to query.
            value: Value to match.
            limit: Maximum number of records to return.

        Returns:
            List of matching model instances.
        """
        try:
            data = self._db.query_by_child("", field, value, limit)
            if not data:
                return []

            return [
                self._dict_to_model(key, value)
                for key, value in data.items()
                if isinstance(value, dict)
            ]
        except Exception as e:
            logger.error(f"Error querying records: {e}")
            raise DatabaseError(f"Failed to query records: {e}")

    async def exists(self, record_id: str) -> bool:
        """
        Check if a record exists.

        Args:
            record_id: Record ID/key.

        Returns:
            True if record exists, False otherwise.
        """
        try:
            data = self._db.get(record_id)
            return data is not None
        except Exception as e:
            logger.error(f"Error checking record existence {record_id}: {e}")
            raise DatabaseError(f"Failed to check record existence: {e}")

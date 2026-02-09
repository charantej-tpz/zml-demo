"""
Firebase Realtime Database client and operations.

Provides access to Firebase Realtime Database through the Admin SDK.
"""

import logging
from typing import Any, Dict, Optional

from firebase_admin import db

from app.db.firebase_admin import get_firebase_app

logger = logging.getLogger(__name__)


def get_realtime_db() -> db.Reference:
    """
    Get a reference to the root of the Realtime Database.

    Ensures Firebase Admin is initialized before accessing the database.

    Returns:
        Reference to the Realtime Database root.
    """
    # Ensure Firebase is initialized
    get_firebase_app()

    return db.reference()


def get_db_reference(path: str) -> db.Reference:
    """
    Get a reference to a specific path in the Realtime Database.

    Args:
        path: Path to the database location (e.g., "users" or "users/user123").

    Returns:
        Reference to the specified database path.
    """
    get_firebase_app()
    return db.reference(path)


async def check_realtime_db_connection() -> bool:
    """
    Check if Realtime Database connection is healthy.

    Performs a lightweight read operation to verify connectivity.

    Returns:
        True if connection is healthy, False otherwise.
    """
    try:
        get_firebase_app()
        # Try to read from root (returns None if empty, but verifies connection)
        ref = db.reference()
        # Just check if we can access the reference
        _ = ref.path
        logger.debug("Realtime Database connection check passed")
        return True
    except Exception as e:
        logger.error(f"Realtime Database connection check failed: {e}")
        return False


def get_realtime_client(base_path: str = "") -> "RealtimeDBOperations":
    """
    Get a Realtime Database client (similar to get_firestore_client).

    Args:
        base_path: Base path for all operations (e.g., "medical_dashboard").

    Returns:
        RealtimeDBOperations instance.

    Example:
        rdb = get_realtime_client("medical_dashboard")
        data = rdb.get("users/user123")
    """
    return RealtimeDBOperations(base_path=base_path)


class RealtimeDBOperations:
    """
    Utility class for common Realtime Database operations.

    Provides a simple interface for CRUD operations on the Realtime Database.
    """

    def __init__(self, base_path: str = ""):
        """
        Initialize with an optional base path.

        Args:
            base_path: Base path for all operations (e.g., "users").
        """
        self.base_path = base_path.strip("/")

    def _get_ref(self, path: str = "") -> db.Reference:
        """Get a reference combining base_path and the given path."""
        get_firebase_app()
        full_path = f"{self.base_path}/{path}".strip("/") if path else self.base_path
        return db.reference(full_path) if full_path else db.reference()

    def get(self, path: str = "") -> Optional[Any]:
        """
        Get data at the specified path.

        Args:
            path: Path relative to base_path.

        Returns:
            Data at the path, or None if not found.
        """
        try:
            return self._get_ref(path).get()
        except Exception as e:
            logger.error(f"Error getting data at {path}: {e}")
            raise

    def set(self, path: str, data: Any) -> None:
        """
        Set data at the specified path (overwrites existing data).

        Args:
            path: Path relative to base_path.
            data: Data to set.
        """
        try:
            self._get_ref(path).set(data)
        except Exception as e:
            logger.error(f"Error setting data at {path}: {e}")
            raise

    def update(self, path: str, data: Dict[str, Any]) -> None:
        """
        Update specific fields at the specified path.

        Args:
            path: Path relative to base_path.
            data: Dictionary of fields to update.
        """
        try:
            self._get_ref(path).update(data)
        except Exception as e:
            logger.error(f"Error updating data at {path}: {e}")
            raise

    def push(self, path: str, data: Any) -> str:
        """
        Push new data with an auto-generated key.

        Args:
            path: Path relative to base_path.
            data: Data to push.

        Returns:
            The auto-generated key.
        """
        try:
            ref = self._get_ref(path).push(data)
            return ref.key
        except Exception as e:
            logger.error(f"Error pushing data at {path}: {e}")
            raise

    def delete(self, path: str = "") -> None:
        """
        Delete data at the specified path.

        Args:
            path: Path relative to base_path.
        """
        try:
            self._get_ref(path).delete()
        except Exception as e:
            logger.error(f"Error deleting data at {path}: {e}")
            raise

    def query_by_child(
        self,
        path: str,
        child_key: str,
        value: Any,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Query data by a child value.

        Args:
            path: Path relative to base_path.
            child_key: Child key to order/filter by.
            value: Value to match.
            limit: Maximum number of results.

        Returns:
            Dictionary of matching records.
        """
        try:
            ref = self._get_ref(path)
            result = ref.order_by_child(child_key).equal_to(value).limit_to_first(limit).get()
            return result or {}
        except Exception as e:
            logger.error(f"Error querying data at {path}: {e}")
            raise

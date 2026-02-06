"""
Common dependencies for API endpoints.

Provides dependency injection functions for FastAPI routes.
"""

from typing import Annotated

from fastapi import Depends
from google.cloud.firestore_v1 import Client

from app.config.settings import Settings, get_settings
from app.db.firestore import get_firestore_client
from app.db.realtime_db import RealtimeDBOperations


def get_settings_dependency() -> Settings:
    """
    Dependency to get application settings.

    Returns:
        Settings instance.
    """
    return get_settings()


def get_db() -> Client:
    """
    Dependency to get Firestore client.

    Returns:
        Firestore Client instance.
    """
    return get_firestore_client()


def get_realtime_db(base_path: str = "") -> RealtimeDBOperations:
    """
    Dependency to get Realtime Database operations.

    Args:
        base_path: Base path for database operations.

    Returns:
        RealtimeDBOperations instance.
    """
    return RealtimeDBOperations(base_path)


# Type aliases for cleaner dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings_dependency)]
FirestoreDep = Annotated[Client, Depends(get_db)]
RealtimeDBDep = Annotated[RealtimeDBOperations, Depends(get_realtime_db)]

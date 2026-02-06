"""
Firestore client singleton and connection management.

Provides a centralized Firestore client that can be used across the application.
Supports both production GCP credentials and local emulator.
"""

import logging
import os
from typing import Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import Client

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# Global client instance
_firestore_client: Optional[Client] = None


def get_firestore_client() -> Client:
    """
    Get or create the Firestore client singleton.

    The client is configured based on environment settings:
    - In development with emulator: connects to local Firestore emulator
    - In staging/production: uses GCP credentials

    Returns:
        Firestore Client instance.

    Raises:
        Exception: If client cannot be initialized.
    """
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    settings = get_settings()

    try:
        # Configure for emulator if enabled
        if settings.use_firestore_emulator:
            os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore_emulator_host
            logger.info(
                f"Connecting to Firestore emulator at {settings.firestore_emulator_host}"
            )

        # Set credentials path if provided
        if settings.service_account_credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                settings.service_account_credentials_path
            )

        # Initialize client
        # Note: project_id is automatically extracted from the service account JSON
        client_kwargs = {}

        if settings.firestore_database_id and settings.firestore_database_id != "(default)":
            client_kwargs["database"] = settings.firestore_database_id

        _firestore_client = firestore.Client(**client_kwargs)

        logger.info(
            f"Firestore client initialized for project: {_firestore_client.project}"
        )

        return _firestore_client

    except Exception as e:
        logger.error(f"Failed to initialize Firestore client: {e}")
        raise


def close_firestore_client() -> None:
    """
    Close the Firestore client connection.

    Should be called during application shutdown.
    """
    global _firestore_client

    if _firestore_client is not None:
        _firestore_client.close()
        _firestore_client = None
        logger.info("Firestore client closed")


async def check_firestore_connection() -> bool:
    """
    Check if Firestore connection is healthy.

    Performs a lightweight operation to verify connectivity.

    Returns:
        True if connection is healthy, False otherwise.
    """
    try:
        client = get_firestore_client()
        # Perform a lightweight operation to check connectivity
        # List collections with a limit of 1
        collections = list(client.collections())
        logger.debug(f"Firestore connection check passed. Found {len(collections)} root collections.")
        return True
    except Exception as e:
        logger.error(f"Firestore connection check failed: {e}")
        return False

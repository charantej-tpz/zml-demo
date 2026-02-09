"""
Firebase Admin SDK initialization.

Provides centralized Firebase Admin initialization that supports both
Firestore and Realtime Database through a single credentials file.
"""

import logging
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# Global Firebase app instance
_firebase_app: Optional[firebase_admin.App] = None


def get_firebase_app() -> firebase_admin.App:
    """
    Get or initialize the Firebase Admin app singleton.

    The app is configured using the Firebase Admin SDK credentials JSON file.
    This single initialization provides access to both Firestore and Realtime Database.

    Returns:
        Firebase Admin App instance.

    Raises:
        ValueError: If credentials path is not configured.
        Exception: If Firebase initialization fails.
    """
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    settings = get_settings()

    try:
        # Check if already initialized (e.g., by another module)
        _firebase_app = firebase_admin.get_app()
        logger.info("Using existing Firebase Admin app")
        return _firebase_app
    except ValueError:
        # App not initialized yet, proceed with initialization
        pass

    # Determine credentials source
    cred = None

    # Priority 1: Service account credentials path from settings
    creds_path = settings.service_account_credentials_path
    if creds_path:
        if os.path.exists(creds_path):
            cred = credentials.Certificate(creds_path)
            logger.info(f"Using service account credentials from: {creds_path}")
        else:
            raise ValueError(f"Service account credentials not found: {creds_path}")

    # Priority 2: Environment variable GOOGLE_APPLICATION_CREDENTIALS (fallback)
    elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        cred_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            logger.info(f"Using credentials from GOOGLE_APPLICATION_CREDENTIALS: {cred_path}")
        else:
            raise ValueError(f"Credentials file not found: {cred_path}")

    # Priority 4: Application Default Credentials (for GCP environments)
    else:
        cred = credentials.ApplicationDefault()
        logger.info("Using Application Default Credentials")

    # Build initialization options
    options = {}

    if settings.realtime_database_url:
        options["databaseURL"] = settings.realtime_database_url

    # Note: project_id is automatically extracted from the service account JSON

    # Initialize Firebase Admin
    _firebase_app = firebase_admin.initialize_app(cred, options)
    logger.info(f"Firebase Admin initialized for project: {_firebase_app.project_id}")

    return _firebase_app


def close_firebase_app() -> None:
    """
    Close the Firebase Admin app.

    Should be called during application shutdown.
    """
    global _firebase_app

    if _firebase_app is not None:
        firebase_admin.delete_app(_firebase_app)
        _firebase_app = None
        logger.info("Firebase Admin app closed")

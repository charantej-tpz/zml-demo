"""
Pytest configuration and fixtures.

Provides common fixtures for testing the FastAPI application.
"""

import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"
os.environ["USE_FIRESTORE_EMULATOR"] = "true"
os.environ["SERVICE_ACCOUNT_CREDENTIALS_PATH"] = ""  # Empty for tests (mocked)


@pytest.fixture(scope="session")
def mock_firestore_client():
    """
    Mock Firestore client for testing.

    Returns a MagicMock that simulates the Firestore client.
    """
    mock_client = MagicMock()
    mock_client.project = "test-project"
    mock_client.collections.return_value = []
    return mock_client


@pytest.fixture(scope="session")
def mock_firebase_app():
    """
    Mock Firebase Admin app for testing.

    Returns a MagicMock that simulates the Firebase Admin app.
    """
    mock_app = MagicMock()
    mock_app.project_id = "test-project"
    return mock_app


@pytest.fixture(scope="session")
def app(mock_firestore_client, mock_firebase_app):
    """
    Create a test application instance.

    Patches the Firestore client and Firebase Admin to use mocks.
    """
    with patch("app.db.firestore.get_firestore_client", return_value=mock_firestore_client):
        with patch("app.db.firebase_admin.get_firebase_app", return_value=mock_firebase_app):
            from app.main import create_application

            test_app = create_application()
            yield test_app


@pytest.fixture(scope="session")
def client(app) -> Generator:
    """
    Create a test client for the FastAPI application.

    Yields:
        TestClient instance for making HTTP requests.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_settings():
    """
    Fixture to provide mock settings for testing.
    """
    from app.config.settings import Settings

    return Settings(
        environment="development",
        debug=True,
        use_firestore_emulator=True,
        service_account_credentials_path="",
    )


@pytest.fixture
def mock_realtime_db():
    """
    Mock Realtime Database operations for testing.
    """
    mock_db = MagicMock()
    mock_db.get.return_value = None
    mock_db.set.return_value = None
    mock_db.push.return_value = "test-key-123"
    mock_db.delete.return_value = None
    return mock_db

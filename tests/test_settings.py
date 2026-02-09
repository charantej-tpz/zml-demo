"""
Tests for application configuration and settings.
"""

import os

import pytest


class TestSettings:
    """Test suite for application settings."""

    def test_settings_defaults(self):
        """Test default settings values."""
        from app.config.settings import Settings

        settings = Settings()

        assert settings.environment.value == "development"
        assert settings.port == 8080
        assert settings.api_prefix == "/api/v1"
        assert settings.firestore_database_id == "(default)"

    def test_settings_from_env(self):
        """Test settings can be loaded from environment variables."""
        os.environ["APP_NAME"] = "Test API"
        os.environ["PORT"] = "9000"

        from app.config.settings import Settings

        settings = Settings()

        assert settings.app_name == "Test API"
        assert settings.port == 9000

        # Cleanup
        del os.environ["APP_NAME"]
        del os.environ["PORT"]

    def test_cors_origins_list(self):
        """Test CORS origins parsing."""
        from app.config.settings import Settings

        settings = Settings(cors_origins="http://localhost:3000,http://localhost:8080")

        origins = settings.cors_origins_list
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "http://localhost:8080" in origins

    def test_log_level_validation(self):
        """Test log level validation accepts valid levels."""
        from app.config.settings import Settings

        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = Settings(log_level=level)
            assert settings.log_level == level

    def test_log_level_validation_invalid(self):
        """Test log level validation rejects invalid levels."""
        from pydantic import ValidationError

        from app.config.settings import Settings

        with pytest.raises(ValidationError):
            Settings(log_level="INVALID")

    def test_environment_properties(self):
        """Test environment check properties."""
        from app.config.settings import Environment, Settings

        dev_settings = Settings(environment=Environment.DEVELOPMENT)
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False

        prod_settings = Settings(environment=Environment.PRODUCTION)
        assert prod_settings.is_production is True
        assert prod_settings.is_development is False

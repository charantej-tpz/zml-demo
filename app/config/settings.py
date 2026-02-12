"""
Application settings management using Pydantic Settings.

Supports multiple environments: development, staging, production.
Configuration is loaded from environment variables and .env files.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Supports loading from .env files based on the ENVIRONMENT variable:
    - .env (base, always loaded)
    - .env.{environment} (environment-specific overrides)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # Application
    app_name: str = Field(
        default="ZML API",
        description="Application name",
    )
    app_version: str = Field(
        default="0.1.0",
        description="Application version",
    )
    api_prefix: str = Field(
        default="/api/v1",
        description="API route prefix",
    )

    # Server
    host: str = Field(
        default="0.0.0.0",  # nosec B104 - intentional for container binding
        description="Server host",
    )
    port: int = Field(
        default=8080,
        description="Server port",
    )

    # Google Cloud / Firebase Settings
    service_account_credentials_path: str = Field(
        default="",
        description="Path to service account credentials JSON (Firebase Admin SDK / GCP)",
    )
    firestore_database_id: str = Field(
        default="(default)",
        description="Firestore database ID",
    )
    use_firestore_emulator: bool = Field(
        default=False,
        description="Use Firestore emulator for local development",
    )
    firestore_emulator_host: str = Field(
        default="localhost:9099",
        description="Firestore emulator host",
    )

    # Firebase Realtime Database
    realtime_database_url: str = Field(
        default="",
        description="Firebase Realtime Database URL (e.g., https://your-project.firebaseio.com)",
    )

    # External Services
    agent_url: str = Field(
        default="http://0.0.0.0:8081",
        description="Symptom checker agent service URL",
    )

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_json_format: bool = Field(
        default=False,
        description="Use JSON format for logs",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid Python logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION


def load_settings_for_environment(env: str | None = None) -> Settings:
    """
    Load settings with environment-specific overrides.

    Args:
        env: Environment name (development, staging, production).
             If None, uses ENVIRONMENT env var or defaults to development.

    Returns:
        Settings instance with merged configuration.
    """
    import os

    # Determine environment
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")

    # Build list of env files to load (in order of precedence)
    env_files = []
    base_env = Path(".env")
    env_specific = Path(f".env.{env}")

    if base_env.exists():
        env_files.append(base_env)
    if env_specific.exists():
        env_files.append(env_specific)

    # Load settings with the last file taking precedence
    if env_files:
        # Pydantic loads files in order, later files override earlier ones
        return Settings(_env_file=tuple(str(f) for f in env_files))

    return Settings()


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return load_settings_for_environment()


# Export for convenience
settings = get_settings()

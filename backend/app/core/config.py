"""Application configuration using pydantic-settings.

This module provides centralized configuration management:
- Environment variable loading from .env file
- Type-safe settings with validation
- Cached settings instance with @lru_cache
- Settings for application, CORS, and future database configuration
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration.

    All settings can be overridden via environment variables.
    Environment variables are case-insensitive.
    Settings are loaded from .env file if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Don't fail if .env file doesn't exist
        extra="ignore",
    )

    # Application metadata
    app_name: str = "AI Foundation for Agentic AI Workflows"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api"

    # Database
    database_url: str

    # CORS settings
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8123"]

    # JWT settings
    jwt_secret_key: str = ""  # Required in production, set via JWT_SECRET_KEY env var
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # OAuth settings (optional - only needed if OAuth enabled)
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    oauth_redirect_base_url: str = "http://localhost:8123"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    The @lru_cache decorator ensures settings are only loaded once
    and reused across the application lifecycle.

    Returns:
        The application settings instance.
    """
    # pydantic-settings automatically loads required fields (like database_url)
    # from environment variables at runtime. Mypy's static analysis doesn't understand
    # this behavior and expects all required fields as constructor arguments. This is
    # a known limitation of mypy with pydantic-settings. The call-arg error is suppressed
    # as the runtime behavior is correct and type-safe.
    return Settings()  # type: ignore[call-arg]

"""
Application Settings using Pydantic Settings.
Configuration is loaded from environment variables.
"""
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "Sumeria Personal Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    # MCP Server
    mcp_server_name: str = "Sumeria MCP Server"
    mcp_transport: str = "stdio"  # stdio or streamable-http

    # Gmail OAuth2 - Multi-account support
    gmail_credentials_file: Optional[Path] = Field(
        default=None,
        description="Path to Google OAuth2 credentials JSON file"
    )
    gmail_tokens_dir: Path = Field(
        default=Path("tokens"),
        description="Directory to store OAuth2 tokens for multiple accounts"
    )
    gmail_scopes: list[str] = Field(
        default=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
        ],
        description="Gmail API scopes"
    )
    gmail_default_account: Optional[str] = Field(
        default=None,
        description="Default Gmail account identifier (email or alias)"
    )

    # Redis (for caching)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Database (for future use)
    database_url: str = "sqlite:///./sumeria.db"

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"


# Global settings instance
settings = Settings()

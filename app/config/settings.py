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

    # Holded API
    holded_api_key: Optional[str] = Field(
        default=None,
        description="Holded API key for authentication"
    )
    holded_api_base_url: str = Field(
        default="https://api.holded.com",
        description="Holded API base URL"
    )

    # Notion API
    notion_api_key: Optional[str] = Field(
        default=None,
        description="Notion API key for authentication"
    )
    notion_api_version: str = Field(
        default="2022-06-28",
        description="Notion API version"
    )

    # WhatsApp Business Cloud API
    whatsapp_access_token: Optional[str] = Field(
        default=None,
        description="WhatsApp Cloud API access token"
    )
    whatsapp_phone_number_id: Optional[str] = Field(
        default=None,
        description="WhatsApp Business phone number ID"
    )
    whatsapp_business_account_id: Optional[str] = Field(
        default=None,
        description="WhatsApp Business account ID"
    )
    whatsapp_webhook_verify_token: Optional[str] = Field(
        default=None,
        description="Webhook verification token for WhatsApp"
    )
    whatsapp_app_secret: Optional[str] = Field(
        default=None,
        description="App secret for webhook signature verification"
    )
    whatsapp_api_version: str = Field(
        default="v21.0",
        description="WhatsApp Cloud API version"
    )
    whatsapp_api_base_url: str = Field(
        default="https://graph.facebook.com",
        description="WhatsApp Cloud API base URL"
    )

    # Google Calendar - Multi-account support
    google_calendar_credentials_file: Optional[Path] = Field(
        default=None,
        description="Path to Google Calendar OAuth2 credentials JSON file"
    )
    google_calendar_tokens_dir: Path = Field(
        default=Path("tokens/google_calendar"),
        description="Directory to store Google Calendar OAuth2 tokens for multiple accounts"
    )
    google_calendar_scopes: list[str] = Field(
        default=[
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
        ],
        description="Google Calendar API scopes"
    )
    google_calendar_default_account: Optional[str] = Field(
        default=None,
        description="Default Google Calendar account identifier (email or alias)"
    )

    # Apple Calendar (CalDAV)
    apple_calendar_url: Optional[str] = Field(
        default=None,
        description="Apple Calendar CalDAV URL (e.g., https://caldav.icloud.com)"
    )
    apple_calendar_username: Optional[str] = Field(
        default=None,
        description="Apple ID for CalDAV access"
    )
    apple_calendar_password: Optional[str] = Field(
        default=None,
        description="App-specific password for CalDAV"
    )
    apple_calendar_tokens_dir: Path = Field(
        default=Path("tokens/apple_calendar"),
        description="Directory to store Apple Calendar credentials"
    )


# Global settings instance
settings = Settings()

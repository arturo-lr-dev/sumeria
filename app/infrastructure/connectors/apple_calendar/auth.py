"""
Apple Calendar (CalDAV) authentication handler.
Uses app-specific passwords for iCloud.
"""
from pathlib import Path
from typing import Optional
import json
from app.config.settings import settings


class AppleCalendarAuthHandler:
    """Handles authentication for Apple Calendar (CalDAV)."""

    def __init__(
        self,
        account_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        caldav_url: Optional[str] = None,
        tokens_dir: Optional[Path] = None
    ):
        """
        Initialize auth handler for Apple Calendar.

        Args:
            account_id: Account identifier
            username: Apple ID (email)
            password: App-specific password
            caldav_url: CalDAV server URL
            tokens_dir: Directory to store credentials
        """
        self.account_id = account_id
        self.username = username or settings.apple_calendar_username
        self.password = password or settings.apple_calendar_password
        self.caldav_url = caldav_url or settings.apple_calendar_url or "https://caldav.icloud.com"
        self.tokens_dir = tokens_dir or settings.apple_calendar_tokens_dir

    def _ensure_tokens_dir(self) -> None:
        """Ensure tokens directory exists."""
        self.tokens_dir.mkdir(parents=True, exist_ok=True)

    @property
    def credentials_file(self) -> Path:
        """Get the credentials file path for this account."""
        safe_account_id = self.account_id.replace('@', '_at_').replace('.', '_')
        return self.tokens_dir / f"credentials_{safe_account_id}.json"

    def save_credentials(self, username: str, password: str, url: str) -> None:
        """
        Save CalDAV credentials.

        Args:
            username: Apple ID
            password: App-specific password
            url: CalDAV URL
        """
        self._ensure_tokens_dir()
        credentials = {
            'username': username,
            'password': password,
            'url': url
        }
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f)

    def load_credentials(self) -> tuple[str, str, str]:
        """
        Load saved credentials.

        Returns:
            Tuple of (username, password, url)

        Raises:
            ValueError: If no credentials available
        """
        if self.credentials_file.exists():
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)
                return creds['username'], creds['password'], creds['url']

        if self.username and self.password:
            return self.username, self.password, self.caldav_url

        raise ValueError("No credentials available for Apple Calendar")

    def revoke_credentials(self) -> None:
        """Delete stored credentials."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()

    @property
    def is_authenticated(self) -> bool:
        """
        Check if credentials are available.

        Returns:
            True if credentials exist
        """
        try:
            self.load_credentials()
            return True
        except ValueError:
            return False

    @staticmethod
    def list_authenticated_accounts(tokens_dir: Optional[Path] = None) -> list[str]:
        """
        List all authenticated accounts.

        Args:
            tokens_dir: Directory where credentials are stored

        Returns:
            List of account identifiers
        """
        tokens_dir = tokens_dir or settings.apple_calendar_tokens_dir

        if not tokens_dir.exists():
            return []

        accounts = []
        for creds_file in tokens_dir.glob("credentials_*.json"):
            account_id = creds_file.stem.replace('credentials_', '').replace('_at_', '@').replace('_', '.')
            accounts.append(account_id)

        return accounts

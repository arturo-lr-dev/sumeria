"""
Gmail OAuth2 authentication handler with multi-account support.
"""
import os
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from app.config.settings import settings


class GmailOAuthHandler:
    """Handles OAuth2 authentication for Gmail API with multi-account support."""

    def __init__(
        self,
        account_id: str,
        credentials_file: Optional[Path] = None,
        tokens_dir: Optional[Path] = None,
        scopes: Optional[list[str]] = None
    ):
        """
        Initialize OAuth handler for a specific account.

        Args:
            account_id: Unique identifier for the account (email or alias)
            credentials_file: Path to OAuth2 credentials JSON from Google Cloud Console
            tokens_dir: Directory where to store/load tokens for all accounts
            scopes: Gmail API scopes to request
        """
        self.account_id = account_id
        self.credentials_file = credentials_file or settings.gmail_credentials_file
        self.tokens_dir = tokens_dir or settings.gmail_tokens_dir
        self.scopes = scopes or settings.gmail_scopes
        self._creds: Optional[Credentials] = None

        # Create tokens directory if it doesn't exist
        self.tokens_dir.mkdir(parents=True, exist_ok=True)

    @property
    def token_file(self) -> Path:
        """Get the token file path for this account."""
        # Sanitize account_id for filename
        safe_account_id = self.account_id.replace('@', '_at_').replace('.', '_')
        return self.tokens_dir / f"token_{safe_account_id}.json"

    def get_credentials(self) -> Credentials:
        """
        Get valid credentials, refreshing or requesting new ones if needed.

        Returns:
            Valid OAuth2 credentials

        Raises:
            FileNotFoundError: If credentials file is not found
            ValueError: If credentials cannot be obtained
        """
        # Load existing token if available
        if self.token_file.exists():
            self._creds = Credentials.from_authorized_user_file(
                str(self.token_file),
                self.scopes
            )

        # Refresh or get new credentials if needed
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                # Refresh expired credentials
                self._creds.refresh(Request())
            else:
                # Get new credentials through OAuth flow
                if not self.credentials_file or not self.credentials_file.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}. "
                        "Please download it from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file),
                    self.scopes
                )
                print(f"\nAuthenticating account: {self.account_id}")
                print("Please follow the browser instructions to authorize access.\n")
                self._creds = flow.run_local_server(port=0)

            # Save credentials for future use
            self._save_credentials()

        return self._creds

    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        if self._creds:
            with open(self.token_file, 'w') as token:
                token.write(self._creds.to_json())

    def revoke_credentials(self) -> None:
        """Revoke and delete stored credentials for this account."""
        if self._creds:
            self._creds = None

        if self.token_file.exists():
            os.remove(self.token_file)

    @property
    def is_authenticated(self) -> bool:
        """Check if valid credentials are available."""
        try:
            creds = self.get_credentials()
            return creds.valid
        except Exception:
            return False

    @staticmethod
    def list_authenticated_accounts(tokens_dir: Optional[Path] = None) -> list[str]:
        """
        List all authenticated accounts.

        Args:
            tokens_dir: Directory where tokens are stored

        Returns:
            List of account identifiers
        """
        tokens_dir = tokens_dir or settings.gmail_tokens_dir

        if not tokens_dir.exists():
            return []

        accounts = []
        for token_file in tokens_dir.glob("token_*.json"):
            # Extract account ID from filename
            account_id = token_file.stem.replace('token_', '').replace('_at_', '@').replace('_', '.')
            accounts.append(account_id)

        return accounts

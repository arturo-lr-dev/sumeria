"""
Gmail account manager for handling multiple accounts.
"""
from typing import Optional, Dict
from app.infrastructure.connectors.gmail.client import GmailClient
from app.infrastructure.connectors.gmail.oauth import GmailOAuthHandler
from app.config.settings import settings


class GmailAccountManager:
    """
    Manages multiple Gmail accounts.
    Provides a central point to access different Gmail clients.
    """

    def __init__(self):
        """Initialize the account manager."""
        self._clients: Dict[str, GmailClient] = {}
        self._default_account = settings.gmail_default_account

    def get_client(self, account_id: Optional[str] = None) -> GmailClient:
        """
        Get Gmail client for a specific account.

        Args:
            account_id: Account identifier (email or alias). If None, uses default account.

        Returns:
            GmailClient instance for the account

        Raises:
            ValueError: If no account_id provided and no default account configured
        """
        # Use default account if none specified
        if account_id is None:
            if self._default_account is None:
                raise ValueError(
                    "No account_id provided and no default account configured. "
                    "Set GMAIL_DEFAULT_ACCOUNT in environment or .env file."
                )
            account_id = self._default_account

        # Return existing client or create new one
        if account_id not in self._clients:
            self._clients[account_id] = GmailClient(account_id=account_id)

        return self._clients[account_id]

    def add_account(self, account_id: str) -> GmailClient:
        """
        Add a new account and authenticate it.

        Args:
            account_id: Account identifier (email or alias)

        Returns:
            GmailClient instance for the new account
        """
        oauth_handler = GmailOAuthHandler(account_id=account_id)

        # Trigger authentication flow
        oauth_handler.get_credentials()

        # Create and store client
        client = GmailClient(account_id=account_id, oauth_handler=oauth_handler)
        self._clients[account_id] = client

        return client

    def remove_account(self, account_id: str) -> None:
        """
        Remove an account and revoke its credentials.

        Args:
            account_id: Account identifier to remove
        """
        if account_id in self._clients:
            # Revoke credentials
            self._clients[account_id].oauth_handler.revoke_credentials()

            # Remove from cache
            del self._clients[account_id]

    def list_accounts(self) -> list[str]:
        """
        List all authenticated accounts.

        Returns:
            List of account identifiers
        """
        return GmailOAuthHandler.list_authenticated_accounts()

    def set_default_account(self, account_id: str) -> None:
        """
        Set the default account.

        Args:
            account_id: Account identifier to set as default
        """
        # Verify account exists
        if account_id not in self.list_accounts():
            raise ValueError(
                f"Account '{account_id}' not found. "
                f"Add the account first using add_account()."
            )

        self._default_account = account_id

    @property
    def default_account(self) -> Optional[str]:
        """Get the current default account."""
        return self._default_account


# Global instance
gmail_account_manager = GmailAccountManager()

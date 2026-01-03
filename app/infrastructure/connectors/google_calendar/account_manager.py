"""
Multi-account manager for Google Calendar.
Similar to Gmail account manager pattern.
"""
from typing import Optional, Dict
from app.infrastructure.connectors.google_calendar.client import GoogleCalendarClient


class GoogleCalendarAccountManager:
    """Manages multiple Google Calendar accounts."""

    def __init__(self):
        """Initialize account manager."""
        self._clients: Dict[str, GoogleCalendarClient] = {}
        self._default_account: Optional[str] = None

    def add_account(self, account_id: str) -> GoogleCalendarClient:
        """
        Add or get calendar client for an account.

        Args:
            account_id: Account identifier (email or alias)

        Returns:
            GoogleCalendarClient for the account
        """
        if account_id not in self._clients:
            self._clients[account_id] = GoogleCalendarClient(account_id=account_id)

            if self._default_account is None:
                self._default_account = account_id

        return self._clients[account_id]

    def get_client(self, account_id: Optional[str] = None) -> GoogleCalendarClient:
        """
        Get client for specific account or default.

        Args:
            account_id: Account identifier (uses default if None)

        Returns:
            GoogleCalendarClient for the account

        Raises:
            ValueError: If no default account is set and account_id is None
        """
        if account_id is None:
            account_id = self._default_account

        if account_id is None:
            raise ValueError("No default account set and no account_id provided")

        if account_id not in self._clients:
            return self.add_account(account_id)

        return self._clients[account_id]

    def set_default_account(self, account_id: str) -> None:
        """
        Set default account.

        Args:
            account_id: Account identifier to set as default
        """
        if account_id not in self._clients:
            self.add_account(account_id)
        self._default_account = account_id

    def list_accounts(self) -> list[str]:
        """
        List all configured accounts.

        Returns:
            List of account identifiers
        """
        return list(self._clients.keys())

    def remove_account(self, account_id: str) -> None:
        """
        Remove an account.

        Args:
            account_id: Account identifier to remove
        """
        if account_id in self._clients:
            del self._clients[account_id]

            if self._default_account == account_id:
                self._default_account = None


# Global instance
google_calendar_account_manager = GoogleCalendarAccountManager()

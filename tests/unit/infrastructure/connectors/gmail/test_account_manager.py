"""
Unit tests for Gmail account manager.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.infrastructure.connectors.gmail.account_manager import GmailAccountManager
from app.infrastructure.connectors.gmail.client import GmailClient


class TestGmailAccountManager:
    """Test suite for GmailAccountManager."""

    @pytest.fixture
    def account_manager(self):
        """Create fresh account manager instance."""
        manager = GmailAccountManager()
        manager._clients = {}  # Clear any existing clients
        return manager

    @pytest.fixture(autouse=True)
    def mock_settings(self):
        """Mock settings."""
        with patch('app.infrastructure.connectors.gmail.account_manager.settings') as mock_settings:
            mock_settings.gmail_default_account = "default@example.com"
            yield mock_settings

    def test_init(self, account_manager):
        """Test account manager initialization."""
        assert account_manager._clients == {}

    @patch('app.infrastructure.connectors.gmail.account_manager.GmailClient')
    def test_get_client_creates_new_client(self, mock_client_class, account_manager):
        """Test that get_client creates new client if not exists."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = account_manager.get_client("test@example.com")

        assert client == mock_client
        mock_client_class.assert_called_once_with(account_id="test@example.com")
        assert account_manager._clients["test@example.com"] == mock_client

    @patch('app.infrastructure.connectors.gmail.account_manager.GmailClient')
    def test_get_client_reuses_existing_client(self, mock_client_class, account_manager):
        """Test that get_client reuses existing client."""
        mock_client = MagicMock()
        account_manager._clients["test@example.com"] = mock_client

        client = account_manager.get_client("test@example.com")

        assert client == mock_client
        mock_client_class.assert_not_called()

    @patch('app.infrastructure.connectors.gmail.account_manager.GmailClient')
    def test_get_client_uses_default_account(self, mock_client_class, account_manager, mock_settings):
        """Test that get_client uses default account when none specified."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = account_manager.get_client()

        mock_client_class.assert_called_once_with(account_id="default@example.com")

    def test_get_client_no_account_no_default_raises_error(self, account_manager):
        """Test that get_client raises error when no account and no default."""
        account_manager._default_account = None

        with pytest.raises(ValueError) as exc_info:
            account_manager.get_client()

        assert "No account_id provided" in str(exc_info.value)

    @patch('app.infrastructure.connectors.gmail.account_manager.GmailOAuthHandler')
    @patch('app.infrastructure.connectors.gmail.account_manager.GmailClient')
    def test_add_account(self, mock_client_class, mock_oauth_class, account_manager):
        """Test adding a new account."""
        mock_oauth = MagicMock()
        mock_oauth_class.return_value = mock_oauth

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        client = account_manager.add_account("new@example.com")

        # Should trigger authentication
        mock_oauth_class.assert_called_once_with(account_id="new@example.com")
        mock_oauth.get_credentials.assert_called_once()

        # Should create and store client
        mock_client_class.assert_called_once_with(
            account_id="new@example.com",
            oauth_handler=mock_oauth
        )
        assert account_manager._clients["new@example.com"] == mock_client
        assert client == mock_client

    def test_remove_account(self, account_manager):
        """Test removing an account."""
        # Add a mock client
        mock_client = MagicMock()
        mock_oauth = MagicMock()
        mock_client.oauth_handler = mock_oauth
        account_manager._clients["test@example.com"] = mock_client

        account_manager.remove_account("test@example.com")

        # Should revoke credentials
        mock_oauth.revoke_credentials.assert_called_once()

        # Should remove from cache
        assert "test@example.com" not in account_manager._clients

    def test_remove_account_not_exists(self, account_manager):
        """Test removing account that doesn't exist."""
        # Should not raise error
        account_manager.remove_account("nonexistent@example.com")

        assert "nonexistent@example.com" not in account_manager._clients

    @patch('app.infrastructure.connectors.gmail.account_manager.GmailOAuthHandler')
    def test_list_accounts(self, mock_oauth_class, account_manager):
        """Test listing authenticated accounts."""
        mock_oauth_class.list_authenticated_accounts.return_value = [
            "account1@example.com",
            "account2@example.com"
        ]

        accounts = account_manager.list_accounts()

        assert len(accounts) == 2
        assert "account1@example.com" in accounts
        assert "account2@example.com" in accounts

    def test_set_default_account_success(self, account_manager):
        """Test setting default account."""
        with patch.object(account_manager, 'list_accounts', return_value=["test@example.com"]):
            account_manager.set_default_account("test@example.com")

            assert account_manager._default_account == "test@example.com"

    def test_set_default_account_not_found(self, account_manager):
        """Test setting default account that doesn't exist."""
        with patch.object(account_manager, 'list_accounts', return_value=[]):
            with pytest.raises(ValueError) as exc_info:
                account_manager.set_default_account("nonexistent@example.com")

            assert "not found" in str(exc_info.value)

    def test_default_account_property(self, account_manager, mock_settings):
        """Test default_account property."""
        assert account_manager.default_account == "default@example.com"

        account_manager._default_account = "custom@example.com"
        assert account_manager.default_account == "custom@example.com"

    @patch('app.infrastructure.connectors.gmail.account_manager.GmailClient')
    def test_multiple_accounts_independent(self, mock_client_class, account_manager):
        """Test that multiple accounts are managed independently."""
        mock_client1 = MagicMock()
        mock_client2 = MagicMock()

        def create_client(account_id):
            if account_id == "account1@example.com":
                return mock_client1
            return mock_client2

        mock_client_class.side_effect = create_client

        client1 = account_manager.get_client("account1@example.com")
        client2 = account_manager.get_client("account2@example.com")

        assert client1 != client2
        assert account_manager._clients["account1@example.com"] == mock_client1
        assert account_manager._clients["account2@example.com"] == mock_client2

    def test_account_manager_singleton_behavior(self):
        """Test that global instance works correctly."""
        from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager

        assert isinstance(gmail_account_manager, GmailAccountManager)

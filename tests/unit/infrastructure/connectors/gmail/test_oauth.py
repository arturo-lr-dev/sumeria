"""
Unit tests for Gmail OAuth handler.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from google.oauth2.credentials import Credentials
from app.infrastructure.connectors.gmail.oauth import GmailOAuthHandler


class TestGmailOAuthHandler:
    """Test suite for GmailOAuthHandler."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for tokens."""
        return tmp_path / "tokens"

    @pytest.fixture
    def credentials_file(self, tmp_path):
        """Create temporary credentials file."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text('{"client_id": "test", "client_secret": "secret"}')
        return creds_file

    @pytest.fixture
    def oauth_handler(self, temp_dir, credentials_file):
        """Create OAuth handler instance."""
        return GmailOAuthHandler(
            account_id="test@example.com",
            credentials_file=credentials_file,
            tokens_dir=temp_dir
        )

    def test_init(self, oauth_handler, credentials_file, temp_dir):
        """Test OAuth handler initialization."""
        assert oauth_handler.account_id == "test@example.com"
        assert oauth_handler.credentials_file == credentials_file
        assert oauth_handler.tokens_dir == temp_dir
        assert oauth_handler._creds is None

    def test_token_file_path(self, oauth_handler, temp_dir):
        """Test token file path generation."""
        expected_path = temp_dir / "token_test_at_example_com.json"
        assert oauth_handler.token_file == expected_path

    def test_token_file_path_sanitization(self, temp_dir, credentials_file):
        """Test account ID sanitization in token filename."""
        handler = GmailOAuthHandler(
            account_id="user.name@example.co.uk",
            credentials_file=credentials_file,
            tokens_dir=temp_dir
        )

        # Should replace @ and .
        assert "user_name_at_example_co_uk" in str(handler.token_file)

    @patch('app.infrastructure.connectors.gmail.oauth.Credentials')
    def test_get_credentials_from_existing_token(self, mock_creds_class, oauth_handler, temp_dir):
        """Test getting credentials from existing valid token."""
        # Create token file
        token_file = oauth_handler.token_file
        temp_dir.mkdir(parents=True, exist_ok=True)
        token_file.write_text('{"token": "test_token"}')

        # Mock valid credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        credentials = oauth_handler.get_credentials()

        assert credentials == mock_creds
        mock_creds_class.from_authorized_user_file.assert_called_once()

    @patch('app.infrastructure.connectors.gmail.oauth.Credentials')
    @patch('app.infrastructure.connectors.gmail.oauth.Request')
    def test_get_credentials_refresh_expired(self, mock_request, mock_creds_class, oauth_handler, temp_dir):
        """Test refreshing expired credentials."""
        # Create token file
        token_file = oauth_handler.token_file
        temp_dir.mkdir(parents=True, exist_ok=True)
        token_file.write_text('{"token": "test_token"}')

        # Mock expired credentials
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"
        mock_creds.to_json.return_value = '{"token": "refreshed_token"}'
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        # After refresh, credentials become valid
        def refresh_side_effect(*args):
            mock_creds.valid = True

        mock_creds.refresh.side_effect = refresh_side_effect

        credentials = oauth_handler.get_credentials()

        assert credentials == mock_creds
        mock_creds.refresh.assert_called_once()

    @patch('app.infrastructure.connectors.gmail.oauth.InstalledAppFlow')
    def test_get_credentials_new_auth_flow(self, mock_flow_class, oauth_handler, credentials_file):
        """Test new OAuth flow when no token exists."""
        # Mock flow
        mock_flow = MagicMock()
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_class.from_client_secrets_file.return_value = mock_flow

        with patch('builtins.open', mock_open()):
            credentials = oauth_handler.get_credentials()

        assert credentials == mock_creds
        mock_flow_class.from_client_secrets_file.assert_called_once()
        mock_flow.run_local_server.assert_called_once()

    def test_get_credentials_missing_credentials_file(self, temp_dir):
        """Test error when credentials file is missing."""
        handler = GmailOAuthHandler(
            account_id="test@example.com",
            credentials_file=Path("/nonexistent/credentials.json"),
            tokens_dir=temp_dir
        )

        with pytest.raises(FileNotFoundError):
            handler.get_credentials()

    def test_save_credentials(self, oauth_handler, temp_dir):
        """Test saving credentials to file."""
        temp_dir.mkdir(parents=True, exist_ok=True)

        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "test"}'
        oauth_handler._creds = mock_creds

        with patch('builtins.open', mock_open()) as mock_file:
            oauth_handler._save_credentials()
            mock_file.assert_called_once()

    def test_revoke_credentials(self, oauth_handler, temp_dir):
        """Test revoking credentials."""
        # Create token file
        temp_dir.mkdir(parents=True, exist_ok=True)
        token_file = oauth_handler.token_file
        token_file.write_text('{"token": "test"}')

        oauth_handler._creds = MagicMock()
        oauth_handler.revoke_credentials()

        assert oauth_handler._creds is None
        assert not token_file.exists()

    @patch('app.infrastructure.connectors.gmail.oauth.Credentials')
    def test_is_authenticated_true(self, mock_creds_class, oauth_handler, temp_dir):
        """Test is_authenticated when credentials are valid."""
        temp_dir.mkdir(parents=True, exist_ok=True)
        oauth_handler.token_file.write_text('{"token": "test"}')

        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        assert oauth_handler.is_authenticated is True

    def test_is_authenticated_false(self, oauth_handler):
        """Test is_authenticated when credentials are invalid."""
        # No token file exists
        assert oauth_handler.is_authenticated is False

    @patch('app.infrastructure.connectors.gmail.oauth.settings')
    def test_list_authenticated_accounts(self, mock_settings, temp_dir):
        """Test listing authenticated accounts."""
        temp_dir.mkdir(parents=True, exist_ok=True)
        mock_settings.gmail_tokens_dir = temp_dir

        # Create some token files
        (temp_dir / "token_user1_at_example_com.json").write_text("{}")
        (temp_dir / "token_user2_at_test_com.json").write_text("{}")

        accounts = GmailOAuthHandler.list_authenticated_accounts(tokens_dir=temp_dir)

        assert len(accounts) == 2
        assert "user1@example.com" in accounts
        assert "user2@test.com" in accounts

    def test_list_authenticated_accounts_empty(self, temp_dir):
        """Test listing accounts when none exist."""
        accounts = GmailOAuthHandler.list_authenticated_accounts(tokens_dir=temp_dir)

        assert len(accounts) == 0

    @patch('app.infrastructure.connectors.gmail.oauth.settings')
    def test_uses_settings_defaults(self, mock_settings):
        """Test that handler uses settings defaults."""
        mock_settings.gmail_credentials_file = Path("/default/creds.json")
        mock_settings.gmail_tokens_dir = Path("/default/tokens")
        mock_settings.gmail_scopes = ["scope1", "scope2"]

        handler = GmailOAuthHandler(account_id="test@example.com")

        assert handler.credentials_file == mock_settings.gmail_credentials_file
        assert handler.tokens_dir == mock_settings.gmail_tokens_dir
        assert handler.scopes == mock_settings.gmail_scopes

    def test_tokens_directory_creation(self, tmp_path, credentials_file):
        """Test that tokens directory is created if it doesn't exist."""
        tokens_dir = tmp_path / "new_tokens_dir"
        assert not tokens_dir.exists()

        handler = GmailOAuthHandler(
            account_id="test@example.com",
            credentials_file=credentials_file,
            tokens_dir=tokens_dir
        )

        assert tokens_dir.exists()
        assert tokens_dir.is_dir()

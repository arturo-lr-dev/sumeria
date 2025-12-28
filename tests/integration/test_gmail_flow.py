"""
Integration tests for Gmail complete flows.
These tests verify end-to-end functionality of Gmail features.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.mcp.tools.gmail_tools import GmailTools
from app.infrastructure.connectors.gmail.account_manager import GmailAccountManager
from tests.fixtures.gmail_fixtures import (
    SAMPLE_GMAIL_MESSAGE,
    SAMPLE_SEARCH_RESULTS,
    create_sample_email
)


@pytest.fixture
def mock_gmail_service():
    """Create mock Gmail API service."""
    service = MagicMock()
    return service


@pytest.fixture
def mock_oauth_handler():
    """Create mock OAuth handler."""
    handler = MagicMock()
    mock_creds = MagicMock()
    mock_creds.valid = True
    handler.get_credentials.return_value = mock_creds
    return handler


class TestGmailIntegrationFlow:
    """Integration tests for complete Gmail workflows."""

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.build')
    async def test_send_email_flow(self, mock_build, mock_gmail_service, mock_oauth_handler):
        """Test complete email sending flow from MCP tools to Gmail API."""
        mock_build.return_value = mock_gmail_service

        # Mock service response
        mock_send = MagicMock()
        mock_send.execute.return_value = {"id": "sent_msg_123"}
        mock_gmail_service.users().messages().send.return_value = mock_send

        # Create tools and execute
        tools = GmailTools()

        with patch('app.infrastructure.connectors.gmail.account_manager.GmailClient') as mock_client_class:
            # Create real client with mocked service
            from app.infrastructure.connectors.gmail.client import GmailClient
            real_client = GmailClient(
                account_id="test@example.com",
                oauth_handler=mock_oauth_handler
            )
            real_client._service = mock_gmail_service

            with patch.object(
                tools.send_email_uc,
                'execute',
                wraps=tools.send_email_uc.execute
            ):
                with patch(
                    'app.application.use_cases.gmail.send_email.gmail_account_manager.get_client',
                    return_value=real_client
                ):
                    result = await tools.send_email(
                        to=["recipient@example.com"],
                        subject="Integration Test",
                        body_text="This is a test email"
                    )

                    assert result.success is True
                    assert result.message_id == "sent_msg_123"

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.build')
    async def test_search_and_get_email_flow(self, mock_build, mock_gmail_service, mock_oauth_handler):
        """Test complete search and retrieve email flow."""
        mock_build.return_value = mock_gmail_service

        # Mock search response
        mock_list = MagicMock()
        mock_list.execute.return_value = SAMPLE_SEARCH_RESULTS
        mock_gmail_service.users().messages().list.return_value = mock_list

        # Mock get response
        mock_get = MagicMock()
        mock_get.execute.return_value = SAMPLE_GMAIL_MESSAGE
        mock_gmail_service.users().messages().get.return_value = mock_get

        tools = GmailTools()

        from app.infrastructure.connectors.gmail.client import GmailClient
        real_client = GmailClient(
            account_id="test@example.com",
            oauth_handler=mock_oauth_handler
        )
        real_client._service = mock_gmail_service

        with patch(
            'app.application.use_cases.gmail.search_emails.gmail_account_manager.get_client',
            return_value=real_client
        ):
            # Search emails
            search_result = await tools.search_emails(
                from_address="sender@example.com",
                max_results=10
            )

            assert search_result.success is True
            assert search_result.count == 2

        with patch(
            'app.application.use_cases.gmail.get_email.gmail_account_manager.get_client',
            return_value=real_client
        ):
            # Get first email
            email_id = search_result.emails[0].id
            get_result = await tools.get_email(message_id=email_id)

            assert get_result.success is True
            assert get_result.email is not None

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.build')
    async def test_mark_as_read_flow(self, mock_build, mock_gmail_service, mock_oauth_handler):
        """Test complete mark as read flow."""
        mock_build.return_value = mock_gmail_service

        # Mock modify response
        mock_modify = MagicMock()
        mock_modify.execute.return_value = {}
        mock_gmail_service.users().messages().modify.return_value = mock_modify

        tools = GmailTools()

        from app.infrastructure.connectors.gmail.client import GmailClient
        real_client = GmailClient(
            account_id="test@example.com",
            oauth_handler=mock_oauth_handler
        )
        real_client._service = mock_gmail_service

        with patch(
            'app.application.use_cases.gmail.manage_labels.gmail_account_manager.get_client',
            return_value=real_client
        ):
            result = await tools.mark_as_read(message_id="msg123")

            assert result["success"] is True
            mock_gmail_service.users().messages().modify.assert_called_once_with(
                userId='me',
                id='msg123',
                body={'removeLabelIds': ['UNREAD']}
            )

    @pytest.mark.asyncio
    async def test_account_manager_multi_account_flow(self, mock_oauth_handler):
        """Test managing multiple Gmail accounts."""
        manager = GmailAccountManager()
        manager._clients = {}  # Reset

        with patch('app.infrastructure.connectors.gmail.account_manager.GmailClient') as mock_client_class:
            mock_client1 = MagicMock()
            mock_client2 = MagicMock()

            def create_client(account_id, **kwargs):
                if account_id == "account1@example.com":
                    return mock_client1
                return mock_client2

            mock_client_class.side_effect = create_client

            # Get clients for different accounts
            client1 = manager.get_client("account1@example.com")
            client2 = manager.get_client("account2@example.com")

            assert client1 == mock_client1
            assert client2 == mock_client2
            assert len(manager._clients) == 2

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.build')
    async def test_error_handling_flow(self, mock_build, mock_gmail_service, mock_oauth_handler):
        """Test error handling in complete flow."""
        mock_build.return_value = mock_gmail_service

        # Mock service to raise error
        from googleapiclient.errors import HttpError
        mock_gmail_service.users().messages().send.side_effect = HttpError(
            resp=MagicMock(status=400),
            content=b"Bad request"
        )

        tools = GmailTools()

        from app.infrastructure.connectors.gmail.client import GmailClient
        real_client = GmailClient(
            account_id="test@example.com",
            oauth_handler=mock_oauth_handler
        )
        real_client._service = mock_gmail_service

        with patch(
            'app.application.use_cases.gmail.send_email.gmail_account_manager.get_client',
            return_value=real_client
        ):
            result = await tools.send_email(
                to=["recipient@example.com"],
                subject="Test",
                body_text="Body"
            )

            # Should handle error gracefully
            assert result.success is False
            assert result.error is not None

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.build')
    async def test_label_management_flow(self, mock_build, mock_gmail_service, mock_oauth_handler):
        """Test complete label management flow."""
        mock_build.return_value = mock_gmail_service

        # Mock modify responses
        mock_modify = MagicMock()
        mock_modify.execute.return_value = {}
        mock_gmail_service.users().messages().modify.return_value = mock_modify

        tools = GmailTools()

        from app.infrastructure.connectors.gmail.client import GmailClient
        real_client = GmailClient(
            account_id="test@example.com",
            oauth_handler=mock_oauth_handler
        )
        real_client._service = mock_gmail_service

        with patch(
            'app.application.use_cases.gmail.manage_labels.gmail_account_manager.get_client',
            return_value=real_client
        ):
            # Mark as unread
            result1 = await tools.mark_as_unread(message_id="msg123")
            assert result1["success"] is True

            # Add label
            result2 = await tools.add_label(message_id="msg123", label="STARRED")
            assert result2["success"] is True

            # Mark as read
            result3 = await tools.mark_as_read(message_id="msg123")
            assert result3["success"] is True

            # Verify all operations were called
            assert mock_gmail_service.users().messages().modify.call_count == 3

"""
Unit tests for Gmail API client.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from googleapiclient.errors import HttpError
from app.infrastructure.connectors.gmail.client import GmailClient
from app.domain.entities.email import EmailDraft, EmailAddress, EmailSearchCriteria
from tests.fixtures.gmail_fixtures import (
    SAMPLE_GMAIL_MESSAGE,
    SAMPLE_SEARCH_RESULTS,
    EMPTY_SEARCH_RESULTS,
    create_sample_draft
)


@pytest.fixture
def mock_oauth_handler():
    """Create mock OAuth handler."""
    handler = MagicMock()
    mock_creds = MagicMock()
    handler.get_credentials.return_value = mock_creds
    return handler


@pytest.fixture
def mock_service():
    """Create mock Gmail service."""
    return MagicMock()


@pytest.fixture
def gmail_client(mock_oauth_handler):
    """Create Gmail client instance with mocked OAuth."""
    return GmailClient(
        account_id="test@example.com",
        oauth_handler=mock_oauth_handler
    )


class TestGmailClient:
    """Test suite for GmailClient."""

    def test_init(self, mock_oauth_handler):
        """Test Gmail client initialization."""
        client = GmailClient(
            account_id="test@example.com",
            oauth_handler=mock_oauth_handler
        )

        assert client.account_id == "test@example.com"
        assert client.oauth_handler == mock_oauth_handler
        assert client._service is None

    def test_init_creates_oauth_handler(self):
        """Test that OAuth handler is created if not provided."""
        with patch('app.infrastructure.connectors.gmail.client.GmailOAuthHandler') as mock_handler_class:
            client = GmailClient(account_id="test@example.com")

            mock_handler_class.assert_called_once_with(account_id="test@example.com")

    @patch('app.infrastructure.connectors.gmail.client.build')
    def test_get_service_creates_service(self, mock_build, gmail_client, mock_oauth_handler):
        """Test that _get_service creates Gmail service."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        service = gmail_client._get_service()

        assert service == mock_service
        mock_oauth_handler.get_credentials.assert_called_once()
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_oauth_handler.get_credentials())

    @patch('app.infrastructure.connectors.gmail.client.build')
    def test_get_service_reuses_existing(self, mock_build, gmail_client):
        """Test that _get_service reuses existing service."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        service1 = gmail_client._get_service()
        service2 = gmail_client._get_service()

        assert service1 == service2
        mock_build.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.GmailMessageMapper')
    async def test_send_email_success(self, mock_mapper, gmail_client, mock_service):
        """Test successful email sending."""
        gmail_client._service = mock_service

        # Mock mapper
        mock_mapper.from_email_draft.return_value = "base64_encoded_message"

        # Mock service response
        mock_send = MagicMock()
        mock_send.execute.return_value = {"id": "msg123"}
        mock_service.users().messages().send.return_value = mock_send

        draft = create_sample_draft()
        message_id = await gmail_client.send_email(draft)

        assert message_id == "msg123"
        mock_mapper.from_email_draft.assert_called_once_with(draft)
        mock_service.users().messages().send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self, gmail_client, mock_service):
        """Test email sending failure."""
        gmail_client._service = mock_service

        # Mock service to raise error
        mock_service.users().messages().send.side_effect = HttpError(
            resp=MagicMock(status=400),
            content=b"Bad request"
        )

        draft = create_sample_draft()

        with pytest.raises(Exception):
            await gmail_client.send_email(draft)

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.GmailMessageMapper')
    async def test_get_email_success(self, mock_mapper, gmail_client, mock_service):
        """Test successful email retrieval."""
        gmail_client._service = mock_service

        # Mock service response
        mock_get = MagicMock()
        mock_get.execute.return_value = SAMPLE_GMAIL_MESSAGE
        mock_service.users().messages().get.return_value = mock_get

        # Mock mapper
        mock_email = MagicMock()
        mock_mapper.to_email_entity.return_value = mock_email

        email = await gmail_client.get_email("msg123")

        assert email == mock_email
        mock_service.users().messages().get.assert_called_once_with(
            userId='me',
            id='msg123',
            format='full'
        )
        mock_mapper.to_email_entity.assert_called_once_with(SAMPLE_GMAIL_MESSAGE)

    @pytest.mark.asyncio
    async def test_get_email_failure(self, gmail_client, mock_service):
        """Test email retrieval failure."""
        gmail_client._service = mock_service

        # Mock service to raise error
        mock_service.users().messages().get.side_effect = HttpError(
            resp=MagicMock(status=404),
            content=b"Not found"
        )

        with pytest.raises(Exception):
            await gmail_client.get_email("nonexistent")

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.gmail.client.GmailMessageMapper')
    async def test_search_emails_success(self, mock_mapper, gmail_client, mock_service):
        """Test successful email search."""
        gmail_client._service = mock_service

        # Mock list response
        mock_list = MagicMock()
        mock_list.execute.return_value = SAMPLE_SEARCH_RESULTS
        mock_service.users().messages().list.return_value = mock_list

        # Mock get responses
        mock_get = MagicMock()
        mock_get.execute.return_value = SAMPLE_GMAIL_MESSAGE
        mock_service.users().messages().get.return_value = mock_get

        # Mock mapper
        mock_email = MagicMock()
        mock_mapper.to_email_entity.return_value = mock_email

        criteria = EmailSearchCriteria(
            from_address="sender@example.com",
            max_results=10
        )

        emails = await gmail_client.search_emails(criteria)

        assert len(emails) == 2
        assert all(e == mock_email for e in emails)
        mock_service.users().messages().list.assert_called_once()
        assert mock_service.users().messages().get.call_count == 2

    @pytest.mark.asyncio
    async def test_search_emails_empty_results(self, gmail_client, mock_service):
        """Test email search with no results."""
        gmail_client._service = mock_service

        # Mock empty response
        mock_list = MagicMock()
        mock_list.execute.return_value = EMPTY_SEARCH_RESULTS
        mock_service.users().messages().list.return_value = mock_list

        criteria = EmailSearchCriteria(query="nonexistent")
        emails = await gmail_client.search_emails(criteria)

        assert len(emails) == 0

    @pytest.mark.asyncio
    async def test_search_emails_uses_criteria(self, gmail_client, mock_service):
        """Test that search uses criteria correctly."""
        gmail_client._service = mock_service

        mock_list = MagicMock()
        mock_list.execute.return_value = EMPTY_SEARCH_RESULTS
        mock_service.users().messages().list.return_value = mock_list

        criteria = EmailSearchCriteria(
            from_address="sender@example.com",
            subject="test",
            is_unread=True,
            max_results=25
        )

        await gmail_client.search_emails(criteria)

        # Verify query was built correctly
        call_args = mock_service.users().messages().list.call_args
        assert call_args[1]['q'] == "from:sender@example.com subject:test is:unread"
        assert call_args[1]['maxResults'] == 25

    @pytest.mark.asyncio
    async def test_mark_as_read(self, gmail_client, mock_service):
        """Test marking email as read."""
        gmail_client._service = mock_service

        mock_modify = MagicMock()
        mock_modify.execute.return_value = {}
        mock_service.users().messages().modify.return_value = mock_modify

        await gmail_client.mark_as_read("msg123")

        mock_service.users().messages().modify.assert_called_once_with(
            userId='me',
            id='msg123',
            body={'removeLabelIds': ['UNREAD']}
        )

    @pytest.mark.asyncio
    async def test_mark_as_unread(self, gmail_client, mock_service):
        """Test marking email as unread."""
        gmail_client._service = mock_service

        mock_modify = MagicMock()
        mock_modify.execute.return_value = {}
        mock_service.users().messages().modify.return_value = mock_modify

        await gmail_client.mark_as_unread("msg123")

        mock_service.users().messages().modify.assert_called_once_with(
            userId='me',
            id='msg123',
            body={'addLabelIds': ['UNREAD']}
        )

    @pytest.mark.asyncio
    async def test_add_label(self, gmail_client, mock_service):
        """Test adding label to email."""
        gmail_client._service = mock_service

        mock_modify = MagicMock()
        mock_modify.execute.return_value = {}
        mock_service.users().messages().modify.return_value = mock_modify

        await gmail_client.add_label("msg123", "STARRED")

        mock_service.users().messages().modify.assert_called_once_with(
            userId='me',
            id='msg123',
            body={'addLabelIds': ['STARRED']}
        )

    @pytest.mark.asyncio
    async def test_get_attachment_success(self, gmail_client, mock_service):
        """Test getting attachment."""
        gmail_client._service = mock_service

        # Mock attachment response (base64 encoded "test data")
        mock_get = MagicMock()
        mock_get.execute.return_value = {
            "data": "dGVzdCBkYXRh"  # base64 for "test data"
        }
        mock_service.users().messages().attachments().get.return_value = mock_get

        data = await gmail_client.get_attachment("msg123", "att456")

        assert data == b"test data"
        mock_service.users().messages().attachments().get.assert_called_once_with(
            userId='me',
            messageId='msg123',
            id='att456'
        )

    @pytest.mark.asyncio
    async def test_get_attachment_failure(self, gmail_client, mock_service):
        """Test attachment retrieval failure."""
        gmail_client._service = mock_service

        mock_service.users().messages().attachments().get.side_effect = HttpError(
            resp=MagicMock(status=404),
            content=b"Not found"
        )

        with pytest.raises(Exception):
            await gmail_client.get_attachment("msg123", "att456")

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, gmail_client, mock_service):
        """Test that operations retry on failure."""
        gmail_client._service = mock_service

        # Mock service to fail twice then succeed
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise HttpError(resp=MagicMock(status=500), content=b"Server error")
            mock_result = MagicMock()
            mock_result.execute.return_value = {"id": "msg123"}
            return mock_result

        mock_service.users().messages().send.side_effect = side_effect

        draft = create_sample_draft()

        # Should succeed after retries
        message_id = await gmail_client.send_email(draft)

        assert message_id == "msg123"
        assert call_count == 3

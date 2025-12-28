"""
Unit tests for Gmail MCP tools.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock
from app.mcp.tools.gmail_tools import GmailTools, EmailSummary, SendEmailResult
from tests.fixtures.gmail_fixtures import create_sample_email


class TestGmailTools:
    """Test suite for Gmail MCP tools."""

    @pytest.fixture
    def gmail_tools(self):
        """Create GmailTools instance."""
        return GmailTools()

    @pytest.fixture
    def mock_send_email_uc(self):
        """Mock SendEmail use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_search_emails_uc(self):
        """Mock SearchEmails use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_get_email_uc(self):
        """Mock GetEmail use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_mark_read_uc(self):
        """Mock MarkAsRead use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_mark_unread_uc(self):
        """Mock MarkAsUnread use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_add_label_uc(self):
        """Mock AddLabel use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.mark.asyncio
    async def test_send_email_success(self, gmail_tools, mock_send_email_uc):
        """Test successful email sending through MCP tool."""
        gmail_tools.send_email_uc = mock_send_email_uc

        # Mock response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message_id = "msg123"
        mock_response.error = None
        mock_send_email_uc.execute.return_value = mock_response

        result = await gmail_tools.send_email(
            to=["recipient@example.com"],
            subject="Test Subject",
            body_text="Test body"
        )

        assert isinstance(result, SendEmailResult)
        assert result.success is True
        assert result.message_id == "msg123"
        assert result.error is None

        # Verify request
        request = mock_send_email_uc.execute.call_args[0][0]
        assert request.to == ["recipient@example.com"]
        assert request.subject == "Test Subject"
        assert request.body_text == "Test body"

    @pytest.mark.asyncio
    async def test_send_email_with_all_params(self, gmail_tools, mock_send_email_uc):
        """Test sending email with all parameters."""
        gmail_tools.send_email_uc = mock_send_email_uc

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message_id = "msg123"
        mock_response.error = None
        mock_send_email_uc.execute.return_value = mock_response

        result = await gmail_tools.send_email(
            to=["to1@example.com", "to2@example.com"],
            subject="Test",
            body_text="Plain text",
            body_html="<p>HTML text</p>",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            account_id="custom@example.com"
        )

        request = mock_send_email_uc.execute.call_args[0][0]
        assert len(request.to) == 2
        assert request.cc == ["cc@example.com"]
        assert request.bcc == ["bcc@example.com"]
        assert request.account_id == "custom@example.com"

    @pytest.mark.asyncio
    async def test_send_email_failure(self, gmail_tools, mock_send_email_uc):
        """Test email sending failure."""
        gmail_tools.send_email_uc = mock_send_email_uc

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.message_id = None
        mock_response.error = "Network error"
        mock_send_email_uc.execute.return_value = mock_response

        result = await gmail_tools.send_email(
            to=["recipient@example.com"],
            subject="Test",
            body_text="Body"
        )

        assert result.success is False
        assert result.error == "Network error"

    @pytest.mark.asyncio
    async def test_search_emails_success(self, gmail_tools, mock_search_emails_uc):
        """Test successful email search."""
        gmail_tools.search_emails_uc = mock_search_emails_uc

        # Mock response
        mock_emails = [create_sample_email(), create_sample_email()]
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.emails = mock_emails
        mock_response.count = 2
        mock_response.error = None
        mock_search_emails_uc.execute.return_value = mock_response

        result = await gmail_tools.search_emails(
            from_address="sender@example.com",
            max_results=10
        )

        assert result.success is True
        assert result.count == 2
        assert len(result.emails) == 2

        # Verify emails are converted to summaries
        for email in result.emails:
            assert isinstance(email, EmailSummary)
            assert email.id is not None
            assert email.subject is not None

    @pytest.mark.asyncio
    async def test_search_emails_all_params(self, gmail_tools, mock_search_emails_uc):
        """Test search with all parameters."""
        gmail_tools.search_emails_uc = mock_search_emails_uc

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.emails = []
        mock_response.count = 0
        mock_response.error = None
        mock_search_emails_uc.execute.return_value = mock_response

        await gmail_tools.search_emails(
            query="important",
            from_address="sender@example.com",
            to_address="recipient@example.com",
            subject="test",
            has_attachment=True,
            is_unread=True,
            label="INBOX",
            max_results=50,
            account_id="custom@example.com"
        )

        request = mock_search_emails_uc.execute.call_args[0][0]
        assert request.query == "important"
        assert request.from_address == "sender@example.com"
        assert request.to_address == "recipient@example.com"
        assert request.subject == "test"
        assert request.has_attachment is True
        assert request.is_unread is True
        assert request.label == "INBOX"
        assert request.max_results == 50
        assert request.account_id == "custom@example.com"

    @pytest.mark.asyncio
    async def test_search_emails_max_results_limit(self, gmail_tools, mock_search_emails_uc):
        """Test that max_results is limited to 100."""
        gmail_tools.search_emails_uc = mock_search_emails_uc

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.emails = []
        mock_response.count = 0
        mock_response.error = None
        mock_search_emails_uc.execute.return_value = mock_response

        await gmail_tools.search_emails(max_results=500)

        request = mock_search_emails_uc.execute.call_args[0][0]
        assert request.max_results == 100  # Should be limited

    @pytest.mark.asyncio
    async def test_get_email_success(self, gmail_tools, mock_get_email_uc):
        """Test successful email retrieval."""
        gmail_tools.get_email_uc = mock_get_email_uc

        mock_email = create_sample_email()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.email = mock_email
        mock_response.error = None
        mock_get_email_uc.execute.return_value = mock_response

        result = await gmail_tools.get_email(message_id="msg123")

        assert result.success is True
        assert result.email is not None
        assert result.email.id == mock_email.id
        assert result.email.subject == mock_email.subject

    @pytest.mark.asyncio
    async def test_get_email_failure(self, gmail_tools, mock_get_email_uc):
        """Test email retrieval failure."""
        gmail_tools.get_email_uc = mock_get_email_uc

        mock_response = MagicMock()
        mock_response.success = False
        mock_response.email = None
        mock_response.error = "Not found"
        mock_get_email_uc.execute.return_value = mock_response

        result = await gmail_tools.get_email(message_id="nonexistent")

        assert result.success is False
        assert result.email is None
        assert result.error == "Not found"

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, gmail_tools, mock_mark_read_uc):
        """Test marking email as read."""
        gmail_tools.mark_read_uc = mock_mark_read_uc

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = None
        mock_mark_read_uc.execute.return_value = mock_response

        result = await gmail_tools.mark_as_read(message_id="msg123")

        assert result["success"] is True
        assert result["error"] is None

        request = mock_mark_read_uc.execute.call_args[0][0]
        assert request.message_id == "msg123"

    @pytest.mark.asyncio
    async def test_mark_as_unread_success(self, gmail_tools, mock_mark_unread_uc):
        """Test marking email as unread."""
        gmail_tools.mark_unread_uc = mock_mark_unread_uc

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = None
        mock_mark_unread_uc.execute.return_value = mock_response

        result = await gmail_tools.mark_as_unread(message_id="msg123")

        assert result["success"] is True

        request = mock_mark_unread_uc.execute.call_args[0][0]
        assert request.message_id == "msg123"

    @pytest.mark.asyncio
    async def test_add_label_success(self, gmail_tools, mock_add_label_uc):
        """Test adding label to email."""
        gmail_tools.add_label_uc = mock_add_label_uc

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.error = None
        mock_add_label_uc.execute.return_value = mock_response

        result = await gmail_tools.add_label(
            message_id="msg123",
            label="STARRED"
        )

        assert result["success"] is True

        request = mock_add_label_uc.execute.call_args[0][0]
        assert request.message_id == "msg123"
        assert request.label == "STARRED"

    @pytest.mark.asyncio
    async def test_email_summary_conversion(self, gmail_tools, mock_search_emails_uc):
        """Test conversion of Email to EmailSummary."""
        gmail_tools.search_emails_uc = mock_search_emails_uc

        email = create_sample_email()
        email.date = datetime(2025, 1, 20, 10, 30, 0)

        mock_response = MagicMock()
        mock_response.success = True
        mock_response.emails = [email]
        mock_response.count = 1
        mock_response.error = None
        mock_search_emails_uc.execute.return_value = mock_response

        result = await gmail_tools.search_emails()

        summary = result.emails[0]
        assert summary.id == email.id
        assert summary.subject == email.subject
        assert summary.from_email == email.from_address.email
        assert summary.from_name == email.from_address.name
        assert summary.date is not None
        assert summary.is_read == email.is_read

    @pytest.mark.asyncio
    async def test_init_creates_use_cases(self):
        """Test that GmailTools initializes all use cases."""
        tools = GmailTools()

        assert tools.send_email_uc is not None
        assert tools.search_emails_uc is not None
        assert tools.get_email_uc is not None
        assert tools.mark_read_uc is not None
        assert tools.mark_unread_uc is not None
        assert tools.add_label_uc is not None

    def test_gmail_tools_global_instance(self):
        """Test that global instance is available."""
        from app.mcp.tools.gmail_tools import gmail_tools

        assert isinstance(gmail_tools, GmailTools)

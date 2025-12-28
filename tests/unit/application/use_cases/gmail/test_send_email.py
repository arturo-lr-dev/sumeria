"""
Unit tests for SendEmail use case.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.application.use_cases.gmail.send_email import (
    SendEmailUseCase,
    SendEmailRequest,
    SendEmailResponse
)


class TestSendEmailUseCase:
    """Test suite for SendEmail use case."""

    @pytest.fixture
    def use_case(self):
        """Create use case instance."""
        return SendEmailUseCase()

    @pytest.fixture
    def mock_client(self):
        """Create mock Gmail client."""
        client = MagicMock()
        client.send_email = AsyncMock(return_value="msg123")
        return client

    @pytest.fixture
    def mock_account_manager(self, mock_client):
        """Mock account manager."""
        with patch('app.application.use_cases.gmail.send_email.gmail_account_manager') as manager:
            manager.get_client.return_value = mock_client
            yield manager

    @pytest.mark.asyncio
    async def test_send_email_success(self, use_case, mock_account_manager, mock_client):
        """Test successful email sending."""
        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test Subject",
            body_text="Test body"
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.message_id == "msg123"
        assert response.error is None

        # Verify client was called
        mock_client.send_email.assert_called_once()
        draft = mock_client.send_email.call_args[0][0]
        assert draft.subject == "Test Subject"
        assert draft.body_text == "Test body"

    @pytest.mark.asyncio
    async def test_send_email_with_html(self, use_case, mock_account_manager, mock_client):
        """Test sending email with HTML body."""
        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test",
            body_text="Plain text",
            body_html="<p>HTML text</p>"
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.send_email.call_args[0][0]
        assert draft.body_text == "Plain text"
        assert draft.body_html == "<p>HTML text</p>"

    @pytest.mark.asyncio
    async def test_send_email_with_cc_bcc(self, use_case, mock_account_manager, mock_client):
        """Test sending email with CC and BCC."""
        request = SendEmailRequest(
            to=["to@example.com"],
            subject="Test",
            body_text="Body",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"]
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.send_email.call_args[0][0]
        assert len(draft.to) == 1
        assert len(draft.cc) == 1
        assert len(draft.bcc) == 1
        assert draft.cc[0].email == "cc@example.com"
        assert draft.bcc[0].email == "bcc@example.com"

    @pytest.mark.asyncio
    async def test_send_email_multiple_recipients(self, use_case, mock_account_manager, mock_client):
        """Test sending email to multiple recipients."""
        request = SendEmailRequest(
            to=["user1@example.com", "user2@example.com", "user3@example.com"],
            subject="Test",
            body_text="Body"
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.send_email.call_args[0][0]
        assert len(draft.to) == 3

    @pytest.mark.asyncio
    async def test_send_email_with_account_id(self, use_case, mock_account_manager, mock_client):
        """Test sending email with specific account."""
        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test",
            body_text="Body",
            account_id="specific@example.com"
        )

        await use_case.execute(request)

        mock_account_manager.get_client.assert_called_once_with("specific@example.com")

    @pytest.mark.asyncio
    async def test_send_email_failure(self, use_case, mock_account_manager, mock_client):
        """Test email sending failure."""
        mock_client.send_email.side_effect = Exception("Network error")

        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test",
            body_text="Body"
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert response.message_id is None
        assert "Network error" in response.error

    @pytest.mark.asyncio
    async def test_send_email_empty_cc_bcc(self, use_case, mock_account_manager, mock_client):
        """Test sending email with None CC and BCC."""
        request = SendEmailRequest(
            to=["recipient@example.com"],
            subject="Test",
            body_text="Body",
            cc=None,
            bcc=None
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.send_email.call_args[0][0]
        assert len(draft.cc) == 0
        assert len(draft.bcc) == 0

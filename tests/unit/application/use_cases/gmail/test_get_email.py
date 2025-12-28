"""
Unit tests for GetEmail use case.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.application.use_cases.gmail.get_email import (
    GetEmailUseCase,
    GetEmailRequest,
    GetEmailResponse
)
from tests.fixtures.gmail_fixtures import create_sample_email


class TestGetEmailUseCase:
    """Test suite for GetEmail use case."""

    @pytest.fixture
    def use_case(self):
        """Create use case instance."""
        return GetEmailUseCase()

    @pytest.fixture
    def mock_email(self):
        """Create mock email."""
        return create_sample_email()

    @pytest.fixture
    def mock_client(self, mock_email):
        """Create mock Gmail client."""
        client = MagicMock()
        client.get_email = AsyncMock(return_value=mock_email)
        return client

    @pytest.fixture
    def mock_account_manager(self, mock_client):
        """Mock account manager."""
        with patch('app.application.use_cases.gmail.get_email.gmail_account_manager') as manager:
            manager.get_client.return_value = mock_client
            yield manager

    @pytest.mark.asyncio
    async def test_get_email_success(self, use_case, mock_account_manager, mock_client, mock_email):
        """Test successful email retrieval."""
        request = GetEmailRequest(message_id="msg123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.email == mock_email
        assert response.error is None

        mock_client.get_email.assert_called_once_with("msg123")

    @pytest.mark.asyncio
    async def test_get_email_with_account_id(self, use_case, mock_account_manager, mock_client):
        """Test get email with specific account."""
        request = GetEmailRequest(
            message_id="msg123",
            account_id="specific@example.com"
        )

        await use_case.execute(request)

        mock_account_manager.get_client.assert_called_once_with("specific@example.com")

    @pytest.mark.asyncio
    async def test_get_email_failure(self, use_case, mock_account_manager, mock_client):
        """Test email retrieval failure."""
        mock_client.get_email.side_effect = Exception("Email not found")

        request = GetEmailRequest(message_id="nonexistent")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.email is None
        assert "Email not found" in response.error

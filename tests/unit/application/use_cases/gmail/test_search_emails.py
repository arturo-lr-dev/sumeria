"""
Unit tests for SearchEmails use case.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock
from app.application.use_cases.gmail.search_emails import (
    SearchEmailsUseCase,
    SearchEmailsRequest,
    SearchEmailsResponse
)
from tests.fixtures.gmail_fixtures import create_sample_email


class TestSearchEmailsUseCase:
    """Test suite for SearchEmails use case."""

    @pytest.fixture
    def use_case(self):
        """Create use case instance."""
        return SearchEmailsUseCase()

    @pytest.fixture
    def mock_emails(self):
        """Create mock emails."""
        return [create_sample_email(), create_sample_email()]

    @pytest.fixture
    def mock_client(self, mock_emails):
        """Create mock Gmail client."""
        client = MagicMock()
        client.search_emails = AsyncMock(return_value=mock_emails)
        return client

    @pytest.fixture
    def mock_account_manager(self, mock_client):
        """Mock account manager."""
        with patch('app.application.use_cases.gmail.search_emails.gmail_account_manager') as manager:
            manager.get_client.return_value = mock_client
            yield manager

    @pytest.mark.asyncio
    async def test_search_emails_success(self, use_case, mock_account_manager, mock_client, mock_emails):
        """Test successful email search."""
        request = SearchEmailsRequest(
            from_address="sender@example.com",
            max_results=10
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.emails) == 2
        assert response.error is None

        # Verify client was called
        mock_client.search_emails.assert_called_once()
        criteria = mock_client.search_emails.call_args[0][0]
        assert criteria.from_address == "sender@example.com"
        assert criteria.max_results == 10

    @pytest.mark.asyncio
    async def test_search_emails_all_criteria(self, use_case, mock_account_manager, mock_client):
        """Test search with all criteria."""
        after_date = datetime(2025, 1, 1)
        before_date = datetime(2025, 1, 31)

        request = SearchEmailsRequest(
            query="important",
            from_address="sender@example.com",
            to_address="recipient@example.com",
            subject="test",
            has_attachment=True,
            is_unread=True,
            label="INBOX",
            after_date=after_date,
            before_date=before_date,
            max_results=25
        )

        await use_case.execute(request)

        criteria = mock_client.search_emails.call_args[0][0]
        assert criteria.query == "important"
        assert criteria.from_address == "sender@example.com"
        assert criteria.to_address == "recipient@example.com"
        assert criteria.subject == "test"
        assert criteria.has_attachment is True
        assert criteria.is_unread is True
        assert criteria.label == "INBOX"
        assert criteria.after_date == after_date
        assert criteria.before_date == before_date
        assert criteria.max_results == 25

    @pytest.mark.asyncio
    async def test_search_emails_empty_results(self, use_case, mock_account_manager, mock_client):
        """Test search with no results."""
        mock_client.search_emails = AsyncMock(return_value=[])

        request = SearchEmailsRequest(query="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.emails) == 0

    @pytest.mark.asyncio
    async def test_search_emails_with_account_id(self, use_case, mock_account_manager, mock_client):
        """Test search with specific account."""
        request = SearchEmailsRequest(
            query="test",
            account_id="specific@example.com"
        )

        await use_case.execute(request)

        mock_account_manager.get_client.assert_called_once_with("specific@example.com")

    @pytest.mark.asyncio
    async def test_search_emails_failure(self, use_case, mock_account_manager, mock_client):
        """Test search failure."""
        mock_client.search_emails.side_effect = Exception("API error")

        request = SearchEmailsRequest(query="test")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert len(response.emails) == 0
        assert "API error" in response.error

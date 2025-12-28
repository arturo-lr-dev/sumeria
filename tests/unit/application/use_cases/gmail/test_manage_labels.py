"""
Unit tests for manage labels use cases.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.application.use_cases.gmail.manage_labels import (
    MarkAsReadUseCase,
    MarkAsUnreadUseCase,
    AddLabelUseCase,
    MarkAsReadRequest,
    MarkAsUnreadRequest,
    AddLabelRequest,
    ManageLabelResponse
)


class TestMarkAsReadUseCase:
    """Test suite for MarkAsRead use case."""

    @pytest.fixture
    def use_case(self):
        """Create use case instance."""
        return MarkAsReadUseCase()

    @pytest.fixture
    def mock_client(self):
        """Create mock Gmail client."""
        client = MagicMock()
        client.mark_as_read = AsyncMock()
        return client

    @pytest.fixture
    def mock_account_manager(self, mock_client):
        """Mock account manager."""
        with patch('app.application.use_cases.gmail.manage_labels.gmail_account_manager') as manager:
            manager.get_client.return_value = mock_client
            yield manager

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, use_case, mock_account_manager, mock_client):
        """Test successful mark as read."""
        request = MarkAsReadRequest(message_id="msg123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.error is None

        mock_client.mark_as_read.assert_called_once_with("msg123")

    @pytest.mark.asyncio
    async def test_mark_as_read_with_account_id(self, use_case, mock_account_manager, mock_client):
        """Test mark as read with specific account."""
        request = MarkAsReadRequest(
            message_id="msg123",
            account_id="specific@example.com"
        )

        await use_case.execute(request)

        mock_account_manager.get_client.assert_called_once_with("specific@example.com")

    @pytest.mark.asyncio
    async def test_mark_as_read_failure(self, use_case, mock_account_manager, mock_client):
        """Test mark as read failure."""
        mock_client.mark_as_read.side_effect = Exception("API error")

        request = MarkAsReadRequest(message_id="msg123")

        response = await use_case.execute(request)

        assert response.success is False
        assert "API error" in response.error


class TestMarkAsUnreadUseCase:
    """Test suite for MarkAsUnread use case."""

    @pytest.fixture
    def use_case(self):
        """Create use case instance."""
        return MarkAsUnreadUseCase()

    @pytest.fixture
    def mock_client(self):
        """Create mock Gmail client."""
        client = MagicMock()
        client.mark_as_unread = AsyncMock()
        return client

    @pytest.fixture
    def mock_account_manager(self, mock_client):
        """Mock account manager."""
        with patch('app.application.use_cases.gmail.manage_labels.gmail_account_manager') as manager:
            manager.get_client.return_value = mock_client
            yield manager

    @pytest.mark.asyncio
    async def test_mark_as_unread_success(self, use_case, mock_account_manager, mock_client):
        """Test successful mark as unread."""
        request = MarkAsUnreadRequest(message_id="msg123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.error is None

        mock_client.mark_as_unread.assert_called_once_with("msg123")

    @pytest.mark.asyncio
    async def test_mark_as_unread_failure(self, use_case, mock_account_manager, mock_client):
        """Test mark as unread failure."""
        mock_client.mark_as_unread.side_effect = Exception("API error")

        request = MarkAsUnreadRequest(message_id="msg123")

        response = await use_case.execute(request)

        assert response.success is False
        assert "API error" in response.error


class TestAddLabelUseCase:
    """Test suite for AddLabel use case."""

    @pytest.fixture
    def use_case(self):
        """Create use case instance."""
        return AddLabelUseCase()

    @pytest.fixture
    def mock_client(self):
        """Create mock Gmail client."""
        client = MagicMock()
        client.add_label = AsyncMock()
        return client

    @pytest.fixture
    def mock_account_manager(self, mock_client):
        """Mock account manager."""
        with patch('app.application.use_cases.gmail.manage_labels.gmail_account_manager') as manager:
            manager.get_client.return_value = mock_client
            yield manager

    @pytest.mark.asyncio
    async def test_add_label_success(self, use_case, mock_account_manager, mock_client):
        """Test successful label addition."""
        request = AddLabelRequest(
            message_id="msg123",
            label="STARRED"
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.error is None

        mock_client.add_label.assert_called_once_with("msg123", "STARRED")

    @pytest.mark.asyncio
    async def test_add_label_with_account_id(self, use_case, mock_account_manager, mock_client):
        """Test add label with specific account."""
        request = AddLabelRequest(
            message_id="msg123",
            label="IMPORTANT",
            account_id="specific@example.com"
        )

        await use_case.execute(request)

        mock_account_manager.get_client.assert_called_once_with("specific@example.com")

    @pytest.mark.asyncio
    async def test_add_label_failure(self, use_case, mock_account_manager, mock_client):
        """Test add label failure."""
        mock_client.add_label.side_effect = Exception("API error")

        request = AddLabelRequest(
            message_id="msg123",
            label="STARRED"
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert "API error" in response.error

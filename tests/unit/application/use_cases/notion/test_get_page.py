"""
Unit tests for GetPage use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.get_page import (
    GetPageUseCase,
    GetPageRequest,
    GetPageResponse
)
from app.domain.entities.notion_page import NotionPage


class TestGetPageUseCase:
    """Test suite for GetPage use case."""

    @pytest.fixture
    def mock_page(self):
        """Create mock Notion page."""
        return NotionPage(
            id="page123",
            title="My Page",
            created_time="2025-01-01T00:00:00Z",
            last_edited_time="2025-01-15T12:00:00Z"
        )

    @pytest.fixture
    def mock_client(self, mock_page):
        """Create mock Notion client."""
        client = MagicMock()
        client.get_page = AsyncMock(return_value=mock_page)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return GetPageUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_page_success(self, use_case, mock_client, mock_page):
        """Test successful page retrieval."""
        request = GetPageRequest(page_id="page123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.page == mock_page
        assert response.error is None
        mock_client.get_page.assert_called_once_with("page123")

    @pytest.mark.asyncio
    async def test_get_page_not_found(self, use_case, mock_client):
        """Test page not found."""
        mock_client.get_page.return_value = None

        request = GetPageRequest(page_id="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.page is None

    @pytest.mark.asyncio
    async def test_get_page_failure(self, use_case, mock_client):
        """Test page retrieval failure."""
        mock_client.get_page.side_effect = Exception("API error")

        request = GetPageRequest(page_id="page123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.page is None
        assert "API error" in response.error

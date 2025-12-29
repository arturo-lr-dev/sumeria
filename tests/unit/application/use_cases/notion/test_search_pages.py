"""
Unit tests for SearchPages use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.search_pages import (
    SearchPagesUseCase,
    SearchPagesRequest,
    SearchPagesResponse
)
from app.domain.entities.notion_page import NotionPage


class TestSearchPagesUseCase:
    """Test suite for SearchPages use case."""

    @pytest.fixture
    def mock_pages(self):
        """Create mock pages."""
        return [
            NotionPage(
                id="page1",
                title="First Page",
                created_time="2025-01-01T00:00:00Z"
            ),
            NotionPage(
                id="page2",
                title="Second Page",
                created_time="2025-01-02T00:00:00Z"
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_pages):
        """Create mock Notion client."""
        client = MagicMock()
        client.search = AsyncMock(return_value=mock_pages)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return SearchPagesUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_search_pages_success(self, use_case, mock_client, mock_pages):
        """Test successful page search."""
        request = SearchPagesRequest(query="test")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.pages) == 2
        assert response.error is None
        mock_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_pages_with_filter(self, use_case, mock_client):
        """Test searching pages with filter."""
        request = SearchPagesRequest(
            query="project",
            filter_type="page"
        )

        await use_case.execute(request)

        criteria = mock_client.search.call_args[0][0]
        assert criteria.query == "project"
        assert criteria.filter_type is not None

    @pytest.mark.asyncio
    async def test_search_pages_with_sort(self, use_case, mock_client):
        """Test searching pages with sorting."""
        request = SearchPagesRequest(
            query="",
            sort_direction="ascending",
            sort_timestamp="created_time"
        )

        await use_case.execute(request)

        criteria = mock_client.search.call_args[0][0]
        assert criteria.sort_direction == "ascending"
        assert criteria.sort_timestamp == "created_time"

    @pytest.mark.asyncio
    async def test_search_pages_with_max_results(self, use_case, mock_client):
        """Test searching with max results."""
        request = SearchPagesRequest(
            query="",
            max_results=50
        )

        await use_case.execute(request)

        criteria = mock_client.search.call_args[0][0]
        assert criteria.max_results == 50

    @pytest.mark.asyncio
    async def test_search_pages_empty_results(self, use_case, mock_client):
        """Test search with no results."""
        mock_client.search = AsyncMock(return_value=[])

        request = SearchPagesRequest(query="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.pages) == 0

    @pytest.mark.asyncio
    async def test_search_pages_failure(self, use_case, mock_client):
        """Test page search failure."""
        mock_client.search.side_effect = Exception("API error")

        request = SearchPagesRequest(query="test")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "API error" in response.error

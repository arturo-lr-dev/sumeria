"""
Unit tests for GetPageContent use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.get_page_content import (
    GetPageContentUseCase,
    GetPageContentRequest,
    GetPageContentResponse
)
from app.domain.entities.notion_block import NotionBlock


class TestGetPageContentUseCase:
    """Test suite for GetPageContent use case."""

    @pytest.fixture
    def mock_blocks(self):
        """Create mock content blocks."""
        return [
            NotionBlock(
                id="block1",
                type="paragraph",
                content={"text": [{"text": {"content": "First paragraph"}}]}
            ),
            NotionBlock(
                id="block2",
                type="heading_1",
                content={"text": [{"text": {"content": "Main Title"}}]}
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_blocks):
        """Create mock Notion client."""
        client = MagicMock()
        client.get_block_children = AsyncMock(return_value=mock_blocks)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return GetPageContentUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_page_content_success(self, use_case, mock_client, mock_blocks):
        """Test successful page content retrieval."""
        request = GetPageContentRequest(page_id="page123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.blocks) == 2
        assert response.error is None
        mock_client.get_block_children.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_page_content_empty(self, use_case, mock_client):
        """Test page with no content."""
        mock_client.get_block_children = AsyncMock(return_value=[])

        request = GetPageContentRequest(page_id="page123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.blocks) == 0

    @pytest.mark.asyncio
    async def test_get_page_content_failure(self, use_case, mock_client):
        """Test page content retrieval failure."""
        mock_client.get_block_children.side_effect = Exception("API error")

        request = GetPageContentRequest(page_id="page123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "API error" in response.error

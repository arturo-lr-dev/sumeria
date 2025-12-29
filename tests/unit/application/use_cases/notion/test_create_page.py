"""
Unit tests for CreatePage use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.create_page import (
    CreatePageUseCase,
    CreatePageRequest,
    CreatePageResponse
)


class TestCreatePageUseCase:
    """Test suite for CreatePage use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Notion client."""
        client = MagicMock()
        client.create_page = AsyncMock(return_value="page123")
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return CreatePageUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_create_page_basic(self, use_case, mock_client):
        """Test creating a basic page."""
        request = CreatePageRequest(
            title="My Page",
            parent_id="parent123"
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.page_id == "page123"
        assert response.error is None
        mock_client.create_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_with_properties(self, use_case, mock_client):
        """Test creating page with custom properties."""
        request = CreatePageRequest(
            title="Project Page",
            parent_id="database123",
            parent_type="database_id",
            properties={
                "Status": {"select": {"name": "In Progress"}},
                "Priority": {"select": {"name": "High"}}
            }
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_page.call_args[0][0]
        assert draft.title == "Project Page"
        assert draft.parent_type == "database_id"
        assert draft.properties is not None

    @pytest.mark.asyncio
    async def test_create_page_with_children(self, use_case, mock_client):
        """Test creating page with child blocks."""
        request = CreatePageRequest(
            title="Document",
            parent_id="parent123",
            children=[
                {"type": "paragraph", "paragraph": {"text": [{"text": {"content": "Hello"}}]}},
                {"type": "heading_1", "heading_1": {"text": [{"text": {"content": "Title"}}]}}
            ]
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_page.call_args[0][0]
        assert len(draft.children) == 2

    @pytest.mark.asyncio
    async def test_create_page_with_icon_and_cover(self, use_case, mock_client):
        """Test creating page with icon and cover."""
        request = CreatePageRequest(
            title="Styled Page",
            parent_id="parent123",
            icon={"type": "emoji", "emoji": "📄"},
            cover={"type": "external", "external": {"url": "https://example.com/cover.jpg"}}
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_page.call_args[0][0]
        assert draft.icon is not None
        assert draft.cover is not None

    @pytest.mark.asyncio
    async def test_create_page_failure(self, use_case, mock_client):
        """Test page creation failure."""
        mock_client.create_page.side_effect = Exception("API error")

        request = CreatePageRequest(
            title="Failed Page",
            parent_id="parent123"
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert response.page_id is None
        assert "API error" in response.error

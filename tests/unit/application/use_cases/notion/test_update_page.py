"""
Unit tests for UpdatePage use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.update_page import (
    UpdatePageUseCase,
    UpdatePageRequest,
    UpdatePageResponse
)


class TestUpdatePageUseCase:
    """Test suite for UpdatePage use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Notion client."""
        client = MagicMock()
        client.update_page = AsyncMock(return_value=True)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return UpdatePageUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_update_page_properties(self, use_case, mock_client):
        """Test updating page properties."""
        request = UpdatePageRequest(
            page_id="page123",
            properties={
                "Status": {"select": {"name": "Done"}},
                "Priority": {"select": {"name": "Low"}}
            }
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.error is None
        mock_client.update_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_page_icon(self, use_case, mock_client):
        """Test updating page icon."""
        request = UpdatePageRequest(
            page_id="page123",
            icon={"type": "emoji", "emoji": "✅"}
        )

        response = await use_case.execute(request)

        assert response.success is True

        call_kwargs = mock_client.update_page.call_args[1]
        assert call_kwargs["icon"] is not None

    @pytest.mark.asyncio
    async def test_update_page_cover(self, use_case, mock_client):
        """Test updating page cover."""
        request = UpdatePageRequest(
            page_id="page123",
            cover={"type": "external", "external": {"url": "https://example.com/new-cover.jpg"}}
        )

        response = await use_case.execute(request)

        assert response.success is True

        call_kwargs = mock_client.update_page.call_args[1]
        assert call_kwargs["cover"] is not None

    @pytest.mark.asyncio
    async def test_update_page_archived(self, use_case, mock_client):
        """Test archiving a page."""
        request = UpdatePageRequest(
            page_id="page123",
            archived=True
        )

        response = await use_case.execute(request)

        assert response.success is True

        call_kwargs = mock_client.update_page.call_args[1]
        assert call_kwargs["archived"] is True

    @pytest.mark.asyncio
    async def test_update_page_multiple_fields(self, use_case, mock_client):
        """Test updating multiple page fields."""
        request = UpdatePageRequest(
            page_id="page123",
            properties={"Status": {"select": {"name": "In Progress"}}},
            icon={"type": "emoji", "emoji": "🔄"},
            cover={"type": "external", "external": {"url": "https://example.com/cover.jpg"}}
        )

        response = await use_case.execute(request)

        assert response.success is True

        call_kwargs = mock_client.update_page.call_args[1]
        assert call_kwargs["properties"] is not None
        assert call_kwargs["icon"] is not None
        assert call_kwargs["cover"] is not None

    @pytest.mark.asyncio
    async def test_update_page_failure(self, use_case, mock_client):
        """Test page update failure."""
        mock_client.update_page.side_effect = Exception("API error")

        request = UpdatePageRequest(
            page_id="page123",
            properties={"Status": {"select": {"name": "Done"}}}
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert "API error" in response.error

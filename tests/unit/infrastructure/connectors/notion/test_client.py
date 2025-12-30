"""
Unit tests for Notion client.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from tenacity import RetryError

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_page import NotionPageDraft, NotionPageSearchCriteria
from app.domain.entities.notion_database import (
    NotionDatabaseEntryDraft,
    NotionDatabaseQuery
)
from app.domain.entities.notion_block import NotionBlockDraft


@pytest.fixture
def mock_notion_api():
    """Mock Notion AsyncClient."""
    with patch("app.infrastructure.connectors.notion.client.AsyncClient") as mock:
        yield mock


@pytest.fixture
def notion_client(mock_notion_api):
    """Create NotionClient with mocked API."""
    with patch("app.config.settings.settings.notion_api_key", "test_key"):
        client = NotionClient(api_key="test_key")
        return client


class TestNotionClient:
    """Test NotionClient class."""

    @pytest.mark.asyncio
    async def test_create_page(self, notion_client):
        """Test creating a page."""
        # Mock response
        notion_client.client.pages.create = AsyncMock(
            return_value={"id": "page_123"}
        )

        # Create draft
        draft = NotionPageDraft(
            title="Test Page",
            parent_id="parent_123",
            parent_type="page_id"
        )

        # Execute
        page_id = await notion_client.create_page(draft)

        # Assert
        assert page_id == "page_123"
        notion_client.client.pages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_page(self, notion_client):
        """Test getting a page."""
        # Mock response
        mock_response = {
            "id": "page_123",
            "properties": {
                "title": {
                    "type": "title",
                    "title": [{"plain_text": "Test Page"}]
                }
            },
            "parent": {"type": "page_id", "page_id": "parent_123"},
            "url": "https://notion.so/page_123",
            "archived": False,
            "created_time": "2025-01-01T00:00:00.000Z",
            "last_edited_time": "2025-01-01T00:00:00.000Z"
        }

        notion_client.client.pages.retrieve = AsyncMock(return_value=mock_response)

        # Execute
        page = await notion_client.get_page("page_123")

        # Assert
        assert page.id == "page_123"
        assert page.title == "Test Page"
        assert page.parent_id == "parent_123"
        notion_client.client.pages.retrieve.assert_called_once_with(page_id="page_123")

    @pytest.mark.asyncio
    async def test_update_page(self, notion_client):
        """Test updating a page."""
        # Mock response
        mock_response = {
            "id": "page_123",
            "properties": {
                "title": {
                    "type": "title",
                    "title": [{"plain_text": "Updated Page"}]
                }
            },
            "parent": {"type": "page_id", "page_id": "parent_123"},
            "archived": False,
            "created_time": "2025-01-01T00:00:00.000Z",
            "last_edited_time": "2025-01-01T00:00:00.000Z"
        }

        notion_client.client.pages.update = AsyncMock(return_value=mock_response)

        # Execute
        properties = {
            "title": {
                "title": [{"text": {"content": "Updated Page"}}]
            }
        }
        page = await notion_client.update_page("page_123", properties=properties)

        # Assert
        assert page.title == "Updated Page"
        notion_client.client.pages.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_search(self, notion_client):
        """Test searching pages."""
        # Mock response
        mock_response = {
            "results": [
                {
                    "object": "page",
                    "id": "page_123",
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [{"plain_text": "Test Page"}]
                        }
                    },
                    "parent": {"type": "page_id", "page_id": "parent_123"},
                    "archived": False,
                    "created_time": "2025-01-01T00:00:00.000Z",
                    "last_edited_time": "2025-01-01T00:00:00.000Z"
                }
            ]
        }

        notion_client.client.search = AsyncMock(return_value=mock_response)

        # Create criteria
        criteria = NotionPageSearchCriteria(
            query="test",
            filter_type="page"
        )

        # Execute
        pages = await notion_client.search(criteria)

        # Assert
        assert len(pages) == 1
        assert pages[0].id == "page_123"
        assert pages[0].title == "Test Page"
        notion_client.client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_database(self, notion_client):
        """Test querying a database."""
        # Mock response
        mock_response = {
            "results": [
                {
                    "id": "entry_123",
                    "parent": {"type": "database_id", "database_id": "db_123"},
                    "properties": {
                        "Name": {
                            "type": "title",
                            "title": [{"plain_text": "Entry 1"}]
                        }
                    },
                    "created_time": "2025-01-01T00:00:00.000Z",
                    "last_edited_time": "2025-01-01T00:00:00.000Z"
                }
            ]
        }

        notion_client.client.databases.query = AsyncMock(return_value=mock_response)

        # Create query
        query = NotionDatabaseQuery(
            database_id="db_123",
            filter={"property": "Status", "select": {"equals": "Active"}}
        )

        # Execute
        entries = await notion_client.query_database(query)

        # Assert
        assert len(entries) == 1
        assert entries[0].id == "entry_123"
        assert entries[0].database_id == "db_123"
        notion_client.client.databases.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_database_entry(self, notion_client):
        """Test creating a database entry."""
        # Mock response
        notion_client.client.pages.create = AsyncMock(
            return_value={"id": "entry_123"}
        )

        # Create draft
        draft = NotionDatabaseEntryDraft(
            database_id="db_123",
            properties={
                "Name": {
                    "title": [{"text": {"content": "New Entry"}}]
                }
            }
        )

        # Execute
        entry_id = await notion_client.create_database_entry(draft)

        # Assert
        assert entry_id == "entry_123"
        notion_client.client.pages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_block_children(self, notion_client):
        """Test getting block children."""
        # Mock response
        mock_response = {
            "results": [
                {
                    "id": "block_123",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"plain_text": "Test content"}]
                    },
                    "has_children": False,
                    "created_time": "2025-01-01T00:00:00.000Z",
                    "last_edited_time": "2025-01-01T00:00:00.000Z"
                }
            ]
        }

        notion_client.client.blocks.children.list = AsyncMock(return_value=mock_response)

        # Execute
        blocks = await notion_client.get_block_children("page_123")

        # Assert
        assert len(blocks) == 1
        assert blocks[0].id == "block_123"
        assert blocks[0].type == "paragraph"
        notion_client.client.blocks.children.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_append_blocks(self, notion_client):
        """Test appending blocks."""
        # Mock response
        mock_response = {
            "results": [
                {"id": "block_123"},
                {"id": "block_456"}
            ]
        }

        notion_client.client.blocks.children.append = AsyncMock(return_value=mock_response)

        # Create block drafts
        blocks = [
            NotionBlockDraft(
                type="paragraph",
                content={"rich_text": [{"type": "text", "text": {"content": "Test"}}]}
            )
        ]

        # Execute
        block_ids = await notion_client.append_blocks("page_123", blocks)

        # Assert
        assert len(block_ids) == 2
        assert block_ids[0] == "block_123"
        assert block_ids[1] == "block_456"
        notion_client.client.blocks.children.append.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_error_handling(self, notion_client):
        """Test error handling when creating a page."""
        # Mock error
        notion_client.client.pages.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Create draft
        draft = NotionPageDraft(
            title="Test Page",
            parent_id="parent_123",
            parent_type="page_id"
        )

        # Execute and assert
        with pytest.raises(Exception, match="Failed to create page: API Error"):
            await notion_client.create_page(draft)

    def test_client_requires_api_key(self):
        """Test that client requires API key."""
        with patch("app.config.settings.settings.notion_api_key", None):
            with pytest.raises(ValueError) as exc_info:
                NotionClient(api_key=None)

            assert "Notion API key is required" in str(exc_info.value)

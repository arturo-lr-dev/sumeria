"""
Unit tests for Notion MCP tools.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.mcp.tools.notion_tools import NotionTools
from app.domain.entities.notion_page import NotionPage
from app.domain.entities.notion_database import NotionDatabaseEntry
from app.domain.entities.notion_block import NotionBlock


@pytest.fixture
def notion_tools():
    """Create NotionTools instance."""
    return NotionTools()


@pytest.fixture
def mock_create_page_uc():
    """Mock CreatePageUseCase."""
    with patch("app.mcp.tools.notion_tools.CreatePageUseCase") as mock:
        yield mock


@pytest.fixture
def mock_search_pages_uc():
    """Mock SearchPagesUseCase."""
    with patch("app.mcp.tools.notion_tools.SearchPagesUseCase") as mock:
        yield mock


@pytest.fixture
def mock_query_database_uc():
    """Mock QueryDatabaseUseCase."""
    with patch("app.mcp.tools.notion_tools.QueryDatabaseUseCase") as mock:
        yield mock


class TestNotionTools:
    """Test NotionTools class."""

    @pytest.mark.asyncio
    async def test_create_page_success(self, notion_tools):
        """Test creating a page successfully."""
        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.page_id = "page_123"
        mock_response.error = None

        notion_tools.create_page_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.create_page(
            title="Test Page",
            parent_id="parent_123",
            parent_type="page_id"
        )

        # Assert
        assert result.success is True
        assert result.page_id == "page_123"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_create_page_error(self, notion_tools):
        """Test creating a page with error."""
        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.page_id = None
        mock_response.error = "API Error"

        notion_tools.create_page_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.create_page(
            title="Test Page",
            parent_id="parent_123"
        )

        # Assert
        assert result.success is False
        assert result.page_id is None
        assert result.error == "API Error"

    @pytest.mark.asyncio
    async def test_get_page_success(self, notion_tools):
        """Test getting a page successfully."""
        # Mock page entity
        mock_page = NotionPage(
            id="page_123",
            title="Test Page",
            parent_type="page_id",
            parent_id="parent_123",
            url="https://notion.so/page_123",
            archived=False,
            created_time=datetime(2025, 1, 1),
            last_edited_time=datetime(2025, 1, 2),
            properties={"test": "value"}
        )

        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.page = mock_page
        mock_response.error = None

        notion_tools.get_page_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.get_page("page_123")

        # Assert
        assert result.success is True
        assert result.page.id == "page_123"
        assert result.page.title == "Test Page"
        assert result.properties == {"test": "value"}

    @pytest.mark.asyncio
    async def test_update_page_success(self, notion_tools):
        """Test updating a page successfully."""
        # Mock page entity
        mock_page = NotionPage(
            id="page_123",
            title="Updated Page",
            parent_type="page_id",
            parent_id="parent_123",
            archived=False,
            created_time=datetime(2025, 1, 1),
            last_edited_time=datetime(2025, 1, 2)
        )

        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.page = mock_page
        mock_response.error = None

        notion_tools.update_page_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.update_page(
            page_id="page_123",
            archived=True
        )

        # Assert
        assert result.success is True
        assert result.page.title == "Updated Page"

    @pytest.mark.asyncio
    async def test_search_pages_success(self, notion_tools):
        """Test searching pages successfully."""
        # Mock page entities
        mock_page1 = NotionPage(
            id="page_1",
            title="Page 1",
            parent_type="workspace",
            created_time=datetime(2025, 1, 1),
            last_edited_time=datetime(2025, 1, 1)
        )
        mock_page2 = NotionPage(
            id="page_2",
            title="Page 2",
            parent_type="workspace",
            created_time=datetime(2025, 1, 2),
            last_edited_time=datetime(2025, 1, 2)
        )

        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.pages = [mock_page1, mock_page2]
        mock_response.count = 2
        mock_response.error = None

        notion_tools.search_pages_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.search_pages(
            query="test",
            filter_type="page"
        )

        # Assert
        assert result.success is True
        assert result.count == 2
        assert len(result.pages) == 2
        assert result.pages[0].id == "page_1"
        assert result.pages[1].id == "page_2"

    @pytest.mark.asyncio
    async def test_create_database_entry_success(self, notion_tools):
        """Test creating a database entry successfully."""
        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.entry_id = "entry_123"
        mock_response.error = None

        notion_tools.create_database_entry_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        properties = {
            "Name": {"title": [{"text": {"content": "Task 1"}}]}
        }
        result = await notion_tools.create_database_entry(
            database_id="db_123",
            properties=properties
        )

        # Assert
        assert result.success is True
        assert result.entry_id == "entry_123"

    @pytest.mark.asyncio
    async def test_query_database_success(self, notion_tools):
        """Test querying database successfully."""
        # Mock entry entities
        mock_entry1 = NotionDatabaseEntry(
            id="entry_1",
            database_id="db_123",
            properties={"Name": {"title": [{"plain_text": "Entry 1"}]}},
            url="https://notion.so/entry_1",
            created_time=datetime(2025, 1, 1),
            last_edited_time=datetime(2025, 1, 1)
        )
        mock_entry2 = NotionDatabaseEntry(
            id="entry_2",
            database_id="db_123",
            properties={"Name": {"title": [{"plain_text": "Entry 2"}]}},
            url="https://notion.so/entry_2",
            created_time=datetime(2025, 1, 2),
            last_edited_time=datetime(2025, 1, 2)
        )

        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.entries = [mock_entry1, mock_entry2]
        mock_response.count = 2
        mock_response.error = None

        notion_tools.query_database_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.query_database(
            database_id="db_123",
            filter={"property": "Status", "select": {"equals": "Active"}}
        )

        # Assert
        assert result.success is True
        assert result.count == 2
        assert len(result.entries) == 2
        assert result.entries[0].id == "entry_1"
        assert result.entries[0].database_id == "db_123"

    @pytest.mark.asyncio
    async def test_append_content_success(self, notion_tools):
        """Test appending content successfully."""
        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.block_ids = ["block_1", "block_2"]
        mock_response.count = 2
        mock_response.error = None

        notion_tools.append_blocks_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        blocks = [
            {
                "type": "paragraph",
                "content": {"rich_text": [{"type": "text", "text": {"content": "Test"}}]}
            }
        ]
        result = await notion_tools.append_content(
            page_id="page_123",
            blocks=blocks
        )

        # Assert
        assert result.success is True
        assert result.count == 2
        assert len(result.block_ids) == 2

    @pytest.mark.asyncio
    async def test_get_page_content_success(self, notion_tools):
        """Test getting page content successfully."""
        # Mock block entities
        mock_block1 = NotionBlock(
            id="block_1",
            type="paragraph",
            has_children=False
        )
        mock_block2 = NotionBlock(
            id="block_2",
            type="heading_1",
            has_children=False
        )

        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.blocks = [mock_block1, mock_block2]
        mock_response.count = 2
        mock_response.error = None

        notion_tools.get_page_content_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.get_page_content("page_123")

        # Assert
        assert result.success is True
        assert result.count == 2
        assert len(result.blocks) == 2
        assert result.blocks[0].type == "paragraph"
        assert result.blocks[1].type == "heading_1"

    @pytest.mark.asyncio
    async def test_search_pages_error(self, notion_tools):
        """Test search pages with error."""
        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.pages = []
        mock_response.count = 0
        mock_response.error = "Search failed"

        notion_tools.search_pages_uc.execute = AsyncMock(return_value=mock_response)

        # Execute
        result = await notion_tools.search_pages(query="test")

        # Assert
        assert result.success is False
        assert result.count == 0
        assert result.error == "Search failed"

    @pytest.mark.asyncio
    async def test_query_database_with_filters_and_sorts(self, notion_tools):
        """Test querying database with filters and sorting."""
        # Mock use case response
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.entries = []
        mock_response.count = 0
        mock_response.error = None

        notion_tools.query_database_uc.execute = AsyncMock(return_value=mock_response)

        # Execute with complex filters
        filter_obj = {
            "and": [
                {"property": "Status", "select": {"equals": "Active"}},
                {"property": "Priority", "number": {"greater_than": 3}}
            ]
        }
        sorts = [
            {"property": "Created", "direction": "descending"}
        ]

        result = await notion_tools.query_database(
            database_id="db_123",
            filter=filter_obj,
            sorts=sorts
        )

        # Assert
        assert result.success is True
        notion_tools.query_database_uc.execute.assert_called_once()

        # Verify the request was built correctly
        call_args = notion_tools.query_database_uc.execute.call_args
        request = call_args[0][0]
        assert request.database_id == "db_123"
        assert request.filter == filter_obj
        assert request.sorts == sorts

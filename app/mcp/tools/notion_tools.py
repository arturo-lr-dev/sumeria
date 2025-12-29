"""
MCP Tools for Notion operations.
Exposes Notion functionality through the MCP protocol.
"""
from typing import Optional
from pydantic import BaseModel

from app.application.use_cases.notion.create_page import CreatePageUseCase, CreatePageRequest
from app.application.use_cases.notion.get_page import GetPageUseCase, GetPageRequest
from app.application.use_cases.notion.update_page import UpdatePageUseCase, UpdatePageRequest
from app.application.use_cases.notion.search_pages import SearchPagesUseCase, SearchPagesRequest
from app.application.use_cases.notion.create_database_entry import (
    CreateDatabaseEntryUseCase,
    CreateDatabaseEntryRequest
)
from app.application.use_cases.notion.query_database import (
    QueryDatabaseUseCase,
    QueryDatabaseRequest
)
from app.application.use_cases.notion.append_blocks import (
    AppendBlocksUseCase,
    AppendBlocksRequest
)
from app.application.use_cases.notion.get_page_content import (
    GetPageContentUseCase,
    GetPageContentRequest
)


# Response models for structured output
class PageSummary(BaseModel):
    """Summary of a Notion page."""
    id: str
    title: str
    url: Optional[str] = None
    parent_type: str
    parent_id: Optional[str] = None
    archived: bool = False
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None


class CreatePageResult(BaseModel):
    """Result of creating a page."""
    success: bool
    page_id: Optional[str] = None
    error: Optional[str] = None


class GetPageResult(BaseModel):
    """Result of getting page details."""
    success: bool
    page: Optional[PageSummary] = None
    properties: Optional[dict] = None
    error: Optional[str] = None


class UpdatePageResult(BaseModel):
    """Result of updating a page."""
    success: bool
    page: Optional[PageSummary] = None
    error: Optional[str] = None


class SearchPagesResult(BaseModel):
    """Result of searching pages."""
    success: bool
    count: int = 0
    pages: list[PageSummary] = []
    error: Optional[str] = None


class DatabaseEntrySummary(BaseModel):
    """Summary of a database entry."""
    id: str
    database_id: Optional[str] = None
    url: Optional[str] = None
    properties: dict
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None


class CreateDatabaseEntryResult(BaseModel):
    """Result of creating a database entry."""
    success: bool
    entry_id: Optional[str] = None
    error: Optional[str] = None


class QueryDatabaseResult(BaseModel):
    """Result of querying a database."""
    success: bool
    count: int = 0
    entries: list[DatabaseEntrySummary] = []
    error: Optional[str] = None


class BlockSummary(BaseModel):
    """Summary of a content block."""
    id: Optional[str] = None
    type: str
    has_children: bool = False

    # Text content (for text-based blocks)
    text: Optional[str] = None

    # Table-specific fields
    table_width: Optional[int] = None
    has_column_header: Optional[bool] = None
    has_row_header: Optional[bool] = None
    cells: Optional[list[str]] = None  # For table_row blocks

    # Code block specific
    language: Optional[str] = None

    # Media blocks
    url: Optional[str] = None
    caption: Optional[str] = None

    # Children blocks
    children: Optional[list["BlockSummary"]] = None


class AppendBlocksResult(BaseModel):
    """Result of appending blocks."""
    success: bool
    count: int = 0
    block_ids: list[str] = []
    error: Optional[str] = None


class GetPageContentResult(BaseModel):
    """Result of getting page content."""
    success: bool
    count: int = 0
    blocks: list[BlockSummary] = []
    error: Optional[str] = None


def _block_to_summary(block) -> BlockSummary:
    """
    Convert NotionBlock entity to BlockSummary.

    Args:
        block: NotionBlock entity

    Returns:
        BlockSummary model
    """
    # Convert children recursively
    children = None
    if block.children:
        children = [_block_to_summary(child) for child in block.children]

    return BlockSummary(
        id=block.id,
        type=block.type,
        has_children=block.has_children,
        text=block.text,
        table_width=block.table_width,
        has_column_header=block.has_column_header,
        has_row_header=block.has_row_header,
        cells=block.cells,
        language=block.language,
        url=block.url,
        caption=block.caption,
        children=children
    )


class NotionTools:
    """Collection of Notion MCP tools."""

    def __init__(self):
        """Initialize use cases."""
        self.create_page_uc = CreatePageUseCase()
        self.get_page_uc = GetPageUseCase()
        self.update_page_uc = UpdatePageUseCase()
        self.search_pages_uc = SearchPagesUseCase()
        self.create_database_entry_uc = CreateDatabaseEntryUseCase()
        self.query_database_uc = QueryDatabaseUseCase()
        self.append_blocks_uc = AppendBlocksUseCase()
        self.get_page_content_uc = GetPageContentUseCase()

    async def create_page(
        self,
        title: str,
        parent_id: str,
        parent_type: str = "page_id",
        properties: Optional[dict] = None,
        children: Optional[list] = None,
        icon: Optional[dict] = None,
        cover: Optional[dict] = None
    ) -> CreatePageResult:
        """
        Create a new page in Notion.

        Args:
            title: Page title
            parent_id: Parent page or database ID
            parent_type: Type of parent (page_id, database_id, workspace)
            properties: Page properties (for database pages)
            children: Initial content blocks
            icon: Page icon
            cover: Page cover

        Returns:
            CreatePageResult with success status and page ID
        """
        request = CreatePageRequest(
            title=title,
            parent_id=parent_id,
            parent_type=parent_type,
            properties=properties,
            children=children,
            icon=icon,
            cover=cover
        )

        response = await self.create_page_uc.execute(request)

        return CreatePageResult(
            success=response.success,
            page_id=response.page_id,
            error=response.error
        )

    async def get_page(
        self,
        page_id: str
    ) -> GetPageResult:
        """
        Get detailed information about a Notion page.

        Args:
            page_id: Page ID

        Returns:
            GetPageResult with page details
        """
        request = GetPageRequest(page_id=page_id)

        response = await self.get_page_uc.execute(request)

        if not response.success or not response.page:
            return GetPageResult(
                success=False,
                error=response.error
            )

        page = response.page

        page_summary = PageSummary(
            id=page.id,
            title=page.title,
            url=page.url,
            parent_type=page.parent_type,
            parent_id=page.parent_id,
            archived=page.archived,
            created_time=page.created_time.isoformat() if page.created_time else None,
            last_edited_time=page.last_edited_time.isoformat() if page.last_edited_time else None
        )

        return GetPageResult(
            success=True,
            page=page_summary,
            properties=page.properties
        )

    async def update_page(
        self,
        page_id: str,
        properties: Optional[dict] = None,
        archived: Optional[bool] = None,
        icon: Optional[dict] = None,
        cover: Optional[dict] = None
    ) -> UpdatePageResult:
        """
        Update a Notion page.

        Args:
            page_id: Page ID
            properties: Properties to update
            archived: Archive status
            icon: Page icon
            cover: Page cover

        Returns:
            UpdatePageResult with updated page details
        """
        request = UpdatePageRequest(
            page_id=page_id,
            properties=properties,
            archived=archived,
            icon=icon,
            cover=cover
        )

        response = await self.update_page_uc.execute(request)

        if not response.success or not response.page:
            return UpdatePageResult(
                success=False,
                error=response.error
            )

        page = response.page

        page_summary = PageSummary(
            id=page.id,
            title=page.title,
            url=page.url,
            parent_type=page.parent_type,
            parent_id=page.parent_id,
            archived=page.archived,
            created_time=page.created_time.isoformat() if page.created_time else None,
            last_edited_time=page.last_edited_time.isoformat() if page.last_edited_time else None
        )

        return UpdatePageResult(
            success=True,
            page=page_summary
        )

    async def search_pages(
        self,
        query: Optional[str] = None,
        filter_type: Optional[str] = None,
        sort_direction: str = "descending",
        sort_timestamp: str = "last_edited_time",
        max_results: int = 100
    ) -> SearchPagesResult:
        """
        Search for pages in Notion workspace.

        Args:
            query: Search query text
            filter_type: Filter by type (page or database)
            sort_direction: Sort direction (ascending or descending)
            sort_timestamp: Sort by timestamp (last_edited_time or created_time)
            max_results: Maximum number of results

        Returns:
            SearchPagesResult with matching pages
        """
        request = SearchPagesRequest(
            query=query,
            filter_type=filter_type,
            sort_direction=sort_direction,
            sort_timestamp=sort_timestamp,
            max_results=max_results
        )

        response = await self.search_pages_uc.execute(request)

        if not response.success:
            return SearchPagesResult(
                success=False,
                error=response.error
            )

        pages = [
            PageSummary(
                id=page.id,
                title=page.title,
                url=page.url,
                parent_type=page.parent_type,
                parent_id=page.parent_id,
                archived=page.archived,
                created_time=page.created_time.isoformat() if page.created_time else None,
                last_edited_time=page.last_edited_time.isoformat() if page.last_edited_time else None
            )
            for page in response.pages
        ]

        return SearchPagesResult(
            success=True,
            count=response.count,
            pages=pages
        )

    async def create_database_entry(
        self,
        database_id: str,
        properties: dict,
        icon: Optional[dict] = None,
        cover: Optional[dict] = None,
        children: Optional[list] = None
    ) -> CreateDatabaseEntryResult:
        """
        Create a new entry in a Notion database.

        Args:
            database_id: Database ID
            properties: Entry properties (must match database schema)
            icon: Entry icon
            cover: Entry cover
            children: Initial content blocks

        Returns:
            CreateDatabaseEntryResult with success status and entry ID
        """
        request = CreateDatabaseEntryRequest(
            database_id=database_id,
            properties=properties,
            icon=icon,
            cover=cover,
            children=children
        )

        response = await self.create_database_entry_uc.execute(request)

        return CreateDatabaseEntryResult(
            success=response.success,
            entry_id=response.entry_id,
            error=response.error
        )

    async def query_database(
        self,
        database_id: str,
        filter: Optional[dict] = None,
        sorts: Optional[list] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> QueryDatabaseResult:
        """
        Query a Notion database with filters and sorting.

        Args:
            database_id: Database ID
            filter: Filter criteria (Notion filter format)
            sorts: Sort criteria (list of sort objects)
            start_cursor: Pagination cursor
            page_size: Number of results per page

        Returns:
            QueryDatabaseResult with matching entries
        """
        request = QueryDatabaseRequest(
            database_id=database_id,
            filter=filter,
            sorts=sorts,
            start_cursor=start_cursor,
            page_size=page_size
        )

        response = await self.query_database_uc.execute(request)

        if not response.success:
            return QueryDatabaseResult(
                success=False,
                error=response.error
            )

        entries = [
            DatabaseEntrySummary(
                id=entry.id,
                database_id=entry.database_id,
                url=entry.url,
                properties=entry.properties,
                created_time=entry.created_time.isoformat() if entry.created_time else None,
                last_edited_time=entry.last_edited_time.isoformat() if entry.last_edited_time else None
            )
            for entry in response.entries
        ]

        return QueryDatabaseResult(
            success=True,
            count=response.count,
            entries=entries
        )

    async def append_content(
        self,
        page_id: str,
        blocks: list[dict]
    ) -> AppendBlocksResult:
        """
        Append content blocks to a Notion page.

        Args:
            page_id: Page ID
            blocks: List of block objects to append

        Returns:
            AppendBlocksResult with created block IDs
        """
        request = AppendBlocksRequest(
            page_id=page_id,
            blocks=blocks
        )

        response = await self.append_blocks_uc.execute(request)

        return AppendBlocksResult(
            success=response.success,
            count=response.count,
            block_ids=response.block_ids,
            error=response.error
        )

    async def get_page_content(
        self,
        page_id: str,
        page_size: int = 100,
        recursive: bool = True
    ) -> GetPageContentResult:
        """
        Get content blocks from a Notion page.

        Args:
            page_id: Page ID
            page_size: Number of blocks to retrieve
            recursive: Fetch children blocks recursively (needed for tables)

        Returns:
            GetPageContentResult with page blocks including extracted text and table data
        """
        request = GetPageContentRequest(
            page_id=page_id,
            page_size=page_size,
            recursive=recursive
        )

        response = await self.get_page_content_uc.execute(request)

        if not response.success:
            return GetPageContentResult(
                success=False,
                error=response.error
            )

        # Convert NotionBlock entities to BlockSummary models with all fields
        blocks = [_block_to_summary(block) for block in response.blocks]

        return GetPageContentResult(
            success=True,
            count=response.count,
            blocks=blocks
        )


# Global instance
notion_tools = NotionTools()

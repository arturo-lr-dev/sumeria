"""
Notion API client implementation.
Handles all interactions with Notion API.
"""
from typing import Optional, Any
from notion_client import Client, AsyncClient
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.infrastructure.connectors.notion.schemas import NotionMapper
from app.domain.entities.notion_page import NotionPage, NotionPageDraft, NotionPageSearchCriteria
from app.domain.entities.notion_database import (
    NotionDatabase,
    NotionDatabaseEntry,
    NotionDatabaseEntryDraft,
    NotionDatabaseQuery
)
from app.domain.entities.notion_block import NotionBlock, NotionBlockDraft


class NotionClient:
    """
    Notion API client for workspace operations.
    Handles authentication and API communication.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Notion client.

        Args:
            api_key: Notion API key (will use settings if not provided)
        """
        self.api_key = api_key or settings.notion_api_key
        if not self.api_key:
            raise ValueError("Notion API key is required")

        self.client = AsyncClient(auth=self.api_key)

    # ============ Page Operations ============

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def create_page(self, draft: NotionPageDraft) -> str:
        """
        Create a new page.

        Args:
            draft: Page draft

        Returns:
            Page ID

        Raises:
            Exception: If API request fails
        """
        try:
            data = NotionMapper.from_page_draft(draft)
            result = await self.client.pages.create(**data)
            return result["id"]

        except Exception as error:
            raise Exception(f"Failed to create page: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_page(self, page_id: str) -> NotionPage:
        """
        Get page by ID.

        Args:
            page_id: Page ID

        Returns:
            NotionPage entity

        Raises:
            Exception: If API request fails
        """
        try:
            data = await self.client.pages.retrieve(page_id=page_id)
            return NotionMapper.to_page_entity(data)

        except Exception as error:
            raise Exception(f"Failed to get page: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def update_page(
        self,
        page_id: str,
        properties: Optional[dict] = None,
        archived: Optional[bool] = None,
        icon: Optional[dict] = None,
        cover: Optional[dict] = None
    ) -> NotionPage:
        """
        Update page properties.

        Args:
            page_id: Page ID
            properties: Properties to update
            archived: Archive status
            icon: Page icon
            cover: Page cover

        Returns:
            Updated NotionPage entity

        Raises:
            Exception: If API request fails
        """
        try:
            update_data = {}

            if properties is not None:
                update_data["properties"] = properties
            if archived is not None:
                update_data["archived"] = archived
            if icon is not None:
                update_data["icon"] = icon
            if cover is not None:
                update_data["cover"] = cover

            data = await self.client.pages.update(page_id=page_id, **update_data)
            return NotionMapper.to_page_entity(data)

        except Exception as error:
            raise Exception(f"Failed to update page: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def search(self, criteria: NotionPageSearchCriteria) -> list[NotionPage]:
        """
        Search pages in workspace.

        Args:
            criteria: Search criteria

        Returns:
            List of matching pages

        Raises:
            Exception: If API request fails
        """
        try:
            query_params = {}

            if criteria.query:
                query_params["query"] = criteria.query

            if criteria.filter_type:
                query_params["filter"] = {
                    "property": "object",
                    "value": criteria.filter_type
                }

            query_params["sort"] = {
                "direction": criteria.sort_direction,
                "timestamp": criteria.sort_timestamp
            }

            query_params["page_size"] = min(criteria.max_results, 100)

            data = await self.client.search(**query_params)

            pages = []
            for result in data.get("results", []):
                if result.get("object") == "page":
                    pages.append(NotionMapper.to_page_entity(result))

            return pages

        except Exception as error:
            raise Exception(f"Failed to search pages: {error}")

    # ============ Database Operations ============

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_database(self, database_id: str) -> NotionDatabase:
        """
        Get database by ID.

        Args:
            database_id: Database ID

        Returns:
            NotionDatabase entity

        Raises:
            Exception: If API request fails
        """
        try:
            data = await self.client.databases.retrieve(database_id=database_id)
            return NotionMapper.to_database_entity(data)

        except Exception as error:
            raise Exception(f"Failed to get database: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def query_database(self, query: NotionDatabaseQuery) -> list[NotionDatabaseEntry]:
        """
        Query database entries.

        Args:
            query: Database query criteria

        Returns:
            List of database entries

        Raises:
            Exception: If API request fails
        """
        try:
            query_params = {"database_id": query.database_id}

            if query.filter:
                query_params["filter"] = query.filter

            if query.sorts:
                query_params["sorts"] = query.sorts

            if query.start_cursor:
                query_params["start_cursor"] = query.start_cursor

            query_params["page_size"] = min(query.page_size, 100)

            data = await self.client.databases.query(**query_params)

            entries = []
            for result in data.get("results", []):
                entries.append(NotionMapper.to_database_entry_entity(result))

            return entries

        except Exception as error:
            raise Exception(f"Failed to query database: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def create_database_entry(self, draft: NotionDatabaseEntryDraft) -> str:
        """
        Create a new entry in a database.

        Args:
            draft: Database entry draft

        Returns:
            Entry ID (page ID)

        Raises:
            Exception: If API request fails
        """
        try:
            data = NotionMapper.from_database_entry_draft(draft)
            result = await self.client.pages.create(**data)
            return result["id"]

        except Exception as error:
            raise Exception(f"Failed to create database entry: {error}")

    # ============ Block Operations ============

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_block_children(
        self,
        block_id: str,
        page_size: int = 100,
        recursive: bool = True
    ) -> list[NotionBlock]:
        """
        Get children blocks of a block or page.

        Args:
            block_id: Block or page ID
            page_size: Number of results per page
            recursive: If True, recursively fetch children of blocks that have children (e.g., tables)

        Returns:
            List of child blocks

        Raises:
            Exception: If API request fails
        """
        try:
            data = await self.client.blocks.children.list(
                block_id=block_id,
                page_size=min(page_size, 100)
            )

            blocks = []
            for result in data.get("results", []):
                block = NotionMapper.to_block_entity(result)

                # If recursive mode and block has children, fetch them
                if recursive and block.has_children:
                    block.children = await self.get_block_children(
                        block_id=block.id,
                        page_size=page_size,
                        recursive=True
                    )

                blocks.append(block)

            return blocks

        except Exception as error:
            raise Exception(f"Failed to get block children: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def append_blocks(
        self,
        block_id: str,
        blocks: list[NotionBlockDraft]
    ) -> list[str]:
        """
        Append blocks to a page or block.

        Args:
            block_id: Parent block or page ID
            blocks: List of block drafts to append

        Returns:
            List of created block IDs

        Raises:
            Exception: If API request fails
        """
        try:
            children = [NotionMapper.from_block_draft(block) for block in blocks]

            data = await self.client.blocks.children.append(
                block_id=block_id,
                children=children
            )

            block_ids = [result["id"] for result in data.get("results", [])]
            return block_ids

        except Exception as error:
            raise Exception(f"Failed to append blocks: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def update_block(
        self,
        block_id: str,
        content: dict
    ) -> NotionBlock:
        """
        Update a block's content.

        Args:
            block_id: Block ID
            content: Updated content

        Returns:
            Updated NotionBlock entity

        Raises:
            Exception: If API request fails
        """
        try:
            data = await self.client.blocks.update(
                block_id=block_id,
                **content
            )

            return NotionMapper.to_block_entity(data)

        except Exception as error:
            raise Exception(f"Failed to update block: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def delete_block(self, block_id: str) -> None:
        """
        Delete (archive) a block.

        Args:
            block_id: Block ID

        Raises:
            Exception: If API request fails
        """
        try:
            await self.client.blocks.delete(block_id=block_id)

        except Exception as error:
            raise Exception(f"Failed to delete block: {error}")

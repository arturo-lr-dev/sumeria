"""
Get Page Content use case.
Handles retrieving content blocks from Notion pages.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_block import NotionBlock


@dataclass
class GetPageContentRequest:
    """Request to get page content."""
    page_id: str
    page_size: int = 100
    recursive: bool = True  # Fetch children recursively (needed for tables, etc.)


@dataclass
class GetPageContentResponse:
    """Response from getting page content."""
    success: bool
    blocks: list[NotionBlock] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        if self.blocks is None:
            self.blocks = []

    def to_dict(self, include_content: bool = False, include_metadata: bool = False) -> dict:
        """
        Convert response to dictionary with serialized blocks.

        Args:
            include_content: Include raw API content in blocks
            include_metadata: Include metadata (timestamps, created_by, etc.)

        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "count": self.count,
            "blocks": [
                block.to_dict(include_content=include_content, include_metadata=include_metadata)
                for block in self.blocks
            ],
            "error": self.error
        }


class GetPageContentUseCase:
    """Use case for getting page content."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: GetPageContentRequest) -> GetPageContentResponse:
        """
        Execute the use case.

        Args:
            request: Get page content request

        Returns:
            Response with content blocks or error
        """
        try:
            # Get blocks (with optional recursive children fetch)
            blocks = await self.client.get_block_children(
                block_id=request.page_id,
                page_size=request.page_size,
                recursive=request.recursive
            )

            return GetPageContentResponse(
                success=True,
                blocks=blocks,
                count=len(blocks)
            )

        except Exception as e:
            return GetPageContentResponse(
                success=False,
                error=str(e)
            )

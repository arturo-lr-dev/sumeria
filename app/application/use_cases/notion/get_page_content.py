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
            # Get blocks
            blocks = await self.client.get_block_children(
                block_id=request.page_id,
                page_size=request.page_size
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

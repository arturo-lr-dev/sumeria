"""
Append Blocks use case.
Handles appending content blocks to Notion pages.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_block import NotionBlockDraft


@dataclass
class AppendBlocksRequest:
    """Request to append blocks."""
    page_id: str
    blocks: list[dict]


@dataclass
class AppendBlocksResponse:
    """Response from appending blocks."""
    success: bool
    block_ids: list[str] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        if self.block_ids is None:
            self.block_ids = []


class AppendBlocksUseCase:
    """Use case for appending blocks to pages."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: AppendBlocksRequest) -> AppendBlocksResponse:
        """
        Execute the use case.

        Args:
            request: Append blocks request

        Returns:
            Response with created block IDs or error
        """
        try:
            # Convert block dicts to drafts
            block_drafts = []
            for block_data in request.blocks:
                draft = NotionBlockDraft(
                    type=block_data.get("type", "paragraph"),
                    content=block_data.get("content", {}),
                    children=block_data.get("children")
                )
                block_drafts.append(draft)

            # Append blocks
            block_ids = await self.client.append_blocks(
                block_id=request.page_id,
                blocks=block_drafts
            )

            return AppendBlocksResponse(
                success=True,
                block_ids=block_ids,
                count=len(block_ids)
            )

        except Exception as e:
            return AppendBlocksResponse(
                success=False,
                error=str(e)
            )

"""
Update Page use case.
Handles updating page properties in Notion.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_page import NotionPage


@dataclass
class UpdatePageRequest:
    """Request to update a page."""
    page_id: str
    properties: Optional[dict] = None
    archived: Optional[bool] = None
    icon: Optional[dict] = None
    cover: Optional[dict] = None


@dataclass
class UpdatePageResponse:
    """Response from updating a page."""
    success: bool
    page: Optional[NotionPage] = None
    error: Optional[str] = None


class UpdatePageUseCase:
    """Use case for updating pages."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: UpdatePageRequest) -> UpdatePageResponse:
        """
        Execute the use case.

        Args:
            request: Update page request

        Returns:
            Response with updated page or error
        """
        try:
            # Update page
            page = await self.client.update_page(
                page_id=request.page_id,
                properties=request.properties,
                archived=request.archived,
                icon=request.icon,
                cover=request.cover
            )

            return UpdatePageResponse(
                success=True,
                page=page
            )

        except Exception as e:
            return UpdatePageResponse(
                success=False,
                error=str(e)
            )

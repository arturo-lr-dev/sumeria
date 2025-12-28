"""
Get Page use case.
Handles retrieving page details from Notion.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_page import NotionPage


@dataclass
class GetPageRequest:
    """Request to get a page."""
    page_id: str


@dataclass
class GetPageResponse:
    """Response from getting a page."""
    success: bool
    page: Optional[NotionPage] = None
    error: Optional[str] = None


class GetPageUseCase:
    """Use case for getting page details."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: GetPageRequest) -> GetPageResponse:
        """
        Execute the use case.

        Args:
            request: Get page request

        Returns:
            Response with page details or error
        """
        try:
            # Get page
            page = await self.client.get_page(request.page_id)

            return GetPageResponse(
                success=True,
                page=page
            )

        except Exception as e:
            return GetPageResponse(
                success=False,
                error=str(e)
            )

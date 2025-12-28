"""
Search Pages use case.
Handles searching for pages in Notion workspace.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_page import NotionPage, NotionPageSearchCriteria


@dataclass
class SearchPagesRequest:
    """Request to search pages."""
    query: Optional[str] = None
    filter_type: Optional[str] = None
    sort_direction: str = "descending"
    sort_timestamp: str = "last_edited_time"
    max_results: int = 100


@dataclass
class SearchPagesResponse:
    """Response from searching pages."""
    success: bool
    pages: list[NotionPage] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        if self.pages is None:
            self.pages = []


class SearchPagesUseCase:
    """Use case for searching pages."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: SearchPagesRequest) -> SearchPagesResponse:
        """
        Execute the use case.

        Args:
            request: Search pages request

        Returns:
            Response with matching pages or error
        """
        try:
            # Create search criteria
            criteria = NotionPageSearchCriteria(
                query=request.query,
                filter_type=request.filter_type,
                sort_direction=request.sort_direction,
                sort_timestamp=request.sort_timestamp,
                max_results=request.max_results
            )

            # Search pages
            pages = await self.client.search(criteria)

            return SearchPagesResponse(
                success=True,
                pages=pages,
                count=len(pages)
            )

        except Exception as e:
            return SearchPagesResponse(
                success=False,
                error=str(e)
            )

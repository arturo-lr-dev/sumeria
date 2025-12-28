"""
Create Page use case.
Handles creating new pages in Notion.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_page import NotionPageDraft


@dataclass
class CreatePageRequest:
    """Request to create a page."""
    title: str
    parent_id: str
    parent_type: str = "page_id"
    properties: Optional[dict] = None
    children: Optional[list] = None
    icon: Optional[dict] = None
    cover: Optional[dict] = None


@dataclass
class CreatePageResponse:
    """Response from creating a page."""
    success: bool
    page_id: Optional[str] = None
    error: Optional[str] = None


class CreatePageUseCase:
    """Use case for creating pages."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: CreatePageRequest) -> CreatePageResponse:
        """
        Execute the use case.

        Args:
            request: Create page request

        Returns:
            Response with page ID or error
        """
        try:
            # Create draft
            draft = NotionPageDraft(
                title=request.title,
                parent_id=request.parent_id,
                parent_type=request.parent_type,
                properties=request.properties,
                children=request.children,
                icon=request.icon,
                cover=request.cover
            )

            # Create page
            page_id = await self.client.create_page(draft)

            return CreatePageResponse(
                success=True,
                page_id=page_id
            )

        except Exception as e:
            return CreatePageResponse(
                success=False,
                error=str(e)
            )

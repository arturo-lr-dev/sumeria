"""
Create Database Entry use case.
Handles creating new entries in Notion databases.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_database import NotionDatabaseEntryDraft


@dataclass
class CreateDatabaseEntryRequest:
    """Request to create a database entry."""
    database_id: str
    properties: dict
    icon: Optional[dict] = None
    cover: Optional[dict] = None
    children: Optional[list] = None


@dataclass
class CreateDatabaseEntryResponse:
    """Response from creating a database entry."""
    success: bool
    entry_id: Optional[str] = None
    error: Optional[str] = None


class CreateDatabaseEntryUseCase:
    """Use case for creating database entries."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: CreateDatabaseEntryRequest) -> CreateDatabaseEntryResponse:
        """
        Execute the use case.

        Args:
            request: Create database entry request

        Returns:
            Response with entry ID or error
        """
        try:
            # Create draft
            draft = NotionDatabaseEntryDraft(
                database_id=request.database_id,
                properties=request.properties,
                icon=request.icon,
                cover=request.cover,
                children=request.children
            )

            # Create entry
            entry_id = await self.client.create_database_entry(draft)

            return CreateDatabaseEntryResponse(
                success=True,
                entry_id=entry_id
            )

        except Exception as e:
            return CreateDatabaseEntryResponse(
                success=False,
                error=str(e)
            )

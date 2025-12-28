"""
Query Database use case.
Handles querying Notion databases with filters and sorting.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.notion.client import NotionClient
from app.domain.entities.notion_database import NotionDatabaseEntry, NotionDatabaseQuery


@dataclass
class QueryDatabaseRequest:
    """Request to query a database."""
    database_id: str
    filter: Optional[dict] = None
    sorts: Optional[list] = None
    start_cursor: Optional[str] = None
    page_size: int = 100


@dataclass
class QueryDatabaseResponse:
    """Response from querying a database."""
    success: bool
    entries: list[NotionDatabaseEntry] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        if self.entries is None:
            self.entries = []


class QueryDatabaseUseCase:
    """Use case for querying databases."""

    def __init__(self, client: Optional[NotionClient] = None):
        """Initialize use case."""
        self.client = client or NotionClient()

    async def execute(self, request: QueryDatabaseRequest) -> QueryDatabaseResponse:
        """
        Execute the use case.

        Args:
            request: Query database request

        Returns:
            Response with database entries or error
        """
        try:
            # Create query
            query = NotionDatabaseQuery(
                database_id=request.database_id,
                filter=request.filter,
                sorts=request.sorts,
                start_cursor=request.start_cursor,
                page_size=request.page_size
            )

            # Query database
            entries = await self.client.query_database(query)

            return QueryDatabaseResponse(
                success=True,
                entries=entries,
                count=len(entries)
            )

        except Exception as e:
            return QueryDatabaseResponse(
                success=False,
                error=str(e)
            )

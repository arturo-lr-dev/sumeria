"""
Unit tests for QueryDatabase use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.query_database import (
    QueryDatabaseUseCase,
    QueryDatabaseRequest,
    QueryDatabaseResponse
)
from app.domain.entities.notion_database import NotionDatabaseEntry


class TestQueryDatabaseUseCase:
    """Test suite for QueryDatabase use case."""

    @pytest.fixture
    def mock_entries(self):
        """Create mock database entries."""
        return [
            NotionDatabaseEntry(
                id="entry1",
                properties={"Name": {"title": [{"text": {"content": "Entry 1"}}]}}
            ),
            NotionDatabaseEntry(
                id="entry2",
                properties={"Name": {"title": [{"text": {"content": "Entry 2"}}]}}
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_entries):
        """Create mock Notion client."""
        client = MagicMock()
        client.query_database = AsyncMock(return_value=mock_entries)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return QueryDatabaseUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_query_database_success(self, use_case, mock_client, mock_entries):
        """Test successful database query."""
        request = QueryDatabaseRequest(database_id="db123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.entries) == 2
        assert response.error is None
        mock_client.query_database.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_database_with_filter(self, use_case, mock_client):
        """Test querying database with filter."""
        request = QueryDatabaseRequest(
            database_id="db123",
            filter={
                "property": "Status",
                "select": {"equals": "Done"}
            }
        )

        await use_case.execute(request)

        query = mock_client.query_database.call_args[0][0]
        assert query.database_id == "db123"
        assert query.filter is not None

    @pytest.mark.asyncio
    async def test_query_database_with_sorts(self, use_case, mock_client):
        """Test querying database with sorting."""
        request = QueryDatabaseRequest(
            database_id="db123",
            sorts=[
                {"property": "Created", "direction": "descending"}
            ]
        )

        await use_case.execute(request)

        query = mock_client.query_database.call_args[0][0]
        assert query.sorts is not None
        assert len(query.sorts) == 1

    @pytest.mark.asyncio
    async def test_query_database_with_pagination(self, use_case, mock_client):
        """Test querying database with pagination."""
        request = QueryDatabaseRequest(
            database_id="db123",
            start_cursor="cursor123",
            page_size=50
        )

        await use_case.execute(request)

        query = mock_client.query_database.call_args[0][0]
        assert query.start_cursor == "cursor123"
        assert query.page_size == 50

    @pytest.mark.asyncio
    async def test_query_database_empty_results(self, use_case, mock_client):
        """Test query with no results."""
        mock_client.query_database = AsyncMock(return_value=[])

        request = QueryDatabaseRequest(database_id="db123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.entries) == 0

    @pytest.mark.asyncio
    async def test_query_database_failure(self, use_case, mock_client):
        """Test database query failure."""
        mock_client.query_database.side_effect = Exception("API error")

        request = QueryDatabaseRequest(database_id="db123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "API error" in response.error

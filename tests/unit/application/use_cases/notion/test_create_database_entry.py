"""
Unit tests for CreateDatabaseEntry use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.create_database_entry import (
    CreateDatabaseEntryUseCase,
    CreateDatabaseEntryRequest,
    CreateDatabaseEntryResponse
)


class TestCreateDatabaseEntryUseCase:
    """Test suite for CreateDatabaseEntry use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Notion client."""
        client = MagicMock()
        client.create_database_entry = AsyncMock(return_value="entry123")
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return CreateDatabaseEntryUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_create_database_entry_basic(self, use_case, mock_client):
        """Test creating a basic database entry."""
        request = CreateDatabaseEntryRequest(
            database_id="db123",
            properties={
                "Name": {"title": [{"text": {"content": "Task 1"}}]},
                "Status": {"select": {"name": "To Do"}}
            }
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.entry_id == "entry123"
        assert response.error is None
        mock_client.create_database_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_database_entry_with_multiple_properties(self, use_case, mock_client):
        """Test creating entry with multiple property types."""
        request = CreateDatabaseEntryRequest(
            database_id="db123",
            properties={
                "Name": {"title": [{"text": {"content": "Project X"}}]},
                "Status": {"select": {"name": "In Progress"}},
                "Priority": {"select": {"name": "High"}},
                "Due Date": {"date": {"start": "2025-02-01"}},
                "Tags": {"multi_select": [{"name": "urgent"}, {"name": "important"}]}
            }
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_database_entry.call_args[0][0]
        assert draft.database_id == "db123"
        assert "Name" in draft.properties
        assert "Tags" in draft.properties

    @pytest.mark.asyncio
    async def test_create_database_entry_with_children(self, use_case, mock_client):
        """Test creating entry with child blocks."""
        request = CreateDatabaseEntryRequest(
            database_id="db123",
            properties={"Name": {"title": [{"text": {"content": "Task"}}]}},
            children=[
                {"type": "paragraph", "paragraph": {"text": [{"text": {"content": "Description"}}]}}
            ]
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_database_entry.call_args[0][0]
        assert draft.children is not None
        assert len(draft.children) == 1

    @pytest.mark.asyncio
    async def test_create_database_entry_failure(self, use_case, mock_client):
        """Test database entry creation failure."""
        mock_client.create_database_entry.side_effect = Exception("API error")

        request = CreateDatabaseEntryRequest(
            database_id="db123",
            properties={"Name": {"title": [{"text": {"content": "Task"}}]}}
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert response.entry_id is None
        assert "API error" in response.error

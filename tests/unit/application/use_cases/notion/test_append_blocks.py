"""
Unit tests for AppendBlocks use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.notion.append_blocks import (
    AppendBlocksUseCase,
    AppendBlocksRequest,
    AppendBlocksResponse
)


class TestAppendBlocksUseCase:
    """Test suite for AppendBlocks use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Notion client."""
        client = MagicMock()
        client.append_blocks = AsyncMock(return_value=["block1", "block2"])
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return AppendBlocksUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_append_blocks_success(self, use_case, mock_client):
        """Test successful block appending."""
        request = AppendBlocksRequest(
            page_id="page123",
            blocks=[
                {"type": "paragraph", "content": {"text": "Hello"}},
                {"type": "heading_1", "content": {"text": "Title"}}
            ]
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.block_ids) == 2
        assert response.error is None
        mock_client.append_blocks.assert_called_once()

    @pytest.mark.asyncio
    async def test_append_single_block(self, use_case, mock_client):
        """Test appending a single block."""
        mock_client.append_blocks = AsyncMock(return_value=["block1"])

        request = AppendBlocksRequest(
            page_id="page123",
            blocks=[{"type": "paragraph", "content": {"text": "Single block"}}]
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 1

    @pytest.mark.asyncio
    async def test_append_blocks_with_children(self, use_case, mock_client):
        """Test appending blocks with nested children."""
        request = AppendBlocksRequest(
            page_id="page123",
            blocks=[
                {
                    "type": "toggle",
                    "content": {"text": "Toggle block"},
                    "children": [
                        {"type": "paragraph", "content": {"text": "Nested paragraph"}}
                    ]
                }
            ]
        )

        response = await use_case.execute(request)

        assert response.success is True

        blocks = mock_client.append_blocks.call_args[1]["blocks"]
        assert len(blocks) == 1
        assert blocks[0].children is not None

    @pytest.mark.asyncio
    async def test_append_blocks_default_type(self, use_case, mock_client):
        """Test appending blocks with default paragraph type."""
        request = AppendBlocksRequest(
            page_id="page123",
            blocks=[{"content": {"text": "Default type"}}]
        )

        response = await use_case.execute(request)

        assert response.success is True

        blocks = mock_client.append_blocks.call_args[1]["blocks"]
        assert blocks[0].type == "paragraph"

    @pytest.mark.asyncio
    async def test_append_blocks_failure(self, use_case, mock_client):
        """Test block appending failure."""
        mock_client.append_blocks.side_effect = Exception("API error")

        request = AppendBlocksRequest(
            page_id="page123",
            blocks=[{"type": "paragraph", "content": {"text": "Test"}}]
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "API error" in response.error

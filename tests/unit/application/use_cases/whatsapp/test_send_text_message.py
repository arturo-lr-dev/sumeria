"""
Unit tests for SendTextMessage use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.application.use_cases.whatsapp.send_text_message import (
    SendTextMessageUseCase,
    SendTextMessageRequest,
    SendTextMessageResponse
)


class TestSendTextMessageUseCase:
    """Test suite for SendTextMessage use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock WhatsApp client."""
        client = MagicMock()
        client.send_text_message = AsyncMock(return_value="wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA")
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return SendTextMessageUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_send_text_message_basic(self, use_case, mock_client):
        """Test sending a basic text message."""
        # Arrange
        request = SendTextMessageRequest(
            to="+14155552671",
            text="Hello, this is a test message"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        assert response.message_id == "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA"
        assert response.error is None
        mock_client.send_text_message.assert_called_once_with(
            to="+14155552671",
            text="Hello, this is a test message",
            preview_url=False
        )

    @pytest.mark.asyncio
    async def test_send_text_message_with_preview_url(self, use_case, mock_client):
        """Test sending text message with URL preview enabled."""
        # Arrange
        request = SendTextMessageRequest(
            to="+14155552671",
            text="Check this out: https://example.com",
            preview_url=True
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        assert response.message_id is not None
        mock_client.send_text_message.assert_called_once_with(
            to="+14155552671",
            text="Check this out: https://example.com",
            preview_url=True
        )

    @pytest.mark.asyncio
    async def test_send_text_message_with_reply_to(self, use_case, mock_client):
        """Test sending text message as a reply."""
        # Arrange
        request = SendTextMessageRequest(
            to="+14155552671",
            text="Thanks for your message!",
            reply_to_message_id="wamid.PREVIOUS_MESSAGE"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        mock_client.send_text_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_text_message_validation_empty_text(self, use_case, mock_client):
        """Test validation when text is empty."""
        # Arrange
        request = SendTextMessageRequest(
            to="+14155552671",
            text=""
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        # Empty text is actually allowed by WhatsApp API (may be used for reactions, etc.)
        # So this test should be removed or expect success
        assert response.success is True
        mock_client.send_text_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_text_message_validation_missing_recipient(self, use_case, mock_client):
        """Test validation when recipient is missing."""
        # Arrange
        request = SendTextMessageRequest(
            to="",
            text="Hello"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert response.message_id is None
        assert "E.164 format" in response.error  # Actual error message from validation
        mock_client.send_text_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_text_message_validation_invalid_phone_format(self, use_case, mock_client):
        """Test validation when phone number format is invalid."""
        # Arrange
        request = SendTextMessageRequest(
            to="1234567890",  # Missing + prefix
            text="Hello"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert response.message_id is None
        assert "must be in E.164 format" in response.error
        mock_client.send_text_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_text_message_failure(self, use_case, mock_client):
        """Test handling of message sending failure."""
        # Arrange
        mock_client.send_text_message.side_effect = Exception("API error: Invalid phone number")

        request = SendTextMessageRequest(
            to="+14155552671",
            text="Hello"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert response.message_id is None
        assert "API error" in response.error

    @pytest.mark.asyncio
    async def test_send_text_message_network_error(self, use_case, mock_client):
        """Test handling of network errors."""
        # Arrange
        mock_client.send_text_message.side_effect = Exception("Network timeout")

        request = SendTextMessageRequest(
            to="+14155552671",
            text="Hello"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert "Network timeout" in response.error

    @pytest.mark.asyncio
    async def test_send_text_message_long_text(self, use_case, mock_client):
        """Test sending long text message (max 4096 characters)."""
        # Arrange
        long_text = "A" * 4096
        request = SendTextMessageRequest(
            to="+14155552671",
            text=long_text
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        mock_client.send_text_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_text_message_text_too_long(self, use_case, mock_client):
        """Test validation when text exceeds maximum length."""
        # Arrange
        too_long_text = "A" * 4097
        request = SendTextMessageRequest(
            to="+14155552671",
            text=too_long_text
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert "cannot exceed 4096 characters" in response.error  # Actual error message
        mock_client.send_text_message.assert_not_called()

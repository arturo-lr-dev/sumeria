"""
Unit tests for SendTemplateMessage use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.application.use_cases.whatsapp.send_template_message import (
    SendTemplateMessageUseCase,
    SendTemplateMessageRequest,
    SendTemplateMessageResponse
)


class TestSendTemplateMessageUseCase:
    """Test suite for SendTemplateMessage use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock WhatsApp client."""
        client = MagicMock()
        client.send_template_message = AsyncMock(return_value="wamid.TEMPLATE123")
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return SendTemplateMessageUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_send_template_basic(self, use_case, mock_client):
        """Test sending basic template message."""
        # Arrange
        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="order_confirmation",
            language="en_US",
            parameters=["John Doe", "12345", "Friday"]
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        assert response.message_id == "wamid.TEMPLATE123"
        assert response.error is None
        mock_client.send_template_message.assert_called_once_with(
            to="+14155552671",
            template_name="order_confirmation",
            language="en_US",
            parameters=["John Doe", "12345", "Friday"]
        )

    @pytest.mark.asyncio
    async def test_send_template_without_parameters(self, use_case, mock_client):
        """Test sending template without parameters."""
        # Arrange
        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="simple_greeting",
            language="en_US"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        mock_client.send_template_message.assert_called_once_with(
            to="+14155552671",
            template_name="simple_greeting",
            language="en_US",
            parameters=[]
        )

    @pytest.mark.asyncio
    async def test_send_template_with_empty_parameters(self, use_case, mock_client):
        """Test sending template with empty parameters list."""
        # Arrange
        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="hello_world",
            language="es_ES",
            parameters=[]
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        mock_client.send_template_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_template_different_languages(self, use_case, mock_client):
        """Test sending templates in different languages."""
        # Arrange
        languages = ["en_US", "es_ES", "fr_FR", "pt_BR"]

        for lang in languages:
            request = SendTemplateMessageRequest(
                to="+14155552671",
                template_name="welcome_message",
                language=lang,
                parameters=["User"]
            )

            # Act
            response = await use_case.execute(request)

            # Assert
            assert response.success is True

        assert mock_client.send_template_message.call_count == len(languages)

    @pytest.mark.asyncio
    async def test_send_template_validation_missing_name(self, use_case, mock_client):
        """Test validation when template name is missing."""
        # Arrange
        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="",
            language="en_US"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert "template_name is required" in response.error
        mock_client.send_template_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_template_validation_missing_language(self, use_case, mock_client):
        """Test that empty language is sent to API (no validation in use case)."""
        # Arrange
        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="order_confirmation",
            language=""
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        # No validation for empty language in use case, so it will be sent to API
        assert response.success is True
        mock_client.send_template_message.assert_called_once_with(
            to="+14155552671",
            template_name="order_confirmation",
            language="",
            parameters=[]
        )

    @pytest.mark.asyncio
    async def test_send_template_validation_invalid_phone(self, use_case, mock_client):
        """Test validation with invalid phone number."""
        # Arrange
        request = SendTemplateMessageRequest(
            to="1234567890",  # Missing + prefix
            template_name="order_confirmation",
            language="en_US"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert "E.164 format" in response.error
        mock_client.send_template_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_template_failure_template_not_approved(self, use_case, mock_client):
        """Test handling when template is not approved."""
        # Arrange
        mock_client.send_template_message.side_effect = Exception(
            "Template not approved or does not exist"
        )

        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="unapproved_template",
            language="en_US"
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert "not approved" in response.error

    @pytest.mark.asyncio
    async def test_send_template_failure_parameter_count_mismatch(self, use_case, mock_client):
        """Test handling when parameter count doesn't match template."""
        # Arrange
        mock_client.send_template_message.side_effect = Exception(
            "Parameter count mismatch"
        )

        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="order_confirmation",
            language="en_US",
            parameters=["John"]  # Missing required parameters
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert "Parameter" in response.error

    @pytest.mark.asyncio
    async def test_send_template_with_many_parameters(self, use_case, mock_client):
        """Test sending template with many parameters."""
        # Arrange
        parameters = [f"Param{i}" for i in range(1, 11)]  # 10 parameters
        request = SendTemplateMessageRequest(
            to="+14155552671",
            template_name="complex_template",
            language="en_US",
            parameters=parameters
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        call_params = mock_client.send_template_message.call_args[1]["parameters"]
        assert len(call_params) == 10

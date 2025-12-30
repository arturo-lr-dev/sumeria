"""
Unit tests for WhatsApp client.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.infrastructure.connectors.whatsapp.client import WhatsAppClient
from app.domain.entities.whatsapp_message import WhatsAppMedia


@pytest.fixture
def whatsapp_client():
    """Create a WhatsApp client with mocked settings."""
    # Create a WhatsAppClient with explicit parameters to avoid settings dependency
    client = WhatsAppClient(
        access_token="test_access_token",
        phone_number_id="123456789"
    )
    # Store business_account_id for tests that need it
    client.business_account_id = "test_business_account_id"
    return client


@pytest.mark.asyncio
async def test_send_text_message_success(whatsapp_client):
    """Test sending a text message successfully."""
    # Arrange
    to = "+14155552671"
    text = "Hello, this is a test message"
    mock_response = {
        "messaging_product": "whatsapp",
        "messages": [
            {"id": "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA"}
        ]
    }

    # Act
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await whatsapp_client.send_text_message(to, text, preview_url=False)

    # Assert
    assert result == "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_send_text_message_with_preview_url(whatsapp_client):
    """Test sending a text message with URL preview enabled."""
    # Arrange
    to = "+14155552671"
    text = "Check this out: https://example.com"
    mock_response = {
        "messages": [{"id": "wamid.TEST123"}]
    }

    # Act
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await whatsapp_client.send_text_message(to, text, preview_url=True)

    # Assert
    assert result == "wamid.TEST123"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_send_media_message_with_url(whatsapp_client):
    """Test sending media message using URL."""
    # Arrange
    to = "+14155552671"
    media = WhatsAppMedia(
        media_type="image",
        media_url="https://example.com/image.jpg",
        caption="Test image"
    )
    mock_response = {
        "messages": [{"id": "wamid.IMAGE123"}]
    }

    # Act
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await whatsapp_client.send_media_message(to, media)

    # Assert
    assert result == "wamid.IMAGE123"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_send_media_message_with_id(whatsapp_client):
    """Test sending media message using media ID."""
    # Arrange
    to = "+14155552671"
    media = WhatsAppMedia(
        media_type="document",
        media_id="1234567890",
        filename="report.pdf",
        caption="Monthly report"
    )
    mock_response = {
        "messages": [{"id": "wamid.DOC456"}]
    }

    # Act
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await whatsapp_client.send_media_message(to, media)

    # Assert
    assert result == "wamid.DOC456"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_send_template_message_success(whatsapp_client):
    """Test sending a template message successfully."""
    # Arrange
    to = "+14155552671"
    template_name = "order_confirmation"
    language = "en_US"
    parameters = ["John Doe", "12345", "Friday"]
    mock_response = {
        "messages": [{"id": "wamid.TEMPLATE789"}]
    }

    # Act
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await whatsapp_client.send_template_message(to, template_name, language, parameters)

    # Assert
    assert result == "wamid.TEMPLATE789"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_upload_media_success(whatsapp_client):
    """Test uploading media successfully."""
    # Arrange
    file_data = b"fake image data"
    mime_type = "image/jpeg"
    filename = "test.jpg"

    mock_response_obj = MagicMock()
    mock_response_obj.json.return_value = {"id": "1234567890123456"}
    mock_response_obj.raise_for_status = MagicMock()

    # Act
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.post = AsyncMock(return_value=mock_response_obj)
        mock_client_class.return_value = mock_client_instance

        result = await whatsapp_client.upload_media(file_data, mime_type, filename)

    # Assert
    assert result == "1234567890123456"
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_media_url_success(whatsapp_client):
    """Test getting media URL successfully."""
    # Arrange
    media_id = "1234567890123456"
    mock_response = {
        "url": "https://lookaside.fbsbx.com/whatsapp_business/attachments/?mid=123456",
        "mime_type": "image/jpeg",
        "file_size": 123456
    }

    # Act
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await whatsapp_client.get_media_url(media_id)

    # Assert
    assert result == "https://lookaside.fbsbx.com/whatsapp_business/attachments/?mid=123456"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_download_media_success(whatsapp_client):
    """Test downloading media successfully."""
    # Arrange
    media_id = "1234567890123456"
    media_url = "https://lookaside.fbsbx.com/whatsapp_business/attachments/?mid=123456"
    media_data = b"fake media content"

    mock_url_response = {
        "url": media_url,
        "mime_type": "image/jpeg"
    }

    # Mock both the first _request (get URL) and the httpx client request
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request, \
         patch('httpx.AsyncClient') as mock_client_class:
        # Setup mocks
        mock_request.return_value = mock_url_response

        mock_response = MagicMock()
        mock_response.content = media_data
        mock_response.headers = {"Content-Type": "image/jpeg"}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client_instance

        data, mime_type = await whatsapp_client.download_media(media_id)

    # Assert
    assert data == media_data
    assert mime_type == "image/jpeg"


@pytest.mark.asyncio
async def test_mark_message_as_read_success(whatsapp_client):
    """Test marking message as read successfully."""
    # Arrange
    message_id = "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA"
    mock_response = {
        "success": True
    }

    # Act
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        await whatsapp_client.mark_message_as_read(message_id)

    # Assert
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_list_templates_success(whatsapp_client):
    """Test listing templates successfully."""
    # Arrange
    mock_response = {
        "data": [
            {
                "id": "template_001",
                "name": "order_confirmation",
                "language": "en_US",
                "status": "APPROVED",
                "category": "UTILITY",
                "components": [
                    {
                        "type": "BODY",
                        "text": "Hi {{1}}, your order #{{2}} has been confirmed."
                    }
                ]
            },
            {
                "id": "template_002",
                "name": "appointment_reminder",
                "language": "en_US",
                "status": "PENDING",
                "category": "UTILITY",
                "components": []
            }
        ]
    }

    # Act
    with patch('app.infrastructure.connectors.whatsapp.client.settings') as mock_settings, \
         patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_settings.whatsapp_business_account_id = "test_business_account_id"
        mock_request.return_value = mock_response
        result = await whatsapp_client.list_templates()

    # Assert
    assert len(result) == 2
    assert result[0]["name"] == "order_confirmation"
    assert result[0]["status"] == "APPROVED"
    assert result[1]["name"] == "appointment_reminder"
    assert result[1]["status"] == "PENDING"


@pytest.mark.asyncio
async def test_send_text_message_failure(whatsapp_client):
    """Test error handling when sending text message fails."""
    # Arrange
    to = "+14155552671"
    text = "Test message"

    # Act & Assert
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("API Error: Invalid phone number")

        with pytest.raises(Exception) as exc_info:
            await whatsapp_client.send_text_message(to, text)

        assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_upload_media_failure(whatsapp_client):
    """Test error handling when media upload fails."""
    # Arrange
    file_data = b"fake data"
    mime_type = "image/jpeg"
    filename = "test.jpg"

    # Act & Assert
    with patch.object(whatsapp_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("File too large")

        with pytest.raises(Exception) as exc_info:
            await whatsapp_client.upload_media(file_data, mime_type, filename)

        assert "Failed to upload media" in str(exc_info.value)

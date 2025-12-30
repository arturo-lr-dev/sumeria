"""
Unit tests for WhatsApp schemas and mappers.
"""
import pytest
from datetime import datetime

from app.infrastructure.connectors.whatsapp.schemas import (
    WhatsAppMessageMapper,
    WhatsAppTemplateMapper
)
from app.domain.entities.whatsapp_message import (
    WhatsAppMessageDraft,
    WhatsAppMedia,
    WhatsAppMessage
)
from tests.fixtures.whatsapp_fixtures import (
    SAMPLE_WEBHOOK_TEXT_MESSAGE,
    SAMPLE_WEBHOOK_IMAGE_MESSAGE,
    SAMPLE_WEBHOOK_STATUS_UPDATE,
    SAMPLE_TEMPLATES_RESPONSE,
    create_sample_message_draft,
    create_sample_media
)


class TestWhatsAppMessageMapper:
    """Tests for WhatsAppMessageMapper."""

    def test_from_message_draft_text(self):
        """Test converting text message draft to API format."""
        # Arrange
        draft = WhatsAppMessageDraft(
            to="+14155552671",
            message_type="text",
            text_content="Hello, this is a test message"
        )

        # Act
        result = WhatsAppMessageMapper.from_message_draft(draft)

        # Assert
        assert result["messaging_product"] == "whatsapp"
        assert result["recipient_type"] == "individual"
        assert result["to"] == "14155552671"  # + prefix is stripped
        assert result["type"] == "text"
        assert result["text"]["body"] == "Hello, this is a test message"

    def test_from_message_draft_image_with_url(self):
        """Test converting image message draft with URL to API format."""
        # Arrange
        media = WhatsAppMedia(
            media_type="image",
            media_url="https://example.com/image.jpg",
            caption="Test image"
        )
        draft = WhatsAppMessageDraft(
            to="+14155552671",
            message_type="image",
            media=media
        )

        # Act
        result = WhatsAppMessageMapper.from_message_draft(draft)

        # Assert
        assert result["type"] == "image"
        assert result["image"]["link"] == "https://example.com/image.jpg"
        assert result["image"]["caption"] == "Test image"

    def test_from_message_draft_image_with_id(self):
        """Test converting image message draft with media ID to API format."""
        # Arrange
        media = WhatsAppMedia(
            media_type="image",
            media_id="1234567890",
            caption="Test caption"
        )
        draft = WhatsAppMessageDraft(
            to="+14155552671",
            message_type="image",
            media=media
        )

        # Act
        result = WhatsAppMessageMapper.from_message_draft(draft)

        # Assert
        assert result["type"] == "image"
        assert result["image"]["id"] == "1234567890"
        assert result["image"]["caption"] == "Test caption"

    def test_from_message_draft_document(self):
        """Test converting document message draft to API format."""
        # Arrange
        media = WhatsAppMedia(
            media_type="document",
            media_id="doc123",
            filename="report.pdf",
            caption="Monthly report"
        )
        draft = WhatsAppMessageDraft(
            to="+14155552671",
            message_type="document",
            media=media
        )

        # Act
        result = WhatsAppMessageMapper.from_message_draft(draft)

        # Assert
        assert result["type"] == "document"
        assert result["document"]["id"] == "doc123"
        assert result["document"]["filename"] == "report.pdf"
        assert result["document"]["caption"] == "Monthly report"

    def test_from_message_draft_template(self):
        """Test converting template message draft to API format."""
        # Arrange
        draft = WhatsAppMessageDraft(
            to="+14155552671",
            message_type="template",
            template_name="order_confirmation"
        )

        # Act
        result = WhatsAppMessageMapper.from_message_draft(draft)

        # Assert
        assert result["type"] == "template"
        assert result["template"]["name"] == "order_confirmation"

    def test_to_message_entity_text(self):
        """Test converting webhook text message to domain entity."""
        # Arrange
        webhook_data = SAMPLE_WEBHOOK_TEXT_MESSAGE["entry"][0]["changes"][0]["value"]["messages"][0]

        # Act
        result = WhatsAppMessageMapper.to_message_entity(webhook_data)

        # Assert
        assert isinstance(result, WhatsAppMessage)
        assert result.id == "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA"
        assert result.from_number == "+14155552671"  # + prefix is added
        assert result.message_type == "text"
        assert result.text_content == "Hello, I need help with my order"
        assert result.media is None

    def test_to_message_entity_image(self):
        """Test converting webhook image message to domain entity."""
        # Arrange
        webhook_data = SAMPLE_WEBHOOK_IMAGE_MESSAGE["entry"][0]["changes"][0]["value"]["messages"][0]

        # Act
        result = WhatsAppMessageMapper.to_message_entity(webhook_data)

        # Assert
        assert isinstance(result, WhatsAppMessage)
        assert result.id == "wamid.IMAGE123456"
        assert result.from_number == "+14155552672"  # + prefix is added
        assert result.message_type == "image"
        assert result.media is not None
        assert result.media.media_type == "image"
        assert result.media.media_id == "1234567890123456"
        assert result.media.caption == "Here's a photo of the issue"

    def test_parse_webhook_payload_text_message(self):
        """Test parsing webhook payload with text messages."""
        # Arrange
        payload = SAMPLE_WEBHOOK_TEXT_MESSAGE

        # Act
        result = WhatsAppMessageMapper.parse_webhook_payload(payload)

        # Assert
        assert len(result) == 1
        assert result[0].message_type == "text"
        assert result[0].text_content == "Hello, I need help with my order"

    def test_parse_webhook_payload_image_message(self):
        """Test parsing webhook payload with image message."""
        # Arrange
        payload = SAMPLE_WEBHOOK_IMAGE_MESSAGE

        # Act
        result = WhatsAppMessageMapper.parse_webhook_payload(payload)

        # Assert
        assert len(result) == 1
        assert result[0].message_type == "image"
        assert result[0].media.caption == "Here's a photo of the issue"

    def test_parse_webhook_payload_empty(self):
        """Test parsing webhook payload with no messages."""
        # Arrange
        payload = {
            "object": "whatsapp_business_account",
            "entry": []
        }

        # Act
        result = WhatsAppMessageMapper.parse_webhook_payload(payload)

        # Assert
        assert len(result) == 0

    def test_parse_status_update(self):
        """Test parsing status update from webhook."""
        # Arrange
        payload = SAMPLE_WEBHOOK_STATUS_UPDATE

        # Act
        result = WhatsAppMessageMapper.parse_status_update(payload)

        # Assert
        assert len(result) == 2
        assert result[0]["message_id"] == "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA"
        assert result[0]["status"] == "delivered"
        assert result[1]["status"] == "read"

    def test_parse_status_update_empty(self):
        """Test parsing status update with no statuses."""
        # Arrange
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {}
                }]
            }]
        }

        # Act
        result = WhatsAppMessageMapper.parse_status_update(payload)

        # Assert
        assert len(result) == 0


class TestWhatsAppTemplateMapper:
    """Tests for WhatsAppTemplateMapper."""

    def test_to_template_entity_complete(self):
        """Test converting complete template API data to domain entity."""
        # Arrange
        api_data = SAMPLE_TEMPLATES_RESPONSE["data"][0]

        # Act
        result = WhatsAppTemplateMapper.to_template_entity(api_data)

        # Assert
        assert result.id == "template_001"
        assert result.name == "order_confirmation"
        assert result.language == "en_US"
        assert result.status == "APPROVED"
        assert result.category == "UTILITY"
        assert len(result.components) == 3
        assert result.components[0].type == "HEADER"
        assert result.components[0].text == "Order Confirmed!"
        assert result.components[1].type == "BODY"
        assert result.components[2].type == "FOOTER"

    def test_to_template_entity_pending(self):
        """Test converting pending template to domain entity."""
        # Arrange
        api_data = SAMPLE_TEMPLATES_RESPONSE["data"][1]

        # Act
        result = WhatsAppTemplateMapper.to_template_entity(api_data)

        # Assert
        assert result.id == "template_002"
        assert result.name == "appointment_reminder"
        assert result.status == "PENDING"
        assert len(result.components) == 1
        assert result.components[0].type == "BODY"

    def test_to_template_entity_minimal(self):
        """Test converting template with minimal data."""
        # Arrange
        api_data = {
            "id": "template_003",
            "name": "simple_greeting",
            "language": "en",
            "status": "APPROVED",
            "category": "UTILITY"
        }

        # Act
        result = WhatsAppTemplateMapper.to_template_entity(api_data)

        # Assert
        assert result.id == "template_003"
        assert result.name == "simple_greeting"
        assert result.status == "APPROVED"
        assert len(result.components) == 0

    def test_to_template_entity_with_parameters(self):
        """Test template component parameter extraction."""
        # Arrange
        api_data = {
            "id": "template_004",
            "name": "welcome_message",
            "language": "en_US",
            "status": "APPROVED",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Welcome {{1}}! Your account {{2}} is ready."
                }
            ]
        }

        # Act
        result = WhatsAppTemplateMapper.to_template_entity(api_data)

        # Assert
        assert len(result.components) == 1
        assert result.components[0].type == "BODY"
        assert result.components[0].text == "Welcome {{1}}! Your account {{2}} is ready."
        # Note: Parameters are extracted when template is used, not when parsed

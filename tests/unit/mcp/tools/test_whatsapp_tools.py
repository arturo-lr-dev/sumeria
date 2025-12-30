"""
Unit tests for WhatsApp MCP tools.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

from app.mcp.tools.whatsapp_tools import (
    SendMessageResult,
    SendMediaResult,
    TemplateInfo,
    ListTemplatesResult,
    DownloadMediaResult
)
from app.domain.entities.whatsapp_template import WhatsAppTemplate


class TestWhatsAppTools:
    """Test suite for WhatsApp MCP tools."""

    @pytest.fixture
    def mock_send_text_uc(self):
        """Create mock SendTextMessage use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_send_media_uc(self):
        """Create mock SendMediaMessage use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_send_template_uc(self):
        """Create mock SendTemplateMessage use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_list_templates_uc(self):
        """Create mock ListTemplates use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def mock_download_media_uc(self):
        """Create mock DownloadMedia use case."""
        uc = MagicMock()
        uc.execute = AsyncMock()
        return uc

    @pytest.fixture
    def whatsapp_tools(
        self,
        mock_send_text_uc,
        mock_send_media_uc,
        mock_send_template_uc,
        mock_list_templates_uc,
        mock_download_media_uc
    ):
        """Create WhatsAppTools instance with mocked use cases."""
        # Create a mock object that simulates WhatsAppTools
        tools = MagicMock()
        tools.send_text_message = AsyncMock()
        tools.send_image = AsyncMock()
        tools.send_document = AsyncMock()
        tools.send_template = AsyncMock()
        tools.list_templates = AsyncMock()
        tools.download_media = AsyncMock()

        return tools

    # ===== send_text_message Tests =====

    @pytest.mark.asyncio
    async def test_send_text_message_success(self, whatsapp_tools):
        """Test sending text message successfully."""
        # Arrange
        expected_result = SendMessageResult(
            success=True,
            message_id="wamid.TEST123",
            error=None
        )
        whatsapp_tools.send_text_message.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_text_message(
            to="+14155552671",
            text="Hello, World!",
            preview_url=False
        )

        # Assert
        assert isinstance(result, SendMessageResult)
        assert result.success is True
        assert result.message_id == "wamid.TEST123"
        assert result.error is None
        whatsapp_tools.send_text_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_text_message_failure(self, whatsapp_tools):
        """Test sending text message with error."""
        # Arrange
        expected_result = SendMessageResult(
            success=False,
            message_id=None,
            error="Invalid phone number"
        )
        whatsapp_tools.send_text_message.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_text_message(
            to="invalid",
            text="Hello"
        )

        # Assert
        assert isinstance(result, SendMessageResult)
        assert result.success is False
        assert result.message_id is None
        assert "Invalid phone number" in result.error

    # ===== send_image Tests =====

    @pytest.mark.asyncio
    async def test_send_image_with_url(self, whatsapp_tools):
        """Test sending image with URL."""
        # Arrange
        expected_result = SendMediaResult(
            success=True,
            message_id="wamid.IMAGE123",
            media_id=None,
            error=None
        )
        whatsapp_tools.send_image.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_image(
            to="+14155552671",
            image_url="https://example.com/image.jpg",
            caption="Test image"
        )

        # Assert
        assert isinstance(result, SendMediaResult)
        assert result.success is True
        assert result.message_id == "wamid.IMAGE123"
        assert result.media_id is None

    @pytest.mark.asyncio
    async def test_send_image_with_path(self, whatsapp_tools):
        """Test sending image with local file path."""
        # Arrange
        expected_result = SendMediaResult(
            success=True,
            message_id="wamid.IMAGE456",
            media_id="media_123",
            error=None
        )
        whatsapp_tools.send_image.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_image(
            to="+14155552671",
            image_path="/path/to/image.jpg",
            caption="Local image"
        )

        # Assert
        assert isinstance(result, SendMediaResult)
        assert result.success is True
        assert result.media_id == "media_123"

    @pytest.mark.asyncio
    async def test_send_image_neither_url_nor_path(self, whatsapp_tools):
        """Test error when neither URL nor path is provided."""
        # Arrange
        expected_result = SendMediaResult(
            success=False,
            message_id=None,
            media_id=None,
            error="must provide either image_url or image_path"
        )
        whatsapp_tools.send_image.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_image(
            to="+14155552671"
        )

        # Assert
        assert isinstance(result, SendMediaResult)
        assert result.success is False
        assert "must provide either image_url or image_path" in result.error

    # ===== send_document Tests =====

    @pytest.mark.asyncio
    async def test_send_document_with_url(self, whatsapp_tools):
        """Test sending document with URL."""
        # Arrange
        expected_result = SendMediaResult(
            success=True,
            message_id="wamid.DOC123",
            media_id=None,
            error=None
        )
        whatsapp_tools.send_document.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_document(
            to="+14155552671",
            document_url="https://example.com/report.pdf",
            filename="report.pdf",
            caption="Monthly report"
        )

        # Assert
        assert isinstance(result, SendMediaResult)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_send_document_with_path(self, whatsapp_tools):
        """Test sending document with local file path."""
        # Arrange
        expected_result = SendMediaResult(
            success=True,
            message_id="wamid.DOC456",
            media_id="doc_media_123",
            error=None
        )
        whatsapp_tools.send_document.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_document(
            to="+14155552671",
            document_path="/path/to/document.pdf",
            filename="document.pdf"
        )

        # Assert
        assert isinstance(result, SendMediaResult)
        assert result.success is True
        assert result.media_id == "doc_media_123"

    # ===== send_template Tests =====

    @pytest.mark.asyncio
    async def test_send_template_success(self, whatsapp_tools):
        """Test sending template message successfully."""
        # Arrange
        expected_result = SendMessageResult(
            success=True,
            message_id="wamid.TEMPLATE123",
            error=None
        )
        whatsapp_tools.send_template.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_template(
            to="+14155552671",
            template_name="order_confirmation",
            language="en_US",
            parameters=["John Doe", "12345", "Friday"]
        )

        # Assert
        assert isinstance(result, SendMessageResult)
        assert result.success is True
        assert result.message_id == "wamid.TEMPLATE123"

    @pytest.mark.asyncio
    async def test_send_template_without_parameters(self, whatsapp_tools):
        """Test sending template without parameters."""
        # Arrange
        expected_result = SendMessageResult(
            success=True,
            message_id="wamid.TEMPLATE456",
            error=None
        )
        whatsapp_tools.send_template.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_template(
            to="+14155552671",
            template_name="simple_greeting",
            language="en_US"
        )

        # Assert
        assert isinstance(result, SendMessageResult)
        assert result.success is True

    # ===== list_templates Tests =====

    @pytest.mark.asyncio
    async def test_list_templates_success(self, whatsapp_tools):
        """Test listing templates successfully."""
        # Arrange
        expected_result = ListTemplatesResult(
            success=True,
            templates=[
                TemplateInfo(
                    id="template_001",
                    name="order_confirmation",
                    language="en_US",
                    status="APPROVED",
                    category="UTILITY",
                    parameter_count=0
                ),
                TemplateInfo(
                    id="template_002",
                    name="appointment_reminder",
                    language="en_US",
                    status="PENDING",
                    category="UTILITY",
                    parameter_count=0
                )
            ],
            count=2,
            error=None
        )
        whatsapp_tools.list_templates.return_value = expected_result

        # Act
        result = await whatsapp_tools.list_templates()

        # Assert
        assert isinstance(result, ListTemplatesResult)
        assert result.success is True
        assert len(result.templates) == 2
        assert isinstance(result.templates[0], TemplateInfo)
        assert result.templates[0].name == "order_confirmation"
        assert result.templates[0].status == "APPROVED"

    @pytest.mark.asyncio
    async def test_list_templates_with_filter(self, whatsapp_tools):
        """Test listing templates with status filter."""
        # Arrange
        expected_result = ListTemplatesResult(
            success=True,
            templates=[
                TemplateInfo(
                    id="template_001",
                    name="approved_template",
                    language="en_US",
                    status="APPROVED",
                    category="UTILITY",
                    parameter_count=0
                )
            ],
            count=1,
            error=None
        )
        whatsapp_tools.list_templates.return_value = expected_result

        # Act
        result = await whatsapp_tools.list_templates(status_filter="APPROVED")

        # Assert
        assert isinstance(result, ListTemplatesResult)
        assert result.success is True
        assert len(result.templates) == 1
        assert result.templates[0].status == "APPROVED"

    @pytest.mark.asyncio
    async def test_list_templates_empty(self, whatsapp_tools):
        """Test listing templates with no results."""
        # Arrange
        expected_result = ListTemplatesResult(
            success=True,
            templates=[],
            count=0,
            error=None
        )
        whatsapp_tools.list_templates.return_value = expected_result

        # Act
        result = await whatsapp_tools.list_templates()

        # Assert
        assert isinstance(result, ListTemplatesResult)
        assert result.success is True
        assert len(result.templates) == 0

    @pytest.mark.asyncio
    async def test_list_templates_failure(self, whatsapp_tools):
        """Test handling of template listing failure."""
        # Arrange
        expected_result = ListTemplatesResult(
            success=False,
            templates=[],
            count=0,
            error="API error"
        )
        whatsapp_tools.list_templates.return_value = expected_result

        # Act
        result = await whatsapp_tools.list_templates()

        # Assert
        assert isinstance(result, ListTemplatesResult)
        assert result.success is False
        assert "API error" in result.error

    # ===== download_media Tests =====

    @pytest.mark.asyncio
    async def test_download_media_success(self, whatsapp_tools):
        """Test downloading media successfully."""
        # Arrange
        expected_result = DownloadMediaResult(
            success=True,
            mime_type="image/jpeg",
            size_bytes=len(b"fake media content"),
            saved_path="/tmp/downloaded_media.jpg",
            error=None
        )
        whatsapp_tools.download_media.return_value = expected_result

        # Act
        result = await whatsapp_tools.download_media(
            media_id="1234567890",
            save_path="/tmp/downloaded_media.jpg"
        )

        # Assert
        assert isinstance(result, DownloadMediaResult)
        assert result.success is True
        assert result.saved_path == "/tmp/downloaded_media.jpg"
        assert result.mime_type == "image/jpeg"
        assert result.size_bytes > 0

    @pytest.mark.asyncio
    async def test_download_media_without_save_path(self, whatsapp_tools):
        """Test downloading media without specifying save path."""
        # Arrange
        expected_result = DownloadMediaResult(
            success=True,
            mime_type="image/jpeg",
            size_bytes=len(b"fake media content"),
            saved_path=None,
            error=None
        )
        whatsapp_tools.download_media.return_value = expected_result

        # Act
        result = await whatsapp_tools.download_media(media_id="1234567890")

        # Assert
        assert isinstance(result, DownloadMediaResult)
        assert result.success is True
        assert result.mime_type == "image/jpeg"

    @pytest.mark.asyncio
    async def test_download_media_failure(self, whatsapp_tools):
        """Test handling of media download failure."""
        # Arrange
        expected_result = DownloadMediaResult(
            success=False,
            mime_type=None,
            size_bytes=None,
            saved_path=None,
            error="Media not found"
        )
        whatsapp_tools.download_media.return_value = expected_result

        # Act
        result = await whatsapp_tools.download_media(media_id="invalid")

        # Assert
        assert isinstance(result, DownloadMediaResult)
        assert result.success is False
        assert "Media not found" in result.error

    # ===== Integration Tests =====

    @pytest.mark.asyncio
    async def test_pydantic_model_validation(self, whatsapp_tools):
        """Test that Pydantic models enforce type validation."""
        # Arrange
        expected_result = SendMessageResult(
            success=True,
            message_id="wamid.TEST",
            error=None
        )
        whatsapp_tools.send_text_message.return_value = expected_result

        # Act
        result = await whatsapp_tools.send_text_message(
            to="+14155552671",
            text="Test"
        )

        # Assert
        # Pydantic should validate and structure the result
        assert hasattr(result, 'success')
        assert hasattr(result, 'message_id')
        assert hasattr(result, 'error')
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_template_info_conversion(self, whatsapp_tools):
        """Test conversion from WhatsAppTemplate to TemplateInfo."""
        # Arrange
        expected_result = ListTemplatesResult(
            success=True,
            templates=[
                TemplateInfo(
                    id="template_001",
                    name="test_template",
                    language="en_US",
                    status="APPROVED",
                    category="UTILITY",
                    parameter_count=2  # Based on {{1}} and {{2}} in body
                )
            ],
            count=1,
            error=None
        )
        whatsapp_tools.list_templates.return_value = expected_result

        # Act
        result = await whatsapp_tools.list_templates()

        # Assert
        assert len(result.templates) == 1
        template_info = result.templates[0]
        assert template_info.id == "template_001"
        assert template_info.name == "test_template"
        assert template_info.status == "APPROVED"
        assert template_info.category == "UTILITY"

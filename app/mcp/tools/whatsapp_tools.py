"""
WhatsApp MCP tools.
Provides MCP tool wrappers for WhatsApp Business operations.
"""
from typing import Optional
from pydantic import BaseModel, Field
from pathlib import Path

from app.application.use_cases.whatsapp.send_text_message import (
    SendTextMessageUseCase,
    SendTextMessageRequest
)
from app.application.use_cases.whatsapp.send_media_message import (
    SendMediaMessageUseCase,
    SendMediaMessageRequest
)
from app.application.use_cases.whatsapp.send_template_message import (
    SendTemplateMessageUseCase,
    SendTemplateMessageRequest
)
from app.application.use_cases.whatsapp.list_templates import (
    ListTemplatesUseCase,
    ListTemplatesRequest
)
from app.application.use_cases.whatsapp.download_media import (
    DownloadMediaUseCase,
    DownloadMediaRequest
)


# ============ Pydantic Models for Structured Output ============

class SendMessageResult(BaseModel):
    """Result of sending a WhatsApp message."""
    success: bool = Field(description="Whether the message was sent successfully")
    message_id: Optional[str] = Field(default=None, description="WhatsApp message ID (wamid)")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class SendMediaResult(BaseModel):
    """Result of sending a WhatsApp media message."""
    success: bool = Field(description="Whether the media was sent successfully")
    message_id: Optional[str] = Field(default=None, description="WhatsApp message ID")
    media_id: Optional[str] = Field(default=None, description="WhatsApp media ID if uploaded")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class TemplateInfo(BaseModel):
    """Information about a WhatsApp message template."""
    id: str = Field(description="Template ID")
    name: str = Field(description="Template name")
    language: str = Field(description="Language code (e.g., en_US)")
    status: str = Field(description="Template status (APPROVED, PENDING, REJECTED)")
    category: str = Field(description="Template category (MARKETING, UTILITY, AUTHENTICATION)")
    parameter_count: int = Field(description="Number of parameters required")


class ListTemplatesResult(BaseModel):
    """Result of listing WhatsApp templates."""
    success: bool = Field(description="Whether the request was successful")
    templates: list[TemplateInfo] = Field(default_factory=list, description="List of templates")
    count: int = Field(description="Number of templates returned")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class DownloadMediaResult(BaseModel):
    """Result of downloading WhatsApp media."""
    success: bool = Field(description="Whether the download was successful")
    mime_type: Optional[str] = Field(default=None, description="MIME type of the media")
    size_bytes: Optional[int] = Field(default=None, description="Size of the media file")
    saved_path: Optional[str] = Field(default=None, description="Path where file was saved")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# ============ WhatsApp Tools Class ============

class WhatsAppTools:
    """
    Collection of WhatsApp MCP tools.

    Provides tools for:
    - Sending text messages
    - Sending media (images, documents, videos, audio)
    - Sending template messages
    - Listing message templates
    - Downloading media from incoming messages
    """

    def __init__(self):
        """Initialize all use cases."""
        self.send_text_uc = SendTextMessageUseCase()
        self.send_media_uc = SendMediaMessageUseCase()
        self.send_template_uc = SendTemplateMessageUseCase()
        self.list_templates_uc = ListTemplatesUseCase()
        self.download_media_uc = DownloadMediaUseCase()

    async def send_text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> SendMessageResult:
        """
        Send a WhatsApp text message.

        Args:
            to: Recipient phone number (E.164 format: +1234567890)
            text: Message text (max 4096 characters)
            preview_url: Enable URL preview for links

        Returns:
            SendMessageResult with success status and message ID
        """
        request = SendTextMessageRequest(
            to=to,
            text=text,
            preview_url=preview_url
        )

        response = await self.send_text_uc.execute(request)

        return SendMessageResult(
            success=response.success,
            message_id=response.message_id,
            error=response.error
        )

    async def send_image(
        self,
        to: str,
        image_url: Optional[str] = None,
        image_path: Optional[str] = None,
        caption: Optional[str] = None
    ) -> SendMediaResult:
        """
        Send an image via WhatsApp.

        Provide EITHER image_url OR image_path (not both).

        Args:
            to: Recipient phone number (E.164 format)
            image_url: URL of image to send
            image_path: Local file path to image
            caption: Optional caption (max 1024 characters)

        Returns:
            SendMediaResult with success status and message/media IDs
        """
        # Read file if path provided
        media_data = None
        mime_type = None
        filename = None

        if image_path:
            try:
                file = Path(image_path)
                if not file.exists():
                    return SendMediaResult(
                        success=False,
                        error=f"Image file not found: {image_path}"
                    )

                media_data = file.read_bytes()
                filename = file.name

                # Determine MIME type
                ext = file.suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png'
                }.get(ext, 'image/jpeg')

            except Exception as e:
                return SendMediaResult(
                    success=False,
                    error=f"Failed to read image file: {e}"
                )

        request = SendMediaMessageRequest(
            to=to,
            media_type='image',
            media_data=media_data,
            media_url=image_url,
            mime_type=mime_type,
            filename=filename,
            caption=caption
        )

        response = await self.send_media_uc.execute(request)

        return SendMediaResult(
            success=response.success,
            message_id=response.message_id,
            media_id=response.media_id,
            error=response.error
        )

    async def send_document(
        self,
        to: str,
        document_url: Optional[str] = None,
        document_path: Optional[str] = None,
        filename: Optional[str] = None,
        caption: Optional[str] = None
    ) -> SendMediaResult:
        """
        Send a document via WhatsApp.

        Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, etc.
        Provide EITHER document_url OR document_path.

        Args:
            to: Recipient phone number (E.164 format)
            document_url: URL of document to send
            document_path: Local file path to document
            filename: Display filename (if not using document_path)
            caption: Optional caption (max 1024 characters)

        Returns:
            SendMediaResult with success status and message/media IDs
        """
        # Read file if path provided
        media_data = None
        mime_type = None

        if document_path:
            try:
                file = Path(document_path)
                if not file.exists():
                    return SendMediaResult(
                        success=False,
                        error=f"Document file not found: {document_path}"
                    )

                media_data = file.read_bytes()
                filename = filename or file.name

                # Determine MIME type
                ext = file.suffix.lower()
                mime_type = {
                    '.pdf': 'application/pdf',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.xls': 'application/vnd.ms-excel',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.ppt': 'application/vnd.ms-powerpoint',
                    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    '.txt': 'text/plain'
                }.get(ext, 'application/octet-stream')

            except Exception as e:
                return SendMediaResult(
                    success=False,
                    error=f"Failed to read document file: {e}"
                )

        request = SendMediaMessageRequest(
            to=to,
            media_type='document',
            media_data=media_data,
            media_url=document_url,
            mime_type=mime_type,
            filename=filename,
            caption=caption
        )

        response = await self.send_media_uc.execute(request)

        return SendMediaResult(
            success=response.success,
            message_id=response.message_id,
            media_id=response.media_id,
            error=response.error
        )

    async def send_template(
        self,
        to: str,
        template_name: str,
        language: str = "en_US",
        parameters: Optional[list[str]] = None
    ) -> SendMessageResult:
        """
        Send a pre-approved WhatsApp template message.

        Templates must be approved by Meta before use.
        Use list_templates() to see available templates.

        Args:
            to: Recipient phone number (E.164 format)
            template_name: Name of approved template
            language: Language code (e.g., "en_US", "es_ES", "pt_BR")
            parameters: Template parameters (e.g., ["John", "123"])

        Returns:
            SendMessageResult with success status and message ID
        """
        request = SendTemplateMessageRequest(
            to=to,
            template_name=template_name,
            language=language,
            parameters=parameters or []
        )

        response = await self.send_template_uc.execute(request)

        return SendMessageResult(
            success=response.success,
            message_id=response.message_id,
            error=response.error
        )

    async def list_templates(
        self,
        status_filter: Optional[str] = None
    ) -> ListTemplatesResult:
        """
        List all WhatsApp message templates.

        Args:
            status_filter: Filter by status (APPROVED, PENDING, REJECTED)

        Returns:
            ListTemplatesResult with all templates
        """
        request = ListTemplatesRequest(status_filter=status_filter)
        response = await self.list_templates_uc.execute(request)

        if not response.success:
            return ListTemplatesResult(
                success=False,
                count=0,
                error=response.error
            )

        # Convert to TemplateInfo models
        templates_info = [
            TemplateInfo(
                id=t.id,
                name=t.name,
                language=t.language,
                status=t.status,
                category=t.category,
                parameter_count=t.get_parameter_count()
            )
            for t in response.templates
        ]

        return ListTemplatesResult(
            success=True,
            templates=templates_info,
            count=response.count
        )

    async def download_media(
        self,
        media_id: str,
        save_path: Optional[str] = None
    ) -> DownloadMediaResult:
        """
        Download media from a WhatsApp message.

        Media ID is provided in incoming webhook messages.

        Args:
            media_id: WhatsApp media ID
            save_path: Optional path to save file

        Returns:
            DownloadMediaResult with download info
        """
        request = DownloadMediaRequest(
            media_id=media_id,
            save_path=save_path
        )

        response = await self.download_media_uc.execute(request)

        return DownloadMediaResult(
            success=response.success,
            mime_type=response.mime_type,
            size_bytes=response.size_bytes,
            saved_path=response.saved_path,
            error=response.error
        )


# Global instance (lazy initialization to avoid import-time errors)
_whatsapp_tools_instance = None


def get_whatsapp_tools() -> WhatsAppTools:
    """Get or create the global WhatsAppTools instance."""
    global _whatsapp_tools_instance
    if _whatsapp_tools_instance is None:
        _whatsapp_tools_instance = WhatsAppTools()
    return _whatsapp_tools_instance


# For backwards compatibility
whatsapp_tools = get_whatsapp_tools

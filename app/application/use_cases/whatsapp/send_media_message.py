"""
Send WhatsApp media message use case.
Handles sending images, videos, documents, and audio via WhatsApp.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.whatsapp.client import WhatsAppClient
from app.domain.entities.whatsapp_message import WhatsAppMedia


@dataclass
class SendMediaMessageRequest:
    """
    Request to send a WhatsApp media message.

    Attributes:
        to: Recipient phone number (E.164 format)
        media_type: Type of media (image, video, document, audio)
        media_data: Binary file data for upload (optional)
        media_url: Public URL to media file (optional, alternative to data)
        media_id: WhatsApp media ID if already uploaded (optional)
        mime_type: MIME type of the media
        filename: Original filename (required for documents)
        caption: Optional caption (max 1024 characters)
    """
    to: str
    media_type: str
    media_data: Optional[bytes] = None
    media_url: Optional[str] = None
    media_id: Optional[str] = None
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    caption: Optional[str] = None


@dataclass
class SendMediaMessageResponse:
    """
    Response after sending media message.

    Attributes:
        success: Whether the message was sent successfully
        message_id: WhatsApp message ID if successful
        media_id: WhatsApp media ID if media was uploaded
        error: Error message if failed
    """
    success: bool
    message_id: Optional[str] = None
    media_id: Optional[str] = None
    error: Optional[str] = None


class SendMediaMessageUseCase:
    """
    Use case for sending WhatsApp media messages.

    Handles uploading media if needed and sending media messages.
    """

    def __init__(self, client: Optional[WhatsAppClient] = None):
        """
        Initialize use case.

        Args:
            client: WhatsAppClient instance (creates new if not provided)
        """
        self.client = client or WhatsAppClient()

    async def execute(
        self,
        request: SendMediaMessageRequest
    ) -> SendMediaMessageResponse:
        """
        Execute the use case to send a media message.

        Args:
            request: Send media message request

        Returns:
            Response with message ID and media ID or error
        """
        try:
            # Validate media type
            valid_types = ['image', 'video', 'document', 'audio', 'sticker']
            if request.media_type not in valid_types:
                return SendMediaMessageResponse(
                    success=False,
                    error=f"Invalid media_type. Must be one of: {valid_types}"
                )

            # Validate phone number
            if not request.to.startswith('+'):
                return SendMediaMessageResponse(
                    success=False,
                    error=f"Phone number must be in E.164 format: {request.to}"
                )

            # Validate caption length
            if request.caption and len(request.caption) > 1024:
                return SendMediaMessageResponse(
                    success=False,
                    error="Media caption cannot exceed 1024 characters"
                )

            # Determine media source
            media_id = request.media_id
            upload_media_id = None

            # If media_data is provided, upload it first
            if request.media_data:
                if not request.mime_type or not request.filename:
                    return SendMediaMessageResponse(
                        success=False,
                        error="mime_type and filename are required when uploading media"
                    )

                media_id = await self.client.upload_media(
                    file_data=request.media_data,
                    mime_type=request.mime_type,
                    filename=request.filename
                )
                upload_media_id = media_id

            # Create media object
            media = WhatsAppMedia(
                media_type=request.media_type,
                media_id=media_id,
                media_url=request.media_url,
                mime_type=request.mime_type,
                filename=request.filename,
                caption=request.caption
            )

            # Send media message
            message_id = await self.client.send_media_message(
                to=request.to,
                media=media
            )

            return SendMediaMessageResponse(
                success=True,
                message_id=message_id,
                media_id=upload_media_id
            )

        except Exception as e:
            return SendMediaMessageResponse(
                success=False,
                error=str(e)
            )

"""
Send WhatsApp text message use case.
Handles sending text messages via WhatsApp Business Cloud API.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.whatsapp.client import WhatsAppClient


@dataclass
class SendTextMessageRequest:
    """
    Request to send a WhatsApp text message.

    Attributes:
        to: Recipient phone number (E.164 format: +1234567890)
        text: Message text (max 4096 characters)
        preview_url: Enable URL preview for links in message
        reply_to_message_id: Optional message ID to reply to
    """
    to: str
    text: str
    preview_url: bool = False
    reply_to_message_id: Optional[str] = None


@dataclass
class SendTextMessageResponse:
    """
    Response after sending text message.

    Attributes:
        success: Whether the message was sent successfully
        message_id: WhatsApp message ID (wamid) if successful
        error: Error message if failed
    """
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class SendTextMessageUseCase:
    """
    Use case for sending WhatsApp text messages.

    Validates input, sends message via WhatsApp API, and returns result.
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
        request: SendTextMessageRequest
    ) -> SendTextMessageResponse:
        """
        Execute the use case to send a text message.

        Args:
            request: Send text message request

        Returns:
            Response with message ID or error
        """
        try:
            # Validate text length
            if len(request.text) > 4096:
                return SendTextMessageResponse(
                    success=False,
                    error="Text message cannot exceed 4096 characters"
                )

            # Validate phone number format
            if not request.to.startswith('+'):
                return SendTextMessageResponse(
                    success=False,
                    error=f"Phone number must be in E.164 format (start with +): {request.to}"
                )

            # Send message
            message_id = await self.client.send_text_message(
                to=request.to,
                text=request.text,
                preview_url=request.preview_url
            )

            return SendTextMessageResponse(
                success=True,
                message_id=message_id
            )

        except Exception as e:
            return SendTextMessageResponse(
                success=False,
                error=str(e)
            )

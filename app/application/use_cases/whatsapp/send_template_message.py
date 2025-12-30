"""
Send WhatsApp template message use case.
Handles sending pre-approved template messages via WhatsApp.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.whatsapp.client import WhatsAppClient


@dataclass
class SendTemplateMessageRequest:
    """
    Request to send a WhatsApp template message.

    Attributes:
        to: Recipient phone number (E.164 format)
        template_name: Name of the approved template
        language: Language code (e.g., "en_US", "es_ES", "pt_BR")
        parameters: Template parameter values (e.g., ["John", "123"])
    """
    to: str
    template_name: str
    language: str = "en_US"
    parameters: list[str] = None

    def __post_init__(self):
        """Initialize default parameters."""
        if self.parameters is None:
            self.parameters = []


@dataclass
class SendTemplateMessageResponse:
    """
    Response after sending template message.

    Attributes:
        success: Whether the message was sent successfully
        message_id: WhatsApp message ID if successful
        error: Error message if failed
    """
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class SendTemplateMessageUseCase:
    """
    Use case for sending WhatsApp template messages.

    Templates must be pre-approved by Meta before they can be used.
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
        request: SendTemplateMessageRequest
    ) -> SendTemplateMessageResponse:
        """
        Execute the use case to send a template message.

        Args:
            request: Send template message request

        Returns:
            Response with message ID or error
        """
        try:
            # Validate phone number
            if not request.to.startswith('+'):
                return SendTemplateMessageResponse(
                    success=False,
                    error=f"Phone number must be in E.164 format: {request.to}"
                )

            # Validate template name
            if not request.template_name:
                return SendTemplateMessageResponse(
                    success=False,
                    error="template_name is required"
                )

            # Send template message
            message_id = await self.client.send_template_message(
                to=request.to,
                template_name=request.template_name,
                language=request.language,
                parameters=request.parameters
            )

            return SendTemplateMessageResponse(
                success=True,
                message_id=message_id
            )

        except Exception as e:
            return SendTemplateMessageResponse(
                success=False,
                error=str(e)
            )

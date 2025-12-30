"""
Process WhatsApp webhook message use case.
Handles incoming webhook payloads from WhatsApp.
"""
from dataclasses import dataclass, field
from typing import Optional, Any

from app.infrastructure.connectors.whatsapp.schemas import WhatsAppMessageMapper
from app.domain.entities.whatsapp_message import WhatsAppMessage


@dataclass
class ProcessWebhookMessageRequest:
    """
    Request to process incoming webhook message.

    Attributes:
        webhook_payload: Complete webhook payload from WhatsApp
    """
    webhook_payload: dict[str, Any]


@dataclass
class ProcessWebhookMessageResponse:
    """
    Response after processing webhook.

    Attributes:
        success: Whether processing was successful
        messages: List of incoming WhatsAppMessage entities
        status_updates: List of message status updates
        message_count: Number of messages processed
        error: Error message if failed
    """
    success: bool
    messages: list[WhatsAppMessage] = field(default_factory=list)
    status_updates: list[dict] = field(default_factory=list)
    message_count: int = 0
    error: Optional[str] = None


class ProcessWebhookMessageUseCase:
    """
    Use case for processing incoming WhatsApp webhooks.

    Parses webhook payloads and extracts messages and status updates.

    In future enhancements, this could:
    - Store messages in database
    - Trigger notifications
    - Auto-respond based on rules
    - Forward to other systems
    """

    async def execute(
        self,
        request: ProcessWebhookMessageRequest
    ) -> ProcessWebhookMessageResponse:
        """
        Execute the use case to process webhook.

        Args:
            request: Process webhook message request

        Returns:
            Response with extracted messages and status updates
        """
        try:
            payload = request.webhook_payload

            # Validate webhook payload structure
            if not payload or "object" not in payload:
                return ProcessWebhookMessageResponse(
                    success=False,
                    error="Invalid webhook payload structure"
                )

            # Only process whatsapp_business_account webhooks
            if payload.get("object") != "whatsapp_business_account":
                return ProcessWebhookMessageResponse(
                    success=False,
                    error=f"Unsupported webhook object type: {payload.get('object')}"
                )

            # Parse messages
            messages = WhatsAppMessageMapper.parse_webhook_payload(payload)

            # Parse status updates
            status_updates = WhatsAppMessageMapper.parse_status_update(payload)

            # TODO: Future enhancements
            # - Store messages in database
            # - Trigger notification handlers
            # - Process auto-reply rules
            # - Forward to other systems (email, Slack, etc.)

            return ProcessWebhookMessageResponse(
                success=True,
                messages=messages,
                status_updates=status_updates,
                message_count=len(messages)
            )

        except Exception as e:
            return ProcessWebhookMessageResponse(
                success=False,
                error=str(e)
            )

"""
WhatsApp Business Cloud API schema mappers.
Converts between WhatsApp API format and domain entities.
"""
from datetime import datetime
from typing import Any, Optional

from app.domain.entities.whatsapp_message import (
    WhatsAppMessage,
    WhatsAppMessageDraft,
    WhatsAppMedia,
    WhatsAppContact
)
from app.domain.entities.whatsapp_template import (
    WhatsAppTemplate,
    WhatsAppTemplateComponent
)


class WhatsAppMessageMapper:
    """
    Maps between WhatsApp API message format and domain entities.

    Handles conversion for:
    - Outgoing messages (Domain → API format)
    - Incoming messages (Webhook → Domain)
    - Message status updates
    """

    @staticmethod
    def to_message_entity(webhook_data: dict[str, Any]) -> WhatsAppMessage:
        """
        Convert webhook message data to WhatsApp message entity.

        Args:
            webhook_data: Message data from WhatsApp webhook

        Returns:
            WhatsAppMessage entity

        Webhook message structure:
        {
            "from": "14155552671",
            "id": "wamid.xxx",
            "timestamp": "1234567890",
            "type": "text",
            "text": {"body": "Hello"},
            ...
        }
        """
        message_id = webhook_data.get("id", "")
        from_number = f"+{webhook_data.get('from', '')}"
        timestamp_str = webhook_data.get("timestamp", "0")
        timestamp = datetime.fromtimestamp(int(timestamp_str))
        message_type = webhook_data.get("type", "")

        # Extract content based on type
        text_content = None
        media = None
        context_message_id = None

        if message_type == "text":
            text_content = webhook_data.get("text", {}).get("body", "")

        elif message_type in ["image", "video", "document", "audio", "sticker"]:
            media_data = webhook_data.get(message_type, {})
            media = WhatsAppMedia(
                media_type=message_type,
                media_id=media_data.get("id"),
                mime_type=media_data.get("mime_type"),
                filename=media_data.get("filename"),
                caption=media_data.get("caption")
            )

        # Check for context (reply to message)
        if "context" in webhook_data:
            context_message_id = webhook_data["context"].get("id")

        return WhatsAppMessage(
            id=message_id,
            from_number=from_number,
            to_number="",  # Not provided in incoming messages
            timestamp=timestamp,
            message_type=message_type,
            text_content=text_content,
            media=media,
            context_message_id=context_message_id
        )

    @staticmethod
    def from_message_draft(draft: WhatsAppMessageDraft) -> dict[str, Any]:
        """
        Convert message draft to WhatsApp API format.

        Args:
            draft: WhatsAppMessageDraft entity

        Returns:
            Data for WhatsApp API request

        Note:
            This is handled directly in WhatsAppClient methods.
            Keeping this method for consistency with other mappers.
        """
        # Basic structure
        data: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": draft.to.lstrip('+'),
            "type": draft.message_type
        }

        # Add content based on type
        if draft.message_type == "text":
            data["text"] = {
                "preview_url": draft.preview_url,
                "body": draft.text_content or ""
            }

        elif draft.media and draft.message_type in ["image", "video", "document", "audio"]:
            media_object: dict[str, Any] = {}

            if draft.media.media_id:
                media_object["id"] = draft.media.media_id
            elif draft.media.media_url:
                media_object["link"] = draft.media.media_url

            if draft.media.caption:
                media_object["caption"] = draft.media.caption

            if draft.media.filename and draft.message_type == "document":
                media_object["filename"] = draft.media.filename

            data[draft.message_type] = media_object

        elif draft.message_type == "template":
            components = []
            if draft.template_params:
                components.append({
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": param}
                        for param in draft.template_params
                    ]
                })

            data["template"] = {
                "name": draft.template_name or "",
                "language": {"code": "en_US"},  # Default, should be provided
                "components": components
            }

        # Add context if replying
        if draft.reply_to_message_id:
            data["context"] = {
                "message_id": draft.reply_to_message_id
            }

        return data

    @staticmethod
    def parse_webhook_payload(payload: dict[str, Any]) -> list[WhatsAppMessage]:
        """
        Parse complete webhook payload and extract all messages.

        WhatsApp webhook can contain multiple messages in one payload.

        Args:
            payload: Complete webhook payload from WhatsApp

        Returns:
            List of WhatsAppMessage entities

        Webhook structure:
        {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "WABA_ID",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {...},
                        "contacts": [...],
                        "messages": [...]
                    },
                    "field": "messages"
                }]
            }]
        }
        """
        messages = []

        # Navigate webhook structure
        entries = payload.get("entry", [])

        for entry in entries:
            changes = entry.get("changes", [])

            for change in changes:
                value = change.get("value", {})

                # Extract messages
                message_list = value.get("messages", [])

                for msg_data in message_list:
                    try:
                        message = WhatsAppMessageMapper.to_message_entity(msg_data)
                        messages.append(message)
                    except Exception as e:
                        # Log error but continue processing other messages
                        print(f"Error parsing message: {e}")

        return messages

    @staticmethod
    def parse_status_update(payload: dict[str, Any]) -> list[dict]:
        """
        Parse message status updates from webhook.

        Status updates indicate when messages are delivered, read, etc.

        Args:
            payload: Complete webhook payload

        Returns:
            List of status update dictionaries

        Status update structure:
        {
            "id": "wamid.xxx",
            "status": "delivered",
            "timestamp": "1234567890",
            "recipient_id": "14155552671"
        }
        """
        status_updates = []

        entries = payload.get("entry", [])

        for entry in entries:
            changes = entry.get("changes", [])

            for change in changes:
                value = change.get("value", {})

                # Extract status updates
                statuses = value.get("statuses", [])

                for status_data in statuses:
                    status_updates.append({
                        "message_id": status_data.get("id"),
                        "status": status_data.get("status"),
                        "timestamp": datetime.fromtimestamp(
                            int(status_data.get("timestamp", 0))
                        ),
                        "recipient_id": f"+{status_data.get('recipient_id', '')}"
                    })

        return status_updates


class WhatsAppTemplateMapper:
    """
    Maps between WhatsApp API template format and domain entities.
    """

    @staticmethod
    def to_template_entity(api_data: dict[str, Any]) -> WhatsAppTemplate:
        """
        Convert WhatsApp API template data to domain entity.

        Args:
            api_data: Template data from WhatsApp API

        Returns:
            WhatsAppTemplate entity

        API template structure:
        {
            "id": "template_id",
            "name": "template_name",
            "language": "en_US",
            "status": "APPROVED",
            "category": "MARKETING",
            "components": [
                {
                    "type": "BODY",
                    "text": "Hello {{1}}, your order {{2}} is ready!",
                    ...
                }
            ]
        }
        """
        template_id = api_data.get("id", "")
        name = api_data.get("name", "")
        language = api_data.get("language", "en_US")
        status = api_data.get("status", "PENDING")
        category = api_data.get("category", "UTILITY")
        namespace = api_data.get("namespace")

        # Parse components
        components = []
        api_components = api_data.get("components", [])

        for comp_data in api_components:
            comp_type = comp_data.get("type", "")
            comp_text = comp_data.get("text")
            comp_format = comp_data.get("format")

            # Extract parameters from text ({{1}}, {{2}}, etc.)
            parameters = []
            if comp_text:
                import re
                param_pattern = r'\{\{(\d+)\}\}'
                matches = re.findall(param_pattern, comp_text)
                parameters = [f"{{{{{m}}}}}" for m in matches]

            component = WhatsAppTemplateComponent(
                type=comp_type,
                text=comp_text,
                parameters=parameters,
                format=comp_format
            )
            components.append(component)

        return WhatsAppTemplate(
            id=template_id,
            name=name,
            language=language,
            status=status,
            category=category,
            components=components,
            namespace=namespace
        )

    @staticmethod
    def to_template_list(api_data_list: list[dict[str, Any]]) -> list[WhatsAppTemplate]:
        """
        Convert list of API template data to list of domain entities.

        Args:
            api_data_list: List of template data from API

        Returns:
            List of WhatsAppTemplate entities
        """
        templates = []

        for api_data in api_data_list:
            try:
                template = WhatsAppTemplateMapper.to_template_entity(api_data)
                templates.append(template)
            except Exception as e:
                # Log error but continue processing
                print(f"Error parsing template: {e}")

        return templates

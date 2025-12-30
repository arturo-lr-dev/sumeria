"""
Test fixtures for WhatsApp integration.
Contains sample data for testing WhatsApp API responses and webhook payloads.
"""
from datetime import datetime


# ============ WhatsApp API Response Fixtures ============

SAMPLE_SEND_MESSAGE_RESPONSE = {
    "messaging_product": "whatsapp",
    "contacts": [
        {
            "input": "14155552671",
            "wa_id": "14155552671"
        }
    ],
    "messages": [
        {
            "id": "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA"
        }
    ]
}

SAMPLE_UPLOAD_MEDIA_RESPONSE = {
    "id": "1234567890123456"
}

SAMPLE_MEDIA_URL_RESPONSE = {
    "url": "https://lookaside.fbsbx.com/whatsapp_business/attachments/?mid=123456",
    "mime_type": "image/jpeg",
    "sha256": "abc123...",
    "file_size": 123456,
    "id": "1234567890123456",
    "messaging_product": "whatsapp"
}

SAMPLE_TEMPLATES_RESPONSE = {
    "data": [
        {
            "id": "template_001",
            "name": "order_confirmation",
            "language": "en_US",
            "status": "APPROVED",
            "category": "UTILITY",
            "components": [
                {
                    "type": "HEADER",
                    "text": "Order Confirmed!",
                    "format": "TEXT"
                },
                {
                    "type": "BODY",
                    "text": "Hi {{1}}, your order #{{2}} has been confirmed and will be delivered by {{3}}."
                },
                {
                    "type": "FOOTER",
                    "text": "Thank you for your purchase!"
                }
            ]
        },
        {
            "id": "template_002",
            "name": "appointment_reminder",
            "language": "en_US",
            "status": "PENDING",
            "category": "UTILITY",
            "components": [
                {
                    "type": "BODY",
                    "text": "Reminder: You have an appointment on {{1}} at {{2}}."
                }
            ]
        }
    ],
    "paging": {
        "cursors": {
            "before": "xyz",
            "after": "abc"
        }
    }
}


# ============ Webhook Payload Fixtures ============

SAMPLE_WEBHOOK_TEXT_MESSAGE = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15551234567",
                            "phone_number_id": "PHONE_NUMBER_ID"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "John Doe"
                                },
                                "wa_id": "14155552671"
                            }
                        ],
                        "messages": [
                            {
                                "from": "14155552671",
                                "id": "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA",
                                "timestamp": "1234567890",
                                "type": "text",
                                "text": {
                                    "body": "Hello, I need help with my order"
                                }
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

SAMPLE_WEBHOOK_IMAGE_MESSAGE = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15551234567",
                            "phone_number_id": "PHONE_NUMBER_ID"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "Jane Smith"
                                },
                                "wa_id": "14155552672"
                            }
                        ],
                        "messages": [
                            {
                                "from": "14155552672",
                                "id": "wamid.IMAGE123456",
                                "timestamp": "1234567891",
                                "type": "image",
                                "image": {
                                    "id": "1234567890123456",
                                    "mime_type": "image/jpeg",
                                    "sha256": "abc123...",
                                    "caption": "Here's a photo of the issue"
                                }
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

SAMPLE_WEBHOOK_STATUS_UPDATE = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15551234567",
                            "phone_number_id": "PHONE_NUMBER_ID"
                        },
                        "statuses": [
                            {
                                "id": "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA",
                                "status": "delivered",
                                "timestamp": "1234567890",
                                "recipient_id": "14155552671",
                                "conversation": {
                                    "id": "CONVERSATION_ID",
                                    "origin": {
                                        "type": "business_initiated"
                                    }
                                },
                                "pricing": {
                                    "billable": True,
                                    "pricing_model": "CBP",
                                    "category": "business_initiated"
                                }
                            },
                            {
                                "id": "wamid.HBgLMTQxNTU1NTI2NzEVAgARGBI5MjQxNjI3NzgwNzAzNTAxNTAA",
                                "status": "read",
                                "timestamp": "1234567892",
                                "recipient_id": "14155552671"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}


# ============ Domain Entity Fixtures ============

def create_sample_message_draft(
    to: str = "+14155552671",
    message_type: str = "text",
    text_content: str = "Test message"
):
    """Create a sample WhatsAppMessageDraft for testing."""
    from app.domain.entities.whatsapp_message import WhatsAppMessageDraft

    return WhatsAppMessageDraft(
        to=to,
        message_type=message_type,
        text_content=text_content
    )


def create_sample_media():
    """Create a sample WhatsAppMedia for testing."""
    from app.domain.entities.whatsapp_message import WhatsAppMedia

    return WhatsAppMedia(
        media_type="image",
        media_id="1234567890123456",
        mime_type="image/jpeg",
        filename="test.jpg",
        caption="Test caption"
    )

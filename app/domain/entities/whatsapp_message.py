"""
WhatsApp message domain entities.
Represents WhatsApp Business Cloud API messages, contacts, and media.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WhatsAppContact:
    """
    Represents a WhatsApp contact/recipient.

    Attributes:
        phone_number: Phone number in E.164 format (e.g., +1234567890)
        name: Contact display name
        profile_name: Profile name from incoming messages
    """
    phone_number: str
    name: Optional[str] = None
    profile_name: Optional[str] = None

    def __post_init__(self):
        """Validate phone number format."""
        if not self.phone_number.startswith('+'):
            raise ValueError(f"Phone number must be in E.164 format (start with +): {self.phone_number}")


@dataclass
class WhatsAppMedia:
    """
    Represents WhatsApp media attachment.

    Supports: image, video, document, audio, sticker

    Attributes:
        media_type: Type of media (image, video, document, audio, sticker)
        media_id: WhatsApp media ID (for uploaded media or received media)
        media_url: Public URL to media file (for sending from URL)
        mime_type: MIME type of the media
        filename: Original filename
        caption: Optional caption for the media
        data: Binary data for uploads (optional)
    """
    media_type: str  # image, video, document, audio, sticker
    media_id: Optional[str] = None
    media_url: Optional[str] = None
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    caption: Optional[str] = None
    data: Optional[bytes] = None

    def __post_init__(self):
        """Validate media type."""
        valid_types = ['image', 'video', 'document', 'audio', 'sticker']
        if self.media_type not in valid_types:
            raise ValueError(f"Invalid media_type. Must be one of: {valid_types}")


@dataclass
class WhatsAppMessage:
    """
    Core WhatsApp message entity.

    Represents a complete WhatsApp message with all metadata.

    Attributes:
        id: WhatsApp message ID (wamid.*)
        from_number: Sender phone number (E.164 format)
        to_number: Recipient phone number (E.164 format)
        timestamp: Message timestamp
        message_type: Type of message (text, image, video, document, audio, template, etc.)
        text_content: Text content (for text messages)
        media: Media attachment (for media messages)
        template_name: Template name (for template messages)
        template_params: Template parameters (for template messages)
        status: Message status (sent, delivered, read, failed)
        context_message_id: ID of message being replied to (for replies)
        error_message: Error message if message failed
    """
    id: str
    from_number: str
    to_number: str
    timestamp: datetime
    message_type: str

    # Content based on type
    text_content: Optional[str] = None
    media: Optional[WhatsAppMedia] = None
    template_name: Optional[str] = None
    template_params: Optional[list[str]] = None

    # Metadata
    status: Optional[str] = None  # sent, delivered, read, failed
    context_message_id: Optional[str] = None  # For replies
    error_message: Optional[str] = None

    def is_text_message(self) -> bool:
        """Check if message is a text message."""
        return self.message_type == 'text'

    def is_media_message(self) -> bool:
        """Check if message is a media message."""
        return self.message_type in ['image', 'video', 'document', 'audio', 'sticker']

    def is_template_message(self) -> bool:
        """Check if message is a template message."""
        return self.message_type == 'template'

    def has_media(self) -> bool:
        """Check if message has media attachment."""
        return self.media is not None

    def is_reply(self) -> bool:
        """Check if message is a reply to another message."""
        return self.context_message_id is not None


@dataclass
class WhatsAppMessageDraft:
    """
    Represents a draft message to be sent.

    Used to construct messages before sending through the API.

    Attributes:
        to: Recipient phone number (E.164 format)
        message_type: Type of message to send
        text_content: Text content (for text messages)
        media: Media attachment (for media messages)
        template_name: Template name (for template messages)
        template_params: Template parameters (for template messages)
        preview_url: Enable URL preview (for text messages with links)
        reply_to_message_id: ID of message to reply to
    """
    to: str
    message_type: str

    # Content based on type
    text_content: Optional[str] = None
    media: Optional[WhatsAppMedia] = None
    template_name: Optional[str] = None
    template_params: Optional[list[str]] = None

    # Optional features
    preview_url: bool = False
    reply_to_message_id: Optional[str] = None

    def __post_init__(self):
        """Validate draft data."""
        # Validate phone number format
        if not self.to.startswith('+'):
            raise ValueError(f"Recipient phone number must be in E.164 format: {self.to}")

        # Validate message type
        valid_types = ['text', 'image', 'video', 'document', 'audio', 'template', 'sticker']
        if self.message_type not in valid_types:
            raise ValueError(f"Invalid message_type. Must be one of: {valid_types}")

        # Validate content based on type
        if self.message_type == 'text' and not self.text_content:
            raise ValueError("text_content is required for text messages")

        if self.message_type in ['image', 'video', 'document', 'audio', 'sticker'] and not self.media:
            raise ValueError(f"media is required for {self.message_type} messages")

        if self.message_type == 'template' and not self.template_name:
            raise ValueError("template_name is required for template messages")

    def validate_text_length(self) -> bool:
        """
        Validate text message length.

        WhatsApp allows up to 4096 characters for text messages.
        """
        if self.text_content and len(self.text_content) > 4096:
            raise ValueError("Text message cannot exceed 4096 characters")
        return True

    def validate_caption_length(self) -> bool:
        """
        Validate media caption length.

        WhatsApp allows up to 1024 characters for captions.
        """
        if self.media and self.media.caption and len(self.media.caption) > 1024:
            raise ValueError("Media caption cannot exceed 1024 characters")
        return True

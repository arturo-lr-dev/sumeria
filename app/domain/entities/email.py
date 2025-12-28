"""
Email domain entities.
These represent the core business objects for email functionality.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class EmailLabel(str, Enum):
    """Common Gmail labels."""
    INBOX = "INBOX"
    SENT = "SENT"
    DRAFT = "DRAFT"
    TRASH = "TRASH"
    SPAM = "SPAM"
    STARRED = "STARRED"
    IMPORTANT = "IMPORTANT"
    UNREAD = "UNREAD"


@dataclass
class EmailAddress:
    """Represents an email address with optional name."""
    email: str
    name: Optional[str] = None

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email


@dataclass
class EmailAttachment:
    """Represents an email attachment."""
    filename: str
    mime_type: str
    size: int
    attachment_id: Optional[str] = None
    data: Optional[bytes] = None


@dataclass
class Email:
    """
    Core email entity representing a complete email message.
    This is the domain model, independent of Gmail API structure.
    """
    id: str
    thread_id: str
    subject: str
    from_address: EmailAddress
    to_addresses: list[EmailAddress]
    cc_addresses: list[EmailAddress] = field(default_factory=list)
    bcc_addresses: list[EmailAddress] = field(default_factory=list)
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    date: Optional[datetime] = None
    labels: list[str] = field(default_factory=list)
    attachments: list[EmailAttachment] = field(default_factory=list)
    snippet: Optional[str] = None
    is_read: bool = False
    is_starred: bool = False

    def has_label(self, label: str) -> bool:
        """Check if email has a specific label."""
        return label in self.labels

    def is_unread(self) -> bool:
        """Check if email is unread."""
        return not self.is_read

    def has_attachments(self) -> bool:
        """Check if email has attachments."""
        return len(self.attachments) > 0


@dataclass
class EmailDraft:
    """Represents a draft email to be sent."""
    to: list[EmailAddress]
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    cc: list[EmailAddress] = field(default_factory=list)
    bcc: list[EmailAddress] = field(default_factory=list)
    attachments: list[EmailAttachment] = field(default_factory=list)
    reply_to_message_id: Optional[str] = None

    def add_recipient(self, email: str, name: Optional[str] = None) -> None:
        """Add a recipient to the email."""
        self.to.append(EmailAddress(email=email, name=name))

    def add_cc(self, email: str, name: Optional[str] = None) -> None:
        """Add a CC recipient."""
        self.cc.append(EmailAddress(email=email, name=name))

    def add_attachment(self, filename: str, data: bytes, mime_type: str) -> None:
        """Add an attachment to the email."""
        self.attachments.append(
            EmailAttachment(
                filename=filename,
                data=data,
                mime_type=mime_type,
                size=len(data)
            )
        )


@dataclass
class EmailSearchCriteria:
    """Criteria for searching emails."""
    query: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    subject: Optional[str] = None
    has_attachment: Optional[bool] = None
    is_unread: Optional[bool] = None
    label: Optional[str] = None
    after_date: Optional[datetime] = None
    before_date: Optional[datetime] = None
    max_results: int = 100

    def to_gmail_query(self) -> str:
        """Convert search criteria to Gmail query string."""
        parts = []

        if self.query:
            parts.append(self.query)
        if self.from_address:
            parts.append(f"from:{self.from_address}")
        if self.to_address:
            parts.append(f"to:{self.to_address}")
        if self.subject:
            parts.append(f"subject:{self.subject}")
        if self.has_attachment:
            parts.append("has:attachment")
        if self.is_unread:
            parts.append("is:unread")
        if self.label:
            parts.append(f"label:{self.label}")
        if self.after_date:
            parts.append(f"after:{self.after_date.strftime('%Y/%m/%d')}")
        if self.before_date:
            parts.append(f"before:{self.before_date.strftime('%Y/%m/%d')}")

        return " ".join(parts) if parts else ""

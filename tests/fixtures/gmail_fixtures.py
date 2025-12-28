"""
Gmail test fixtures with sample data.
"""
from datetime import datetime
from app.domain.entities.email import Email, EmailAddress, EmailAttachment, EmailDraft


# Sample Gmail API message response
SAMPLE_GMAIL_MESSAGE = {
    "id": "18d4f5e6a7b8c9d0",
    "threadId": "18d4f5e6a7b8c9d0",
    "labelIds": ["INBOX", "UNREAD"],
    "snippet": "This is a test email snippet...",
    "payload": {
        "headers": [
            {"name": "From", "value": "John Doe <john@example.com>"},
            {"name": "To", "value": "jane@example.com"},
            {"name": "Cc", "value": "bob@example.com"},
            {"name": "Subject", "value": "Test Email Subject"},
            {"name": "Date", "value": "Mon, 20 Jan 2025 10:30:00 -0800"}
        ],
        "mimeType": "multipart/alternative",
        "body": {
            "size": 0
        },
        "parts": [
            {
                "mimeType": "text/plain",
                "body": {
                    "size": 100,
                    "data": "VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keS4="  # Base64: "This is a test email body."
                }
            },
            {
                "mimeType": "text/html",
                "body": {
                    "size": 150,
                    "data": "PGh0bWw+PGJvZHk+VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keS48L2JvZHk+PC9odG1sPg=="  # Base64: "<html><body>This is a test email body.</body></html>"
                }
            }
        ]
    }
}


# Sample Gmail message with attachment
SAMPLE_GMAIL_MESSAGE_WITH_ATTACHMENT = {
    "id": "18d4f5e6a7b8c9d1",
    "threadId": "18d4f5e6a7b8c9d1",
    "labelIds": ["INBOX"],
    "snippet": "Email with attachment...",
    "payload": {
        "headers": [
            {"name": "From", "value": "sender@example.com"},
            {"name": "To", "value": "recipient@example.com"},
            {"name": "Subject", "value": "Document Attached"},
            {"name": "Date", "value": "Tue, 21 Jan 2025 14:00:00 -0800"}
        ],
        "mimeType": "multipart/mixed",
        "parts": [
            {
                "mimeType": "text/plain",
                "body": {
                    "size": 50,
                    "data": "UGxlYXNlIGZpbmQgYXR0YWNoZWQgZG9jdW1lbnQu"  # "Please find attached document."
                }
            },
            {
                "filename": "document.pdf",
                "mimeType": "application/pdf",
                "body": {
                    "size": 1024,
                    "attachmentId": "ANGjdJ8w..."
                }
            }
        ]
    }
}


# Sample simple text-only message
SAMPLE_SIMPLE_MESSAGE = {
    "id": "simple123",
    "threadId": "simple123",
    "labelIds": ["SENT"],
    "snippet": "Simple message",
    "payload": {
        "headers": [
            {"name": "From", "value": "me@example.com"},
            {"name": "To", "value": "you@example.com"},
            {"name": "Subject", "value": "Simple Subject"}
        ],
        "mimeType": "text/plain",
        "body": {
            "size": 30,
            "data": "SGVsbG8sIHRoaXMgaXMgc2ltcGxlIHRleHQu"  # "Hello, this is simple text."
        }
    }
}


# Sample domain Email entity
def create_sample_email() -> Email:
    """Create a sample Email domain entity."""
    return Email(
        id="18d4f5e6a7b8c9d0",
        thread_id="18d4f5e6a7b8c9d0",
        subject="Test Email Subject",
        from_address=EmailAddress(email="john@example.com", name="John Doe"),
        to_addresses=[EmailAddress(email="jane@example.com")],
        cc_addresses=[EmailAddress(email="bob@example.com")],
        body_text="This is a test email body.",
        body_html="<html><body>This is a test email body.</body></html>",
        date=datetime(2025, 1, 20, 10, 30, 0),
        labels=["INBOX", "UNREAD"],
        snippet="This is a test email snippet...",
        is_read=False,
        is_starred=False
    )


def create_sample_email_with_attachment() -> Email:
    """Create a sample Email with attachment."""
    return Email(
        id="18d4f5e6a7b8c9d1",
        thread_id="18d4f5e6a7b8c9d1",
        subject="Document Attached",
        from_address=EmailAddress(email="sender@example.com"),
        to_addresses=[EmailAddress(email="recipient@example.com")],
        body_text="Please find attached document.",
        date=datetime(2025, 1, 21, 14, 0, 0),
        labels=["INBOX"],
        snippet="Email with attachment...",
        attachments=[
            EmailAttachment(
                filename="document.pdf",
                mime_type="application/pdf",
                size=1024,
                attachment_id="ANGjdJ8w..."
            )
        ],
        is_read=True,
        is_starred=False
    )


def create_sample_draft() -> EmailDraft:
    """Create a sample EmailDraft."""
    return EmailDraft(
        to=[EmailAddress(email="recipient@example.com", name="Recipient Name")],
        subject="Test Draft Subject",
        body_text="This is the plain text body.",
        body_html="<p>This is the HTML body.</p>",
        cc=[EmailAddress(email="cc@example.com")],
        bcc=[EmailAddress(email="bcc@example.com")]
    )


# Gmail API search results
SAMPLE_SEARCH_RESULTS = {
    "messages": [
        {"id": "18d4f5e6a7b8c9d0", "threadId": "18d4f5e6a7b8c9d0"},
        {"id": "18d4f5e6a7b8c9d1", "threadId": "18d4f5e6a7b8c9d1"}
    ],
    "resultSizeEstimate": 2
}


# Empty search results
EMPTY_SEARCH_RESULTS = {
    "resultSizeEstimate": 0
}

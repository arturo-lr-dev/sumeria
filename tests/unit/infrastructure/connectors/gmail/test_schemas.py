"""
Unit tests for Gmail schemas and message mapping.
"""
import pytest
from datetime import datetime
from app.infrastructure.connectors.gmail.schemas import GmailMessageMapper
from app.domain.entities.email import EmailAddress, EmailDraft, EmailLabel
from tests.fixtures.gmail_fixtures import (
    SAMPLE_GMAIL_MESSAGE,
    SAMPLE_GMAIL_MESSAGE_WITH_ATTACHMENT,
    SAMPLE_SIMPLE_MESSAGE,
    create_sample_draft
)


class TestGmailMessageMapper:
    """Test suite for GmailMessageMapper."""

    def test_to_email_entity_full_message(self):
        """Test converting a full Gmail message to Email entity."""
        email = GmailMessageMapper.to_email_entity(SAMPLE_GMAIL_MESSAGE)

        assert email.id == "18d4f5e6a7b8c9d0"
        assert email.thread_id == "18d4f5e6a7b8c9d0"
        assert email.subject == "Test Email Subject"
        assert email.from_address.email == "john@example.com"
        assert email.from_address.name == "John Doe"
        assert len(email.to_addresses) == 1
        assert email.to_addresses[0].email == "jane@example.com"
        assert len(email.cc_addresses) == 1
        assert email.cc_addresses[0].email == "bob@example.com"
        assert email.body_text == "This is a test email body."
        assert "<html>" in email.body_html
        assert email.snippet == "This is a test email snippet..."
        assert email.is_read is False
        assert "INBOX" in email.labels
        assert "UNREAD" in email.labels

    def test_to_email_entity_with_attachment(self):
        """Test converting message with attachment."""
        email = GmailMessageMapper.to_email_entity(SAMPLE_GMAIL_MESSAGE_WITH_ATTACHMENT)

        assert email.id == "18d4f5e6a7b8c9d1"
        assert email.has_attachments() is True
        assert len(email.attachments) == 1
        assert email.attachments[0].filename == "document.pdf"
        assert email.attachments[0].mime_type == "application/pdf"
        assert email.attachments[0].size == 1024
        assert email.attachments[0].attachment_id == "ANGjdJ8w..."

    def test_to_email_entity_simple_message(self):
        """Test converting simple text-only message."""
        email = GmailMessageMapper.to_email_entity(SAMPLE_SIMPLE_MESSAGE)

        assert email.id == "simple123"
        assert email.subject == "Simple Subject"
        assert email.body_text == "Hello, this is simple text."
        assert email.body_html is None
        assert email.has_attachments() is False
        assert email.is_read is True  # No UNREAD label
        assert "SENT" in email.labels

    def test_parse_email_address_with_name(self):
        """Test parsing email address with name."""
        address = GmailMessageMapper._parse_email_address("John Doe <john@example.com>")

        assert address.email == "john@example.com"
        assert address.name == "John Doe"

    def test_parse_email_address_without_name(self):
        """Test parsing email address without name."""
        address = GmailMessageMapper._parse_email_address("john@example.com")

        assert address.email == "john@example.com"
        assert address.name is None

    def test_parse_email_address_empty(self):
        """Test parsing empty email address."""
        address = GmailMessageMapper._parse_email_address("")

        assert address.email == "unknown@unknown.com"

    def test_parse_email_addresses_multiple(self):
        """Test parsing multiple email addresses."""
        addresses = GmailMessageMapper._parse_email_addresses(
            "John <john@example.com>, jane@example.com, Bob <bob@example.com>"
        )

        assert len(addresses) == 3
        assert addresses[0].email == "john@example.com"
        assert addresses[0].name == "John"
        assert addresses[1].email == "jane@example.com"
        assert addresses[2].email == "bob@example.com"

    def test_parse_email_addresses_empty(self):
        """Test parsing empty addresses string."""
        addresses = GmailMessageMapper._parse_email_addresses("")

        assert len(addresses) == 0

    def test_from_email_draft_simple(self):
        """Test converting EmailDraft to Gmail message format."""
        draft = EmailDraft(
            to=[EmailAddress(email="recipient@example.com")],
            subject="Test Subject",
            body_text="Test body"
        )

        raw_message = GmailMessageMapper.from_email_draft(draft)

        assert isinstance(raw_message, str)
        assert len(raw_message) > 0
        # Base64 encoded message should not contain newlines
        assert '\n' not in raw_message

    def test_from_email_draft_with_html(self):
        """Test converting draft with HTML body."""
        draft = EmailDraft(
            to=[EmailAddress(email="recipient@example.com")],
            subject="Test Subject",
            body_text="Plain text",
            body_html="<p>HTML text</p>"
        )

        raw_message = GmailMessageMapper.from_email_draft(draft)

        assert isinstance(raw_message, str)
        assert len(raw_message) > 0

    def test_from_email_draft_with_cc_bcc(self):
        """Test converting draft with CC and BCC."""
        draft = EmailDraft(
            to=[EmailAddress(email="to@example.com")],
            subject="Test",
            body_text="Body",
            cc=[EmailAddress(email="cc@example.com")],
            bcc=[EmailAddress(email="bcc@example.com")]
        )

        raw_message = GmailMessageMapper.from_email_draft(draft)

        assert isinstance(raw_message, str)

    def test_from_email_draft_with_attachment(self):
        """Test converting draft with attachment."""
        draft = create_sample_draft()
        draft.add_attachment("test.txt", b"test content", "text/plain")

        raw_message = GmailMessageMapper.from_email_draft(draft)

        assert isinstance(raw_message, str)
        assert len(raw_message) > 0

    def test_extract_body_multipart(self):
        """Test extracting body from multipart message."""
        payload = SAMPLE_GMAIL_MESSAGE["payload"]
        body_text, body_html = GmailMessageMapper._extract_body(payload)

        assert body_text == "This is a test email body."
        assert "<html>" in body_html

    def test_extract_body_simple_text(self):
        """Test extracting body from simple text message."""
        payload = SAMPLE_SIMPLE_MESSAGE["payload"]
        body_text, body_html = GmailMessageMapper._extract_body(payload)

        assert body_text == "Hello, this is simple text."
        assert body_html is None

    def test_extract_attachments(self):
        """Test extracting attachments from payload."""
        payload = SAMPLE_GMAIL_MESSAGE_WITH_ATTACHMENT["payload"]
        attachments = GmailMessageMapper._extract_attachments(payload)

        assert len(attachments) == 1
        assert attachments[0].filename == "document.pdf"

    def test_extract_attachments_none(self):
        """Test extracting attachments when there are none."""
        payload = SAMPLE_SIMPLE_MESSAGE["payload"]
        attachments = GmailMessageMapper._extract_attachments(payload)

        assert len(attachments) == 0

    def test_parse_date_valid(self):
        """Test parsing valid date string."""
        date_str = "Mon, 20 Jan 2025 10:30:00 -0800"
        date = GmailMessageMapper._parse_date(date_str)

        assert isinstance(date, datetime)
        assert date.year == 2025
        assert date.month == 1
        assert date.day == 20

    def test_parse_date_invalid(self):
        """Test parsing invalid date string."""
        date = GmailMessageMapper._parse_date("invalid date")

        assert date is None

    def test_label_parsing_starred(self):
        """Test parsing STARRED label."""
        message = SAMPLE_GMAIL_MESSAGE.copy()
        message["labelIds"] = ["INBOX", "STARRED"]

        email = GmailMessageMapper.to_email_entity(message)

        assert email.is_starred is True
        assert email.is_read is True  # No UNREAD label

    def test_label_parsing_unread(self):
        """Test parsing UNREAD label."""
        message = SAMPLE_GMAIL_MESSAGE.copy()
        message["labelIds"] = ["INBOX", "UNREAD"]

        email = GmailMessageMapper.to_email_entity(message)

        assert email.is_read is False
        assert email.is_starred is False

    def test_missing_headers(self):
        """Test handling message with missing headers."""
        message = {
            "id": "test123",
            "threadId": "test123",
            "payload": {
                "headers": [],
                "body": {}
            }
        }

        email = GmailMessageMapper.to_email_entity(message)

        assert email.id == "test123"
        assert email.subject == "(No Subject)"
        assert email.from_address.email == "unknown@unknown.com"

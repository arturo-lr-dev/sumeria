"""
Gmail API response schemas and mappers.
Maps Gmail API responses to domain entities.
"""
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Any, Optional
from app.domain.entities.email import (
    Email,
    EmailAddress,
    EmailAttachment,
    EmailDraft,
    EmailLabel
)


class GmailMessageMapper:
    """Maps Gmail API message format to domain Email entity."""

    @staticmethod
    def to_email_entity(gmail_message: dict[str, Any]) -> Email:
        """
        Convert Gmail API message to Email domain entity.

        Args:
            gmail_message: Message from Gmail API

        Returns:
            Email entity
        """
        headers = {
            h['name'].lower(): h['value']
            for h in gmail_message.get('payload', {}).get('headers', [])
        }

        # Parse addresses
        from_addr = GmailMessageMapper._parse_email_address(
            headers.get('from', '')
        )
        to_addrs = GmailMessageMapper._parse_email_addresses(
            headers.get('to', '')
        )
        cc_addrs = GmailMessageMapper._parse_email_addresses(
            headers.get('cc', '')
        )

        # Get body
        body_text, body_html = GmailMessageMapper._extract_body(
            gmail_message.get('payload', {})
        )

        # Parse date
        date_str = headers.get('date')
        date = GmailMessageMapper._parse_date(date_str) if date_str else None

        # Get labels
        labels = gmail_message.get('labelIds', [])

        # Check read status
        is_read = EmailLabel.UNREAD.value not in labels
        is_starred = EmailLabel.STARRED.value in labels

        # Get attachments
        attachments = GmailMessageMapper._extract_attachments(
            gmail_message.get('payload', {})
        )

        return Email(
            id=gmail_message['id'],
            thread_id=gmail_message.get('threadId', ''),
            subject=headers.get('subject', '(No Subject)'),
            from_address=from_addr,
            to_addresses=to_addrs,
            cc_addresses=cc_addrs,
            body_text=body_text,
            body_html=body_html,
            date=date,
            labels=labels,
            attachments=attachments,
            snippet=gmail_message.get('snippet', ''),
            is_read=is_read,
            is_starred=is_starred
        )

    @staticmethod
    def _parse_email_address(address_str: str) -> EmailAddress:
        """Parse email address from string like 'Name <email@example.com>'."""
        if not address_str:
            return EmailAddress(email="unknown@unknown.com")

        if '<' in address_str and '>' in address_str:
            name = address_str.split('<')[0].strip().strip('"')
            email = address_str.split('<')[1].split('>')[0].strip()
            return EmailAddress(email=email, name=name if name else None)

        return EmailAddress(email=address_str.strip())

    @staticmethod
    def _parse_email_addresses(addresses_str: str) -> list[EmailAddress]:
        """Parse multiple email addresses from comma-separated string."""
        if not addresses_str:
            return []

        addresses = []
        for addr in addresses_str.split(','):
            addr = addr.strip()
            if addr:
                addresses.append(GmailMessageMapper._parse_email_address(addr))

        return addresses

    @staticmethod
    def _extract_body(payload: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """Extract text and HTML body from message payload."""
        body_text = None
        body_html = None

        def decode_body(data: str) -> str:
            """Decode base64url encoded body data."""
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        # Check if simple text/html message
        if 'body' in payload and payload['body'].get('data'):
            mime_type = payload.get('mimeType', '')
            data = decode_body(payload['body']['data'])

            if 'text/plain' in mime_type:
                body_text = data
            elif 'text/html' in mime_type:
                body_html = data

        # Check multipart message
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')

                if mime_type == 'text/plain' and part.get('body', {}).get('data'):
                    body_text = decode_body(part['body']['data'])
                elif mime_type == 'text/html' and part.get('body', {}).get('data'):
                    body_html = decode_body(part['body']['data'])
                elif 'parts' in part:
                    # Recursive for nested parts
                    text, html = GmailMessageMapper._extract_body(part)
                    body_text = body_text or text
                    body_html = body_html or html

        return body_text, body_html

    @staticmethod
    def _extract_attachments(payload: dict[str, Any]) -> list[EmailAttachment]:
        """Extract attachment metadata from message payload."""
        attachments = []

        def process_part(part: dict[str, Any]) -> None:
            """Process a message part for attachments."""
            if part.get('filename'):
                attachment = EmailAttachment(
                    filename=part['filename'],
                    mime_type=part.get('mimeType', 'application/octet-stream'),
                    size=part.get('body', {}).get('size', 0),
                    attachment_id=part.get('body', {}).get('attachmentId')
                )
                attachments.append(attachment)

            # Check nested parts
            if 'parts' in part:
                for sub_part in part['parts']:
                    process_part(sub_part)

        if 'parts' in payload:
            for part in payload['parts']:
                process_part(part)

        return attachments

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """Parse date string to datetime."""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    @staticmethod
    def from_email_draft(draft: EmailDraft) -> str:
        """
        Convert EmailDraft to Gmail API message format (base64 encoded).

        Args:
            draft: Email draft to send

        Returns:
            Base64 encoded message string
        """
        # Create MIME message
        if draft.body_html:
            message = MIMEMultipart('alternative')
            if draft.body_text:
                message.attach(MIMEText(draft.body_text, 'plain'))
            message.attach(MIMEText(draft.body_html, 'html'))
        else:
            message = MIMEText(draft.body_text or '', 'plain')

        # Set headers
        message['To'] = ', '.join(str(addr) for addr in draft.to)
        message['Subject'] = draft.subject

        if draft.cc:
            message['Cc'] = ', '.join(str(addr) for addr in draft.cc)

        if draft.reply_to_message_id:
            message['In-Reply-To'] = draft.reply_to_message_id
            message['References'] = draft.reply_to_message_id

        # Add attachments
        if draft.attachments:
            if not isinstance(message, MIMEMultipart):
                # Convert to multipart
                content = message.get_payload()
                message = MIMEMultipart()
                message.attach(MIMEText(content, 'plain'))

            for attachment in draft.attachments:
                part = MIMEBase(*attachment.mime_type.split('/'))
                part.set_payload(attachment.data)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={attachment.filename}'
                )
                message.attach(part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode('utf-8')

        return raw_message

"""
MCP Tools for Gmail operations.
Exposes Gmail functionality through the MCP protocol.
"""
from typing import Optional
from pydantic import BaseModel

from app.application.use_cases.gmail.send_email import SendEmailUseCase, SendEmailRequest
from app.application.use_cases.gmail.search_emails import SearchEmailsUseCase, SearchEmailsRequest
from app.application.use_cases.gmail.get_email import GetEmailUseCase, GetEmailRequest
from app.application.use_cases.gmail.manage_labels import (
    MarkAsReadUseCase,
    MarkAsUnreadUseCase,
    AddLabelUseCase,
    MarkAsReadRequest,
    MarkAsUnreadRequest,
    AddLabelRequest
)


# Response models for structured output
class EmailSummary(BaseModel):
    """Summary of an email for display."""
    id: str
    subject: str
    from_email: str
    from_name: Optional[str] = None
    date: Optional[str] = None
    snippet: str
    is_read: bool
    has_attachments: bool


class SendEmailResult(BaseModel):
    """Result of sending an email."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class SearchEmailsResult(BaseModel):
    """Result of searching emails."""
    success: bool
    count: int
    emails: list[EmailSummary]
    error: Optional[str] = None


class EmailDetail(BaseModel):
    """Detailed email information."""
    id: str
    subject: str
    from_email: str
    from_name: Optional[str] = None
    to_emails: list[str]
    cc_emails: list[str]
    date: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    labels: list[str]
    is_read: bool
    is_starred: bool
    attachments: list[dict]


class GetEmailResult(BaseModel):
    """Result of getting email details."""
    success: bool
    email: Optional[EmailDetail] = None
    error: Optional[str] = None


class GmailTools:
    """Collection of Gmail MCP tools."""

    def __init__(self):
        """Initialize use cases."""
        self.send_email_uc = SendEmailUseCase()
        self.search_emails_uc = SearchEmailsUseCase()
        self.get_email_uc = GetEmailUseCase()
        self.mark_read_uc = MarkAsReadUseCase()
        self.mark_unread_uc = MarkAsUnreadUseCase()
        self.add_label_uc = AddLabelUseCase()

    async def send_email(
        self,
        to: list[str],
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        cc: Optional[list[str]] = None,
        bcc: Optional[list[str]] = None,
        account_id: Optional[str] = None
    ) -> SendEmailResult:
        """
        Send an email via Gmail.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body_text: Plain text body (optional)
            body_html: HTML body (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            account_id: Gmail account to use (optional, uses default if not specified)

        Returns:
            SendEmailResult with success status and message ID
        """
        request = SendEmailRequest(
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            cc=cc,
            bcc=bcc,
            account_id=account_id
        )

        response = await self.send_email_uc.execute(request)

        return SendEmailResult(
            success=response.success,
            message_id=response.message_id,
            error=response.error
        )

    async def search_emails(
        self,
        query: Optional[str] = None,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        subject: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        label: Optional[str] = None,
        max_results: int = 10,
        account_id: Optional[str] = None
    ) -> SearchEmailsResult:
        """
        Search emails in Gmail.

        Args:
            query: Search query (Gmail search syntax)
            from_address: Filter by sender email
            to_address: Filter by recipient email
            subject: Filter by subject keywords
            has_attachment: Filter emails with attachments
            is_unread: Filter unread emails
            label: Filter by Gmail label (INBOX, SENT, etc.)
            max_results: Maximum number of results (default: 10, max: 100)
            account_id: Gmail account to search (optional)

        Returns:
            SearchEmailsResult with matching emails
        """
        request = SearchEmailsRequest(
            query=query,
            from_address=from_address,
            to_address=to_address,
            subject=subject,
            has_attachment=has_attachment,
            is_unread=is_unread,
            label=label,
            max_results=min(max_results, 100),
            account_id=account_id
        )

        response = await self.search_emails_uc.execute(request)

        # Convert to summaries
        emails = [
            EmailSummary(
                id=email.id,
                subject=email.subject,
                from_email=email.from_address.email,
                from_name=email.from_address.name,
                date=email.date.isoformat() if email.date else None,
                snippet=email.snippet or "",
                is_read=email.is_read,
                has_attachments=email.has_attachments()
            )
            for email in response.emails
        ]

        return SearchEmailsResult(
            success=response.success,
            count=response.count,
            emails=emails,
            error=response.error
        )

    async def get_email(
        self,
        message_id: str,
        account_id: Optional[str] = None
    ) -> GetEmailResult:
        """
        Get detailed information about a specific email.

        Args:
            message_id: Gmail message ID
            account_id: Gmail account to use (optional)

        Returns:
            GetEmailResult with complete email details
        """
        request = GetEmailRequest(
            message_id=message_id,
            account_id=account_id
        )

        response = await self.get_email_uc.execute(request)

        if not response.success or not response.email:
            return GetEmailResult(
                success=False,
                error=response.error
            )

        email = response.email

        # Convert to detail model
        email_detail = EmailDetail(
            id=email.id,
            subject=email.subject,
            from_email=email.from_address.email,
            from_name=email.from_address.name,
            to_emails=[addr.email for addr in email.to_addresses],
            cc_emails=[addr.email for addr in email.cc_addresses],
            date=email.date.isoformat() if email.date else None,
            body_text=email.body_text,
            body_html=email.body_html,
            labels=email.labels,
            is_read=email.is_read,
            is_starred=email.is_starred,
            attachments=[
                {
                    "filename": att.filename,
                    "mime_type": att.mime_type,
                    "size": att.size
                }
                for att in email.attachments
            ]
        )

        return GetEmailResult(
            success=True,
            email=email_detail
        )

    async def mark_as_read(
        self,
        message_id: str,
        account_id: Optional[str] = None
    ) -> dict:
        """
        Mark an email as read.

        Args:
            message_id: Gmail message ID
            account_id: Gmail account to use (optional)

        Returns:
            Success status
        """
        request = MarkAsReadRequest(
            message_id=message_id,
            account_id=account_id
        )

        response = await self.mark_read_uc.execute(request)

        return {
            "success": response.success,
            "error": response.error
        }

    async def mark_as_unread(
        self,
        message_id: str,
        account_id: Optional[str] = None
    ) -> dict:
        """
        Mark an email as unread.

        Args:
            message_id: Gmail message ID
            account_id: Gmail account to use (optional)

        Returns:
            Success status
        """
        request = MarkAsUnreadRequest(
            message_id=message_id,
            account_id=account_id
        )

        response = await self.mark_unread_uc.execute(request)

        return {
            "success": response.success,
            "error": response.error
        }

    async def add_label(
        self,
        message_id: str,
        label: str,
        account_id: Optional[str] = None
    ) -> dict:
        """
        Add a label to an email.

        Args:
            message_id: Gmail message ID
            label: Label to add (e.g., 'STARRED', 'IMPORTANT')
            account_id: Gmail account to use (optional)

        Returns:
            Success status
        """
        request = AddLabelRequest(
            message_id=message_id,
            label=label,
            account_id=account_id
        )

        response = await self.add_label_uc.execute(request)

        return {
            "success": response.success,
            "error": response.error
        }


# Global instance
gmail_tools = GmailTools()

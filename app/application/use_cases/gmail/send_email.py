"""
Use case: Send an email.
"""
from dataclasses import dataclass
from typing import Optional
from app.domain.entities.email import EmailDraft, EmailAddress
from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager


@dataclass
class SendEmailRequest:
    """Request to send an email."""
    to: list[str]  # List of email addresses
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    cc: Optional[list[str]] = None
    bcc: Optional[list[str]] = None
    account_id: Optional[str] = None  # Which account to use


@dataclass
class SendEmailResponse:
    """Response after sending an email."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class SendEmailUseCase:
    """Use case for sending emails."""

    async def execute(self, request: SendEmailRequest) -> SendEmailResponse:
        """
        Send an email.

        Args:
            request: Send email request

        Returns:
            SendEmailResponse with result
        """
        try:
            # Get Gmail client for the specified account
            client = gmail_account_manager.get_client(request.account_id)

            # Build email draft
            draft = EmailDraft(
                to=[EmailAddress(email=addr) for addr in request.to],
                subject=request.subject,
                body_text=request.body_text,
                body_html=request.body_html,
                cc=[EmailAddress(email=addr) for addr in (request.cc or [])],
                bcc=[EmailAddress(email=addr) for addr in (request.bcc or [])]
            )

            # Send email
            message_id = await client.send_email(draft)

            return SendEmailResponse(
                success=True,
                message_id=message_id
            )

        except Exception as e:
            return SendEmailResponse(
                success=False,
                error=str(e)
            )

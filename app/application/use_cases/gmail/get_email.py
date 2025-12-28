"""
Use case: Get a specific email by ID.
"""
from dataclasses import dataclass
from typing import Optional
from app.domain.entities.email import Email
from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager


@dataclass
class GetEmailRequest:
    """Request to get an email."""
    message_id: str
    account_id: Optional[str] = None


@dataclass
class GetEmailResponse:
    """Response with email data."""
    success: bool
    email: Optional[Email] = None
    error: Optional[str] = None


class GetEmailUseCase:
    """Use case for getting a specific email."""

    async def execute(self, request: GetEmailRequest) -> GetEmailResponse:
        """
        Get an email by ID.

        Args:
            request: Get email request

        Returns:
            GetEmailResponse with email data
        """
        try:
            # Get Gmail client
            client = gmail_account_manager.get_client(request.account_id)

            # Get email
            email = await client.get_email(request.message_id)

            return GetEmailResponse(
                success=True,
                email=email
            )

        except Exception as e:
            return GetEmailResponse(
                success=False,
                error=str(e)
            )

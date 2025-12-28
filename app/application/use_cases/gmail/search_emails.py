"""
Use case: Search emails.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.entities.email import Email, EmailSearchCriteria
from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager


@dataclass
class SearchEmailsRequest:
    """Request to search emails."""
    query: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    subject: Optional[str] = None
    has_attachment: Optional[bool] = None
    is_unread: Optional[bool] = None
    label: Optional[str] = None
    after_date: Optional[datetime] = None
    before_date: Optional[datetime] = None
    max_results: int = 10
    account_id: Optional[str] = None


@dataclass
class SearchEmailsResponse:
    """Response with search results."""
    success: bool
    emails: list[Email]
    count: int
    error: Optional[str] = None


class SearchEmailsUseCase:
    """Use case for searching emails."""

    async def execute(self, request: SearchEmailsRequest) -> SearchEmailsResponse:
        """
        Search emails based on criteria.

        Args:
            request: Search request

        Returns:
            SearchEmailsResponse with results
        """
        try:
            # Get Gmail client
            client = gmail_account_manager.get_client(request.account_id)

            # Build search criteria
            criteria = EmailSearchCriteria(
                query=request.query,
                from_address=request.from_address,
                to_address=request.to_address,
                subject=request.subject,
                has_attachment=request.has_attachment,
                is_unread=request.is_unread,
                label=request.label,
                after_date=request.after_date,
                before_date=request.before_date,
                max_results=request.max_results
            )

            # Search emails
            emails = await client.search_emails(criteria)

            return SearchEmailsResponse(
                success=True,
                emails=emails,
                count=len(emails)
            )

        except Exception as e:
            return SearchEmailsResponse(
                success=False,
                emails=[],
                count=0,
                error=str(e)
            )

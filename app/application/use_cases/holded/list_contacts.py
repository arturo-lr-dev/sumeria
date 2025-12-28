"""
List Contacts use case.
Handles listing contacts from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.contact import Contact


@dataclass
class ListContactsRequest:
    """Request to list contacts."""
    contact_type: Optional[str] = None  # client or supplier
    max_results: int = 100


@dataclass
class ListContactsResponse:
    """Response from listing contacts."""
    success: bool
    contacts: list[Contact] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        if self.contacts is None:
            self.contacts = []


class ListContactsUseCase:
    """Use case for listing contacts."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: ListContactsRequest) -> ListContactsResponse:
        """
        Execute the use case.

        Args:
            request: List contacts request

        Returns:
            Response with contacts or error
        """
        try:
            contacts = await self.client.list_contacts(
                contact_type=request.contact_type,
                max_results=request.max_results
            )

            return ListContactsResponse(
                success=True,
                contacts=contacts,
                count=len(contacts)
            )

        except Exception as e:
            return ListContactsResponse(
                success=False,
                error=str(e)
            )

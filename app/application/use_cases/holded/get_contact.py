"""
Get Contact use case.
Handles retrieving contact details from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.contact import Contact


@dataclass
class GetContactRequest:
    """Request to get a contact."""
    contact_id: str


@dataclass
class GetContactResponse:
    """Response from getting a contact."""
    success: bool
    contact: Optional[Contact] = None
    error: Optional[str] = None


class GetContactUseCase:
    """Use case for getting contact details."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: GetContactRequest) -> GetContactResponse:
        """
        Execute the use case.

        Args:
            request: Get contact request

        Returns:
            Response with contact or error
        """
        try:
            contact = await self.client.get_contact(request.contact_id)

            return GetContactResponse(
                success=True,
                contact=contact
            )

        except Exception as e:
            return GetContactResponse(
                success=False,
                error=str(e)
            )

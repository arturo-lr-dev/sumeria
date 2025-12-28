"""
Create Contact use case.
Handles creating new contacts in Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.contact import ContactDraft, ContactAddress


@dataclass
class CreateContactRequest:
    """Request to create a contact."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    vat_number: Optional[str] = None
    type: str = "client"
    notes: Optional[str] = None
    billing_address: Optional[dict] = None
    shipping_address: Optional[dict] = None
    tags: Optional[list[str]] = None


@dataclass
class CreateContactResponse:
    """Response from creating a contact."""
    success: bool
    contact_id: Optional[str] = None
    error: Optional[str] = None


class CreateContactUseCase:
    """Use case for creating contacts."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: CreateContactRequest) -> CreateContactResponse:
        """
        Execute the use case.

        Args:
            request: Create contact request

        Returns:
            Response with contact ID or error
        """
        try:
            # Parse addresses
            billing_addr = None
            if request.billing_address:
                billing_addr = ContactAddress(**request.billing_address)

            shipping_addr = None
            if request.shipping_address:
                shipping_addr = ContactAddress(**request.shipping_address)

            # Create draft
            draft = ContactDraft(
                name=request.name,
                email=request.email,
                phone=request.phone,
                mobile=request.mobile,
                vat_number=request.vat_number,
                type=request.type,
                notes=request.notes,
                billing_address=billing_addr,
                shipping_address=shipping_addr,
                tags=request.tags
            )

            # Create contact
            contact_id = await self.client.create_contact(draft)

            return CreateContactResponse(
                success=True,
                contact_id=contact_id
            )

        except Exception as e:
            return CreateContactResponse(
                success=False,
                error=str(e)
            )

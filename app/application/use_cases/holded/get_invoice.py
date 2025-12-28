"""
Get Invoice use case.
Handles retrieving invoice details from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.invoice import Invoice


@dataclass
class GetInvoiceRequest:
    """Request to get an invoice."""
    invoice_id: str


@dataclass
class GetInvoiceResponse:
    """Response from getting an invoice."""
    success: bool
    invoice: Optional[Invoice] = None
    error: Optional[str] = None


class GetInvoiceUseCase:
    """Use case for getting invoice details."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: GetInvoiceRequest) -> GetInvoiceResponse:
        """
        Execute the use case.

        Args:
            request: Get invoice request

        Returns:
            Response with invoice or error
        """
        try:
            invoice = await self.client.get_invoice(request.invoice_id)

            return GetInvoiceResponse(
                success=True,
                invoice=invoice
            )

        except Exception as e:
            return GetInvoiceResponse(
                success=False,
                error=str(e)
            )

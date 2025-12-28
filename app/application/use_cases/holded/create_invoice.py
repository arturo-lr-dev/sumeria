"""
Create Invoice use case.
Handles creating new invoices in Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.invoice import InvoiceDraft, InvoiceItem


@dataclass
class CreateInvoiceRequest:
    """Request to create an invoice."""
    contact_id: str
    items: list[dict]
    doc_type: str = "invoice"
    date: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    payment_method: Optional[str] = None


@dataclass
class CreateInvoiceResponse:
    """Response from creating an invoice."""
    success: bool
    invoice_id: Optional[str] = None
    error: Optional[str] = None


class CreateInvoiceUseCase:
    """Use case for creating invoices."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: CreateInvoiceRequest) -> CreateInvoiceResponse:
        """
        Execute the use case.

        Args:
            request: Create invoice request

        Returns:
            Response with invoice ID or error
        """
        try:
            # Convert items
            from datetime import date as date_type
            items = []
            for item_data in request.items:
                items.append(InvoiceItem(
                    name=item_data["name"],
                    description=item_data.get("description"),
                    quantity=item_data.get("quantity", 1.0),
                    price=item_data.get("price", 0.0),
                    tax_rate=item_data.get("tax_rate", 0.0),
                    discount=item_data.get("discount", 0.0),
                    product_id=item_data.get("product_id")
                ))

            # Parse dates
            doc_date = None
            if request.date:
                doc_date = date_type.fromisoformat(request.date)

            due_date = None
            if request.due_date:
                due_date = date_type.fromisoformat(request.due_date)

            # Create draft
            draft = InvoiceDraft(
                contact_id=request.contact_id,
                items=items,
                doc_type=request.doc_type,
                date=doc_date,
                due_date=due_date,
                notes=request.notes,
                tags=request.tags,
                payment_method=request.payment_method
            )

            # Create invoice
            invoice_id = await self.client.create_invoice(draft)

            return CreateInvoiceResponse(
                success=True,
                invoice_id=invoice_id
            )

        except Exception as e:
            return CreateInvoiceResponse(
                success=False,
                error=str(e)
            )

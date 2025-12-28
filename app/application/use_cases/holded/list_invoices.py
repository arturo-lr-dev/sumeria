"""
List Invoices use case.
Handles listing invoices from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.invoice import Invoice, InvoiceSearchCriteria


@dataclass
class ListInvoicesRequest:
    """Request to list invoices."""
    contact_id: Optional[str] = None
    status: Optional[str] = None
    doc_type: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    paid: Optional[bool] = None
    max_results: int = 10


@dataclass
class ListInvoicesResponse:
    """Response from listing invoices."""
    success: bool
    invoices: list[Invoice] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        if self.invoices is None:
            self.invoices = []


class ListInvoicesUseCase:
    """Use case for listing invoices."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: ListInvoicesRequest) -> ListInvoicesResponse:
        """
        Execute the use case.

        Args:
            request: List invoices request

        Returns:
            Response with invoices or error
        """
        try:
            from datetime import date as date_type

            # Parse dates
            from_date = None
            if request.from_date:
                from_date = date_type.fromisoformat(request.from_date)

            to_date = None
            if request.to_date:
                to_date = date_type.fromisoformat(request.to_date)

            # Create criteria
            criteria = InvoiceSearchCriteria(
                contact_id=request.contact_id,
                status=request.status,
                doc_type=request.doc_type,
                from_date=from_date,
                to_date=to_date,
                paid=request.paid,
                max_results=request.max_results
            )

            # List invoices
            invoices = await self.client.list_invoices(criteria)

            return ListInvoicesResponse(
                success=True,
                invoices=invoices,
                count=len(invoices)
            )

        except Exception as e:
            return ListInvoicesResponse(
                success=False,
                error=str(e)
            )

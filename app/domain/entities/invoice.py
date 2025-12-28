"""
Invoice domain entity for Holded integration.
Represents invoices, quotes, and other documents in Holded.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date


@dataclass
class InvoiceItem:
    """Line item in an invoice."""
    name: str
    description: Optional[str] = None
    quantity: float = 1.0
    price: float = 0.0
    tax_rate: float = 0.0
    discount: float = 0.0
    product_id: Optional[str] = None

    def subtotal(self) -> float:
        """Calculate subtotal before tax."""
        base = self.quantity * self.price
        return base - (base * self.discount / 100)

    def total(self) -> float:
        """Calculate total with tax."""
        subtotal = self.subtotal()
        return subtotal + (subtotal * self.tax_rate / 100)


@dataclass
class Invoice:
    """
    Invoice entity representing a document (invoice, quote, etc).
    Maps to Holded documents API.
    """
    id: Optional[str] = None
    doc_type: str = "invoice"  # invoice, quote, proforma, etc.
    number: Optional[str] = None

    # Contact
    contact_id: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None

    # Dates
    date: Optional[date] = None
    due_date: Optional[date] = None

    # Items
    items: list[InvoiceItem] = None

    # Amounts
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0

    # Payment
    paid: bool = False
    paid_amount: float = 0.0
    payment_method: Optional[str] = None

    # Status
    status: str = "draft"  # draft, sent, paid, cancelled

    # Additional info
    notes: Optional[str] = None
    tags: list[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.tags is None:
            self.tags = []

    def calculate_totals(self):
        """Calculate totals from items."""
        self.subtotal = sum(item.subtotal() for item in self.items)
        self.tax_amount = sum(item.total() - item.subtotal() for item in self.items)
        self.total = self.subtotal + self.tax_amount


@dataclass
class InvoiceDraft:
    """Draft for creating a new invoice."""
    contact_id: str
    items: list[InvoiceItem]
    doc_type: str = "invoice"
    date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    payment_method: Optional[str] = None


@dataclass
class InvoiceSearchCriteria:
    """Criteria for searching invoices."""
    contact_id: Optional[str] = None
    status: Optional[str] = None
    doc_type: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    paid: Optional[bool] = None
    max_results: int = 10

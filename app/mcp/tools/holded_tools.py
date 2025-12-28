"""
MCP Tools for Holded operations.
Exposes Holded functionality through the MCP protocol.
"""
from typing import Optional
from pydantic import BaseModel

from app.application.use_cases.holded.create_invoice import (
    CreateInvoiceUseCase,
    CreateInvoiceRequest
)
from app.application.use_cases.holded.get_invoice import (
    GetInvoiceUseCase,
    GetInvoiceRequest
)
from app.application.use_cases.holded.list_invoices import (
    ListInvoicesUseCase,
    ListInvoicesRequest
)
from app.application.use_cases.holded.create_contact import (
    CreateContactUseCase,
    CreateContactRequest
)
from app.application.use_cases.holded.get_contact import (
    GetContactUseCase,
    GetContactRequest
)
from app.application.use_cases.holded.list_contacts import (
    ListContactsUseCase,
    ListContactsRequest
)
from app.application.use_cases.holded.list_products import (
    ListProductsUseCase,
    ListProductsRequest
)


# Response models for structured output
class InvoiceSummary(BaseModel):
    """Summary of an invoice for display."""
    id: str
    doc_type: str
    number: Optional[str] = None
    contact_name: Optional[str] = None
    date: Optional[str] = None
    total: float
    paid: bool
    status: str


class CreateInvoiceResult(BaseModel):
    """Result of creating an invoice."""
    success: bool
    invoice_id: Optional[str] = None
    error: Optional[str] = None


class ListInvoicesResult(BaseModel):
    """Result of listing invoices."""
    success: bool
    count: int
    invoices: list[InvoiceSummary]
    error: Optional[str] = None


class InvoiceDetail(BaseModel):
    """Detailed invoice information."""
    id: str
    doc_type: str
    number: Optional[str] = None
    contact_id: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: float
    tax_amount: float
    total: float
    paid: bool
    paid_amount: float
    status: str
    items: list[dict]
    notes: Optional[str] = None


class GetInvoiceResult(BaseModel):
    """Result of getting invoice details."""
    success: bool
    invoice: Optional[InvoiceDetail] = None
    error: Optional[str] = None


class ContactSummary(BaseModel):
    """Summary of a contact for display."""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    type: str
    vat_number: Optional[str] = None


class CreateContactResult(BaseModel):
    """Result of creating a contact."""
    success: bool
    contact_id: Optional[str] = None
    error: Optional[str] = None


class ListContactsResult(BaseModel):
    """Result of listing contacts."""
    success: bool
    count: int
    contacts: list[ContactSummary]
    error: Optional[str] = None


class ContactDetail(BaseModel):
    """Detailed contact information."""
    id: str
    name: str
    code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    vat_number: Optional[str] = None
    type: str
    notes: Optional[str] = None
    billing_address: Optional[dict] = None
    shipping_address: Optional[dict] = None


class GetContactResult(BaseModel):
    """Result of getting contact details."""
    success: bool
    contact: Optional[ContactDetail] = None
    error: Optional[str] = None


class ProductSummary(BaseModel):
    """Summary of a product for display."""
    id: str
    name: str
    code: Optional[str] = None
    price: float
    tax_rate: float
    type: str
    active: bool


class ListProductsResult(BaseModel):
    """Result of listing products."""
    success: bool
    count: int
    products: list[ProductSummary]
    error: Optional[str] = None


class HoldedTools:
    """Collection of Holded MCP tools."""

    def __init__(self):
        """Initialize use cases."""
        self.create_invoice_uc = CreateInvoiceUseCase()
        self.get_invoice_uc = GetInvoiceUseCase()
        self.list_invoices_uc = ListInvoicesUseCase()
        self.create_contact_uc = CreateContactUseCase()
        self.get_contact_uc = GetContactUseCase()
        self.list_contacts_uc = ListContactsUseCase()
        self.list_products_uc = ListProductsUseCase()

    async def create_invoice(
        self,
        contact_id: str,
        items: list[dict],
        doc_type: str = "invoice",
        date: Optional[str] = None,
        due_date: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[list[str]] = None,
        payment_method: Optional[str] = None
    ) -> CreateInvoiceResult:
        """
        Create a new invoice in Holded.

        Args:
            contact_id: Contact ID (customer or supplier)
            items: List of invoice items with keys: name, description, quantity, price, tax_rate, discount, product_id
            doc_type: Document type (invoice, quote, proforma, etc.)
            date: Invoice date (ISO format: YYYY-MM-DD)
            due_date: Due date (ISO format: YYYY-MM-DD)
            notes: Additional notes
            tags: List of tags
            payment_method: Payment method

        Returns:
            CreateInvoiceResult with success status and invoice ID
        """
        request = CreateInvoiceRequest(
            contact_id=contact_id,
            items=items,
            doc_type=doc_type,
            date=date,
            due_date=due_date,
            notes=notes,
            tags=tags,
            payment_method=payment_method
        )

        response = await self.create_invoice_uc.execute(request)

        return CreateInvoiceResult(
            success=response.success,
            invoice_id=response.invoice_id,
            error=response.error
        )

    async def get_invoice(self, invoice_id: str) -> GetInvoiceResult:
        """
        Get detailed information about a specific invoice.

        Args:
            invoice_id: Holded invoice ID

        Returns:
            GetInvoiceResult with complete invoice details
        """
        request = GetInvoiceRequest(invoice_id=invoice_id)

        response = await self.get_invoice_uc.execute(request)

        if not response.success or not response.invoice:
            return GetInvoiceResult(
                success=False,
                error=response.error
            )

        invoice = response.invoice

        # Convert to detail model
        invoice_detail = InvoiceDetail(
            id=invoice.id or "",
            doc_type=invoice.doc_type,
            number=invoice.number,
            contact_id=invoice.contact_id,
            contact_name=invoice.contact_name,
            contact_email=invoice.contact_email,
            date=invoice.date.isoformat() if invoice.date else None,
            due_date=invoice.due_date.isoformat() if invoice.due_date else None,
            subtotal=invoice.subtotal,
            tax_amount=invoice.tax_amount,
            total=invoice.total,
            paid=invoice.paid,
            paid_amount=invoice.paid_amount,
            status=invoice.status,
            items=[
                {
                    "name": item.name,
                    "description": item.description,
                    "quantity": item.quantity,
                    "price": item.price,
                    "tax_rate": item.tax_rate,
                    "discount": item.discount,
                    "subtotal": item.subtotal(),
                    "total": item.total()
                }
                for item in invoice.items
            ],
            notes=invoice.notes
        )

        return GetInvoiceResult(
            success=True,
            invoice=invoice_detail
        )

    async def list_invoices(
        self,
        contact_id: Optional[str] = None,
        status: Optional[str] = None,
        doc_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        paid: Optional[bool] = None,
        max_results: int = 10
    ) -> ListInvoicesResult:
        """
        List invoices from Holded.

        Args:
            contact_id: Filter by contact ID
            status: Filter by status (draft, sent, paid, cancelled)
            doc_type: Filter by document type (invoice, quote, proforma, etc.)
            from_date: Filter by date from (ISO format: YYYY-MM-DD)
            to_date: Filter by date to (ISO format: YYYY-MM-DD)
            paid: Filter by paid status
            max_results: Maximum number of results (default: 10, max: 100)

        Returns:
            ListInvoicesResult with matching invoices
        """
        request = ListInvoicesRequest(
            contact_id=contact_id,
            status=status,
            doc_type=doc_type,
            from_date=from_date,
            to_date=to_date,
            paid=paid,
            max_results=min(max_results, 100)
        )

        response = await self.list_invoices_uc.execute(request)

        # Convert to summaries
        invoices = [
            InvoiceSummary(
                id=invoice.id or "",
                doc_type=invoice.doc_type,
                number=invoice.number,
                contact_name=invoice.contact_name,
                date=invoice.date.isoformat() if invoice.date else None,
                total=invoice.total,
                paid=invoice.paid,
                status=invoice.status
            )
            for invoice in response.invoices
        ]

        return ListInvoicesResult(
            success=response.success,
            count=response.count,
            invoices=invoices,
            error=response.error
        )

    async def create_contact(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        mobile: Optional[str] = None,
        vat_number: Optional[str] = None,
        type: str = "client",
        notes: Optional[str] = None,
        billing_address: Optional[dict] = None,
        shipping_address: Optional[dict] = None,
        tags: Optional[list[str]] = None
    ) -> CreateContactResult:
        """
        Create a new contact in Holded.

        Args:
            name: Contact name (required)
            email: Contact email
            phone: Contact phone
            mobile: Contact mobile
            vat_number: VAT/Tax number
            type: Contact type (client or supplier)
            notes: Additional notes
            billing_address: Billing address dict with keys: street, city, province, postal_code, country
            shipping_address: Shipping address dict with keys: street, city, province, postal_code, country
            tags: List of tags

        Returns:
            CreateContactResult with success status and contact ID
        """
        request = CreateContactRequest(
            name=name,
            email=email,
            phone=phone,
            mobile=mobile,
            vat_number=vat_number,
            type=type,
            notes=notes,
            billing_address=billing_address,
            shipping_address=shipping_address,
            tags=tags
        )

        response = await self.create_contact_uc.execute(request)

        return CreateContactResult(
            success=response.success,
            contact_id=response.contact_id,
            error=response.error
        )

    async def get_contact(self, contact_id: str) -> GetContactResult:
        """
        Get detailed information about a specific contact.

        Args:
            contact_id: Holded contact ID

        Returns:
            GetContactResult with complete contact details
        """
        request = GetContactRequest(contact_id=contact_id)

        response = await self.get_contact_uc.execute(request)

        if not response.success or not response.contact:
            return GetContactResult(
                success=False,
                error=response.error
            )

        contact = response.contact

        # Convert addresses to dict
        billing_addr = None
        if contact.billing_address:
            billing_addr = {
                "street": contact.billing_address.street,
                "city": contact.billing_address.city,
                "province": contact.billing_address.province,
                "postal_code": contact.billing_address.postal_code,
                "country": contact.billing_address.country
            }

        shipping_addr = None
        if contact.shipping_address:
            shipping_addr = {
                "street": contact.shipping_address.street,
                "city": contact.shipping_address.city,
                "province": contact.shipping_address.province,
                "postal_code": contact.shipping_address.postal_code,
                "country": contact.shipping_address.country
            }

        # Convert to detail model
        contact_detail = ContactDetail(
            id=contact.id or "",
            name=contact.name,
            code=contact.code,
            email=contact.email,
            phone=contact.phone,
            mobile=contact.mobile,
            vat_number=contact.vat_number,
            type=contact.type,
            notes=contact.notes,
            billing_address=billing_addr,
            shipping_address=shipping_addr
        )

        return GetContactResult(
            success=True,
            contact=contact_detail
        )

    async def list_contacts(
        self,
        contact_type: Optional[str] = None,
        max_results: int = 100
    ) -> ListContactsResult:
        """
        List contacts from Holded.

        Args:
            contact_type: Filter by type (client or supplier)
            max_results: Maximum number of results (default: 100)

        Returns:
            ListContactsResult with matching contacts
        """
        request = ListContactsRequest(
            contact_type=contact_type,
            max_results=max_results
        )

        response = await self.list_contacts_uc.execute(request)

        # Convert to summaries
        contacts = [
            ContactSummary(
                id=contact.id or "",
                name=contact.name,
                email=contact.email,
                phone=contact.phone,
                type=contact.type,
                vat_number=contact.vat_number
            )
            for contact in response.contacts
        ]

        return ListContactsResult(
            success=response.success,
            count=response.count,
            contacts=contacts,
            error=response.error
        )

    async def list_products(
        self,
        active_only: bool = True,
        max_results: int = 100
    ) -> ListProductsResult:
        """
        List products from Holded.

        Args:
            active_only: Only return active products (default: True)
            max_results: Maximum number of results (default: 100)

        Returns:
            ListProductsResult with matching products
        """
        request = ListProductsRequest(
            active_only=active_only,
            max_results=max_results
        )

        response = await self.list_products_uc.execute(request)

        # Convert to summaries
        products = [
            ProductSummary(
                id=product.id or "",
                name=product.name,
                code=product.code,
                price=product.price,
                tax_rate=product.tax_rate or 0.0,
                type=product.type,
                active=product.active
            )
            for product in response.products
        ]

        return ListProductsResult(
            success=response.success,
            count=response.count,
            products=products,
            error=response.error
        )


# Global instance
holded_tools = HoldedTools()

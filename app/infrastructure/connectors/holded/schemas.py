"""
Holded API schemas and mappers.
Converts between Holded API format and domain entities.
"""
from datetime import datetime, date
from typing import Any, Optional

from app.domain.entities.invoice import Invoice, InvoiceItem, InvoiceDraft
from app.domain.entities.contact import Contact, ContactAddress, ContactDraft
from app.domain.entities.product import Product


class HoldedMapper:
    """Maps between Holded API responses and domain entities."""

    # ============ Invoice Mapping ============

    @staticmethod
    def to_invoice_entity(data: dict[str, Any]) -> Invoice:
        """
        Convert Holded invoice data to Invoice entity.

        Args:
            data: Holded API response data

        Returns:
            Invoice entity
        """
        # Parse items
        items = []
        for item_data in data.get("items", []):
            items.append(InvoiceItem(
                name=item_data.get("name", ""),
                description=item_data.get("desc", ""),
                quantity=float(item_data.get("units", 1)),
                price=float(item_data.get("price", 0)),
                tax_rate=float(item_data.get("tax", 0)),
                discount=float(item_data.get("discount", 0)),
                product_id=item_data.get("productId")
            ))

        # Parse dates
        doc_date = None
        if data.get("date"):
            doc_date = datetime.fromtimestamp(data["date"]).date()

        due_date = None
        if data.get("dueDate"):
            due_date = datetime.fromtimestamp(data["dueDate"]).date()

        created_at = None
        if data.get("createdAt"):
            created_at = datetime.fromtimestamp(data["createdAt"])

        invoice = Invoice(
            id=data.get("id"),
            doc_type=data.get("docType", "invoice"),
            number=data.get("number"),
            contact_id=data.get("contactId"),
            contact_name=data.get("contactName"),
            contact_email=data.get("contactEmail"),
            date=doc_date,
            due_date=due_date,
            items=items,
            subtotal=float(data.get("subtotal", 0)),
            tax_amount=float(data.get("tax", 0)),
            total=float(data.get("total", 0)),
            paid=data.get("paid", False),
            paid_amount=float(data.get("paidAmount", 0)),
            payment_method=data.get("paymentMethod"),
            status=data.get("status", "draft"),
            notes=data.get("notes"),
            tags=data.get("tags", []),
            created_at=created_at
        )

        return invoice

    @staticmethod
    def from_invoice_draft(draft: InvoiceDraft) -> dict[str, Any]:
        """
        Convert InvoiceDraft to Holded API format.

        Args:
            draft: Invoice draft

        Returns:
            Data for Holded API
        """
        items = []
        for item in draft.items:
            items.append({
                "name": item.name,
                "desc": item.description or "",
                "units": item.quantity,
                "price": item.price,
                "tax": item.tax_rate,
                "discount": item.discount,
                "productId": item.product_id
            })

        data = {
            "contactId": draft.contact_id,
            "docType": draft.doc_type,
            "items": items
        }

        if draft.date:
            data["date"] = int(draft.date.strftime("%s"))

        if draft.due_date:
            data["dueDate"] = int(draft.due_date.strftime("%s"))

        if draft.notes:
            data["notes"] = draft.notes

        if draft.tags:
            data["tags"] = draft.tags

        if draft.payment_method:
            data["paymentMethod"] = draft.payment_method

        return data

    # ============ Contact Mapping ============

    @staticmethod
    def to_contact_entity(data: dict[str, Any]) -> Contact:
        """
        Convert Holded contact data to Contact entity.

        Args:
            data: Holded API response data

        Returns:
            Contact entity
        """
        # Parse addresses
        billing_address = None
        if data.get("billAddress"):
            addr = data["billAddress"]
            billing_address = ContactAddress(
                street=addr.get("address"),
                city=addr.get("city"),
                province=addr.get("province"),
                postal_code=addr.get("postalCode"),
                country=addr.get("country")
            )

        shipping_address = None
        if data.get("shipAddress"):
            addr = data["shipAddress"]
            shipping_address = ContactAddress(
                street=addr.get("address"),
                city=addr.get("city"),
                province=addr.get("province"),
                postal_code=addr.get("postalCode"),
                country=addr.get("country")
            )

        # Parse timestamps
        created_at = None
        if data.get("createdAt"):
            created_at = datetime.fromtimestamp(data["createdAt"])

        updated_at = None
        if data.get("updatedAt"):
            updated_at = datetime.fromtimestamp(data["updatedAt"])

        contact = Contact(
            id=data.get("id"),
            name=data.get("name", ""),
            code=data.get("code"),
            email=data.get("email"),
            phone=data.get("phone"),
            mobile=data.get("mobile"),
            vat_number=data.get("vatNumber"),
            billing_address=billing_address,
            shipping_address=shipping_address,
            type=data.get("type", "client"),
            notes=data.get("notes"),
            tags=data.get("tags", []),
            created_at=created_at,
            updated_at=updated_at
        )

        return contact

    @staticmethod
    def from_contact_draft(draft: ContactDraft) -> dict[str, Any]:
        """
        Convert ContactDraft to Holded API format.

        Args:
            draft: Contact draft

        Returns:
            Data for Holded API
        """
        data = {
            "name": draft.name,
            "type": draft.type
        }

        if draft.email:
            data["email"] = draft.email

        if draft.phone:
            data["phone"] = draft.phone

        if draft.mobile:
            data["mobile"] = draft.mobile

        if draft.vat_number:
            data["vatNumber"] = draft.vat_number

        if draft.notes:
            data["notes"] = draft.notes

        if draft.tags:
            data["tags"] = draft.tags

        if draft.billing_address:
            data["billAddress"] = {
                "address": draft.billing_address.street,
                "city": draft.billing_address.city,
                "province": draft.billing_address.province,
                "postalCode": draft.billing_address.postal_code,
                "country": draft.billing_address.country
            }

        if draft.shipping_address:
            data["shipAddress"] = {
                "address": draft.shipping_address.street,
                "city": draft.shipping_address.city,
                "province": draft.shipping_address.province,
                "postalCode": draft.shipping_address.postal_code,
                "country": draft.shipping_address.country
            }

        return data

    # ============ Product Mapping ============

    @staticmethod
    def to_product_entity(data: dict[str, Any]) -> Product:
        """
        Convert Holded product data to Product entity.

        Args:
            data: Holded API response data

        Returns:
            Product entity
        """
        created_at = None
        if data.get("createdAt"):
            created_at = datetime.fromtimestamp(data["createdAt"])

        updated_at = None
        if data.get("updatedAt"):
            updated_at = datetime.fromtimestamp(data["updatedAt"])

        product = Product(
            id=data.get("id"),
            name=data.get("name", ""),
            code=data.get("code"),
            description=data.get("desc"),
            price=float(data.get("price", 0)),
            cost=float(data.get("cost", 0)) if data.get("cost") else None,
            tax_rate=float(data.get("tax", 0)),
            type=data.get("type", "product"),
            stock=data.get("stock"),
            track_stock=data.get("trackStock", False),
            active=data.get("active", True),
            category=data.get("category"),
            tags=data.get("tags", []),
            created_at=created_at,
            updated_at=updated_at
        )

        return product

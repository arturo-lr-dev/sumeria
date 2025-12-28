"""
Unit tests for Holded schemas and mappers.
"""
import pytest
from datetime import datetime, date

from app.infrastructure.connectors.holded.schemas import HoldedMapper
from app.domain.entities.invoice import InvoiceDraft, InvoiceItem
from app.domain.entities.contact import ContactDraft, ContactAddress


def test_invoice_entity_mapping():
    """Test mapping Holded invoice data to Invoice entity."""
    # Arrange
    holded_data = {
        "id": "invoice123",
        "docType": "invoice",
        "number": "INV-001",
        "contactId": "contact123",
        "contactName": "Test Customer",
        "contactEmail": "test@example.com",
        "items": [
            {
                "name": "Test Item",
                "desc": "Test Description",
                "units": 2,
                "price": 50.0,
                "tax": 21.0,
                "discount": 0
            }
        ],
        "subtotal": 100.0,
        "tax": 21.0,
        "total": 121.0,
        "paid": False,
        "status": "draft"
    }

    # Act
    invoice = HoldedMapper.to_invoice_entity(holded_data)

    # Assert
    assert invoice.id == "invoice123"
    assert invoice.doc_type == "invoice"
    assert invoice.number == "INV-001"
    assert invoice.contact_name == "Test Customer"
    assert len(invoice.items) == 1
    assert invoice.items[0].name == "Test Item"
    assert invoice.total == 121.0


def test_invoice_draft_mapping():
    """Test mapping InvoiceDraft to Holded format."""
    # Arrange
    draft = InvoiceDraft(
        contact_id="contact123",
        items=[
            InvoiceItem(
                name="Test Item",
                description="Test Description",
                quantity=2,
                price=50.0,
                tax_rate=21.0
            )
        ],
        doc_type="invoice",
        notes="Test notes"
    )

    # Act
    holded_data = HoldedMapper.from_invoice_draft(draft)

    # Assert
    assert holded_data["contactId"] == "contact123"
    assert holded_data["docType"] == "invoice"
    assert len(holded_data["items"]) == 1
    assert holded_data["items"][0]["name"] == "Test Item"
    assert holded_data["items"][0]["units"] == 2
    assert holded_data["notes"] == "Test notes"


def test_contact_entity_mapping():
    """Test mapping Holded contact data to Contact entity."""
    # Arrange
    holded_data = {
        "id": "contact123",
        "name": "Test Customer",
        "email": "test@example.com",
        "phone": "+1234567890",
        "type": "client",
        "vatNumber": "ESB12345678",
        "billAddress": {
            "address": "123 Main St",
            "city": "Madrid",
            "province": "Madrid",
            "postalCode": "28001",
            "country": "Spain"
        }
    }

    # Act
    contact = HoldedMapper.to_contact_entity(holded_data)

    # Assert
    assert contact.id == "contact123"
    assert contact.name == "Test Customer"
    assert contact.email == "test@example.com"
    assert contact.vat_number == "ESB12345678"
    assert contact.billing_address is not None
    assert contact.billing_address.city == "Madrid"


def test_contact_draft_mapping():
    """Test mapping ContactDraft to Holded format."""
    # Arrange
    draft = ContactDraft(
        name="Test Customer",
        email="test@example.com",
        phone="+1234567890",
        type="client",
        vat_number="ESB12345678",
        billing_address=ContactAddress(
            street="123 Main St",
            city="Madrid",
            postal_code="28001",
            country="Spain"
        )
    )

    # Act
    holded_data = HoldedMapper.from_contact_draft(draft)

    # Assert
    assert holded_data["name"] == "Test Customer"
    assert holded_data["email"] == "test@example.com"
    assert holded_data["type"] == "client"
    assert holded_data["vatNumber"] == "ESB12345678"
    assert holded_data["billAddress"]["city"] == "Madrid"


def test_product_entity_mapping():
    """Test mapping Holded product data to Product entity."""
    # Arrange
    holded_data = {
        "id": "product123",
        "name": "Test Product",
        "code": "PROD-001",
        "desc": "Test Description",
        "price": 100.0,
        "tax": 21.0,
        "type": "product",
        "active": True
    }

    # Act
    product = HoldedMapper.to_product_entity(holded_data)

    # Assert
    assert product.id == "product123"
    assert product.name == "Test Product"
    assert product.code == "PROD-001"
    assert product.price == 100.0
    assert product.tax_rate == 21.0
    assert product.active is True

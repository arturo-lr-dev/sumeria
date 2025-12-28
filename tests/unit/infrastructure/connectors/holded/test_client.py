"""
Unit tests for Holded client.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.invoice import InvoiceDraft, InvoiceItem
from app.domain.entities.contact import ContactDraft


@pytest.fixture
def holded_client():
    """Create a Holded client with mocked API key."""
    with patch('app.infrastructure.connectors.holded.client.settings') as mock_settings:
        mock_settings.holded_api_key = "test_api_key"
        mock_settings.holded_api_base_url = "https://api.holded.com"
        return HoldedClient()


@pytest.mark.asyncio
async def test_create_invoice_success(holded_client):
    """Test creating an invoice successfully."""
    # Arrange
    draft = InvoiceDraft(
        contact_id="contact123",
        items=[
            InvoiceItem(name="Test Item", quantity=1, price=100.0, tax_rate=21.0)
        ],
        doc_type="invoice"
    )

    mock_response = {"id": "invoice123"}

    # Act
    with patch.object(holded_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await holded_client.create_invoice(draft)

    # Assert
    assert result == "invoice123"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_get_invoice_success(holded_client):
    """Test getting an invoice successfully."""
    # Arrange
    invoice_id = "invoice123"
    mock_response = {
        "id": invoice_id,
        "docType": "invoice",
        "number": "INV-001",
        "contactId": "contact123",
        "contactName": "Test Customer",
        "items": [],
        "subtotal": 100.0,
        "tax": 21.0,
        "total": 121.0,
        "paid": False,
        "status": "draft"
    }

    # Act
    with patch.object(holded_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await holded_client.get_invoice(invoice_id)

    # Assert
    assert result.id == invoice_id
    assert result.doc_type == "invoice"
    assert result.total == 121.0


@pytest.mark.asyncio
async def test_create_contact_success(holded_client):
    """Test creating a contact successfully."""
    # Arrange
    draft = ContactDraft(
        name="Test Customer",
        email="test@example.com",
        type="client"
    )

    mock_response = {"id": "contact123"}

    # Act
    with patch.object(holded_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await holded_client.create_contact(draft)

    # Assert
    assert result == "contact123"
    mock_request.assert_called_once()


@pytest.mark.asyncio
async def test_list_contacts_success(holded_client):
    """Test listing contacts successfully."""
    # Arrange
    mock_response = [
        {
            "id": "contact1",
            "name": "Customer 1",
            "type": "client",
            "email": "customer1@example.com"
        },
        {
            "id": "contact2",
            "name": "Customer 2",
            "type": "client",
            "email": "customer2@example.com"
        }
    ]

    # Act
    with patch.object(holded_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await holded_client.list_contacts(contact_type="client")

    # Assert
    assert len(result) == 2
    assert result[0].name == "Customer 1"
    assert result[1].name == "Customer 2"


@pytest.mark.asyncio
async def test_list_products_success(holded_client):
    """Test listing products successfully."""
    # Arrange
    mock_response = [
        {
            "id": "product1",
            "name": "Product 1",
            "price": 100.0,
            "tax": 21.0,
            "type": "product",
            "active": True
        }
    ]

    # Act
    with patch.object(holded_client, '_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        result = await holded_client.list_products()

    # Assert
    assert len(result) == 1
    assert result[0].name == "Product 1"
    assert result[0].price == 100.0

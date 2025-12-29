"""
Unit tests for CreateInvoice use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.create_invoice import (
    CreateInvoiceUseCase,
    CreateInvoiceRequest,
    CreateInvoiceResponse
)


class TestCreateInvoiceUseCase:
    """Test suite for CreateInvoice use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Holded client."""
        client = MagicMock()
        client.create_invoice = AsyncMock(return_value="invoice123")
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return CreateInvoiceUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_create_invoice_basic(self, use_case, mock_client):
        """Test creating a basic invoice."""
        request = CreateInvoiceRequest(
            contact_id="contact123",
            items=[
                {
                    "name": "Product 1",
                    "quantity": 2,
                    "price": 100.0
                }
            ]
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.invoice_id == "invoice123"
        assert response.error is None
        mock_client.create_invoice.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_invoice_with_multiple_items(self, use_case, mock_client):
        """Test creating invoice with multiple items."""
        request = CreateInvoiceRequest(
            contact_id="contact123",
            items=[
                {
                    "name": "Product 1",
                    "description": "First product",
                    "quantity": 2,
                    "price": 100.0,
                    "tax_rate": 21.0
                },
                {
                    "name": "Product 2",
                    "quantity": 1,
                    "price": 50.0,
                    "discount": 10.0
                }
            ]
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_invoice.call_args[0][0]
        assert len(draft.items) == 2
        assert draft.items[0].name == "Product 1"
        assert draft.items[0].tax_rate == 21.0
        assert draft.items[1].discount == 10.0

    @pytest.mark.asyncio
    async def test_create_invoice_with_dates(self, use_case, mock_client):
        """Test creating invoice with dates."""
        request = CreateInvoiceRequest(
            contact_id="contact123",
            items=[{"name": "Service", "price": 200.0}],
            date="2025-01-15",
            due_date="2025-02-15"
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_invoice.call_args[0][0]
        assert draft.date is not None
        assert draft.due_date is not None

    @pytest.mark.asyncio
    async def test_create_invoice_with_metadata(self, use_case, mock_client):
        """Test creating invoice with notes and tags."""
        request = CreateInvoiceRequest(
            contact_id="contact123",
            items=[{"name": "Consulting", "price": 1000.0}],
            notes="Monthly consulting services",
            tags=["consulting", "monthly"],
            payment_method="bank_transfer"
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_invoice.call_args[0][0]
        assert draft.notes == "Monthly consulting services"
        assert draft.tags == ["consulting", "monthly"]
        assert draft.payment_method == "bank_transfer"

    @pytest.mark.asyncio
    async def test_create_invoice_failure(self, use_case, mock_client):
        """Test invoice creation failure."""
        mock_client.create_invoice.side_effect = Exception("API error")

        request = CreateInvoiceRequest(
            contact_id="contact123",
            items=[{"name": "Product", "price": 100.0}]
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert response.invoice_id is None
        assert "API error" in response.error

    @pytest.mark.asyncio
    async def test_create_invoice_default_values(self, use_case, mock_client):
        """Test invoice creation with default values."""
        request = CreateInvoiceRequest(
            contact_id="contact123",
            items=[{"name": "Product"}]
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_invoice.call_args[0][0]
        assert draft.items[0].quantity == 1.0
        assert draft.items[0].price == 0.0
        assert draft.items[0].tax_rate == 0.0

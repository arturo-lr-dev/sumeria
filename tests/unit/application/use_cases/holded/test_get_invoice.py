"""
Unit tests for GetInvoice use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.get_invoice import (
    GetInvoiceUseCase,
    GetInvoiceRequest,
    GetInvoiceResponse
)
from app.domain.entities.invoice import Invoice


class TestGetInvoiceUseCase:
    """Test suite for GetInvoice use case."""

    @pytest.fixture
    def mock_invoice(self):
        """Create mock invoice."""
        return Invoice(
            id="invoice123",
            number="INV-001",
            contact_id="contact123",
            status="paid",
            total=1000.0
        )

    @pytest.fixture
    def mock_client(self, mock_invoice):
        """Create mock Holded client."""
        client = MagicMock()
        client.get_invoice = AsyncMock(return_value=mock_invoice)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return GetInvoiceUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_invoice_success(self, use_case, mock_client, mock_invoice):
        """Test successful invoice retrieval."""
        request = GetInvoiceRequest(invoice_id="invoice123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.invoice == mock_invoice
        assert response.error is None
        mock_client.get_invoice.assert_called_once_with("invoice123")

    @pytest.mark.asyncio
    async def test_get_invoice_not_found(self, use_case, mock_client):
        """Test invoice not found."""
        mock_client.get_invoice.return_value = None

        request = GetInvoiceRequest(invoice_id="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.invoice is None

    @pytest.mark.asyncio
    async def test_get_invoice_failure(self, use_case, mock_client):
        """Test invoice retrieval failure."""
        mock_client.get_invoice.side_effect = Exception("API error")

        request = GetInvoiceRequest(invoice_id="invoice123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.invoice is None
        assert "API error" in response.error

"""
Unit tests for ListInvoices use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.list_invoices import (
    ListInvoicesUseCase,
    ListInvoicesRequest,
    ListInvoicesResponse
)
from app.domain.entities.invoice import Invoice


class TestListInvoicesUseCase:
    """Test suite for ListInvoices use case."""

    @pytest.fixture
    def mock_invoices(self):
        """Create mock invoices."""
        return [
            Invoice(
                id="1",
                number="INV-001",
                contact_id="contact1",
                status="paid",
                total=1000.0
            ),
            Invoice(
                id="2",
                number="INV-002",
                contact_id="contact2",
                status="pending",
                total=500.0
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_invoices):
        """Create mock Holded client."""
        client = MagicMock()
        client.list_invoices = AsyncMock(return_value=mock_invoices)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return ListInvoicesUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_list_invoices_success(self, use_case, mock_client, mock_invoices):
        """Test successful invoice listing."""
        request = ListInvoicesRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.invoices) == 2
        assert response.error is None
        mock_client.list_invoices.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_invoices_with_filters(self, use_case, mock_client):
        """Test listing invoices with filters."""
        request = ListInvoicesRequest(
            contact_id="contact123",
            status="paid",
            max_results=50
        )

        await use_case.execute(request)

        mock_client.list_invoices.assert_called_once()
        criteria = mock_client.list_invoices.call_args[0][0]
        assert criteria.contact_id == "contact123"
        assert criteria.status == "paid"
        assert criteria.max_results == 50

    @pytest.mark.asyncio
    async def test_list_invoices_empty_results(self, use_case, mock_client):
        """Test listing with no invoices."""
        mock_client.list_invoices = AsyncMock(return_value=[])

        request = ListInvoicesRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.invoices) == 0

    @pytest.mark.asyncio
    async def test_list_invoices_failure(self, use_case, mock_client):
        """Test invoice listing failure."""
        mock_client.list_invoices.side_effect = Exception("Network error")

        request = ListInvoicesRequest()

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "Network error" in response.error

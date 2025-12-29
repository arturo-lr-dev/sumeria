"""
Unit tests for CreateContact use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.create_contact import (
    CreateContactUseCase,
    CreateContactRequest,
    CreateContactResponse
)


class TestCreateContactUseCase:
    """Test suite for CreateContact use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Holded client."""
        client = MagicMock()
        client.create_contact = AsyncMock(return_value="contact123")
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return CreateContactUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_create_contact_basic(self, use_case, mock_client):
        """Test creating a basic contact."""
        request = CreateContactRequest(
            name="John Doe",
            email="john@example.com"
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.contact_id == "contact123"
        assert response.error is None
        mock_client.create_contact.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_contact_with_full_data(self, use_case, mock_client):
        """Test creating contact with all fields."""
        request = CreateContactRequest(
            name="Jane Smith",
            email="jane@example.com",
            phone="+1234567890",
            mobile="+0987654321",
            vat_number="VAT123456",
            type="supplier",
            notes="Important supplier",
            tags=["vip", "supplier"]
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.contact_id == "contact123"

        draft = mock_client.create_contact.call_args[0][0]
        assert draft.name == "Jane Smith"
        assert draft.email == "jane@example.com"
        assert draft.type == "supplier"
        assert draft.tags == ["vip", "supplier"]

    @pytest.mark.asyncio
    async def test_create_contact_with_addresses(self, use_case, mock_client):
        """Test creating contact with billing and shipping addresses."""
        request = CreateContactRequest(
            name="ACME Corp",
            email="contact@acme.com",
            billing_address={
                "street": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "country": "US"
            },
            shipping_address={
                "street": "456 Warehouse Ave",
                "city": "Brooklyn",
                "postal_code": "11201",
                "country": "US"
            }
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_contact.call_args[0][0]
        assert draft.billing_address is not None
        assert draft.billing_address.city == "New York"
        assert draft.shipping_address is not None
        assert draft.shipping_address.city == "Brooklyn"

    @pytest.mark.asyncio
    async def test_create_contact_failure(self, use_case, mock_client):
        """Test contact creation failure."""
        mock_client.create_contact.side_effect = Exception("API error")

        request = CreateContactRequest(name="Test User")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.contact_id is None
        assert "API error" in response.error

    @pytest.mark.asyncio
    async def test_create_contact_client_type(self, use_case, mock_client):
        """Test creating client type contact (default)."""
        request = CreateContactRequest(
            name="Client Corp",
            type="client"
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_contact.call_args[0][0]
        assert draft.type == "client"

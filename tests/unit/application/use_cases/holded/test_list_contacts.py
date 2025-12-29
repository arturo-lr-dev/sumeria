"""
Unit tests for ListContacts use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.list_contacts import (
    ListContactsUseCase,
    ListContactsRequest,
    ListContactsResponse
)
from app.domain.entities.contact import Contact


class TestListContactsUseCase:
    """Test suite for ListContacts use case."""

    @pytest.fixture
    def mock_contacts(self):
        """Create mock contacts."""
        return [
            Contact(
                id="1",
                name="Contact 1",
                email="contact1@example.com",
                type="client"
            ),
            Contact(
                id="2",
                name="Contact 2",
                email="contact2@example.com",
                type="supplier"
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_contacts):
        """Create mock Holded client."""
        client = MagicMock()
        client.list_contacts = AsyncMock(return_value=mock_contacts)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return ListContactsUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_list_contacts_success(self, use_case, mock_client, mock_contacts):
        """Test successful contact listing."""
        request = ListContactsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.contacts) == 2
        assert response.error is None
        mock_client.list_contacts.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_contacts_with_type_filter(self, use_case, mock_client):
        """Test listing contacts with type filter."""
        request = ListContactsRequest(contact_type="client")

        await use_case.execute(request)

        mock_client.list_contacts.assert_called_once_with(
            contact_type="client",
            max_results=100
        )

    @pytest.mark.asyncio
    async def test_list_contacts_with_max_results(self, use_case, mock_client):
        """Test listing contacts with max results."""
        request = ListContactsRequest(max_results=50)

        await use_case.execute(request)

        mock_client.list_contacts.assert_called_once_with(
            contact_type=None,
            max_results=50
        )

    @pytest.mark.asyncio
    async def test_list_contacts_empty_results(self, use_case, mock_client):
        """Test listing with no contacts."""
        mock_client.list_contacts = AsyncMock(return_value=[])

        request = ListContactsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.contacts) == 0

    @pytest.mark.asyncio
    async def test_list_contacts_failure(self, use_case, mock_client):
        """Test contact listing failure."""
        mock_client.list_contacts.side_effect = Exception("Network error")

        request = ListContactsRequest()

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "Network error" in response.error

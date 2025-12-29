"""
Unit tests for GetContact use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.get_contact import (
    GetContactUseCase,
    GetContactRequest,
    GetContactResponse
)
from app.domain.entities.contact import Contact


class TestGetContactUseCase:
    """Test suite for GetContact use case."""

    @pytest.fixture
    def mock_contact(self):
        """Create mock contact."""
        return Contact(
            id="contact123",
            name="John Doe",
            email="john@example.com",
            type="client"
        )

    @pytest.fixture
    def mock_client(self, mock_contact):
        """Create mock Holded client."""
        client = MagicMock()
        client.get_contact = AsyncMock(return_value=mock_contact)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return GetContactUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_contact_success(self, use_case, mock_client, mock_contact):
        """Test successful contact retrieval."""
        request = GetContactRequest(contact_id="contact123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.contact == mock_contact
        assert response.error is None
        mock_client.get_contact.assert_called_once_with("contact123")

    @pytest.mark.asyncio
    async def test_get_contact_not_found(self, use_case, mock_client):
        """Test contact not found."""
        mock_client.get_contact.return_value = None

        request = GetContactRequest(contact_id="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.contact is None

    @pytest.mark.asyncio
    async def test_get_contact_failure(self, use_case, mock_client):
        """Test contact retrieval failure."""
        mock_client.get_contact.side_effect = Exception("API error")

        request = GetContactRequest(contact_id="contact123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.contact is None
        assert "API error" in response.error

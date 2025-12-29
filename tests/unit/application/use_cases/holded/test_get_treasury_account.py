"""
Unit tests for GetTreasuryAccount use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.get_treasury_account import (
    GetTreasuryAccountUseCase,
    GetTreasuryAccountRequest,
    GetTreasuryAccountResponse
)
from app.domain.entities.treasury import TreasuryAccount


class TestGetTreasuryAccountUseCase:
    """Test suite for GetTreasuryAccount use case."""

    @pytest.fixture
    def mock_account(self):
        """Create mock treasury account."""
        return TreasuryAccount(
            id="account123",
            name="Main Account",
            type="bank",
            balance=5000.0
        )

    @pytest.fixture
    def mock_client(self, mock_account):
        """Create mock Holded client."""
        client = MagicMock()
        client.get_treasury_account = AsyncMock(return_value=mock_account)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return GetTreasuryAccountUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_treasury_account_success(self, use_case, mock_client, mock_account):
        """Test successful treasury account retrieval."""
        request = GetTreasuryAccountRequest(treasury_id="account123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.treasury_account == mock_account
        assert response.error is None
        mock_client.get_treasury_account.assert_called_once_with("account123")

    @pytest.mark.asyncio
    async def test_get_treasury_account_not_found(self, use_case, mock_client):
        """Test treasury account not found."""
        mock_client.get_treasury_account.return_value = None

        request = GetTreasuryAccountRequest(treasury_id="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.treasury_account is None

    @pytest.mark.asyncio
    async def test_get_treasury_account_failure(self, use_case, mock_client):
        """Test treasury account retrieval failure."""
        mock_client.get_treasury_account.side_effect = Exception("API error")

        request = GetTreasuryAccountRequest(treasury_id="account123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.treasury_account is None
        assert "API error" in response.error

"""
Unit tests for ListTreasuryAccounts use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.list_treasury_accounts import (
    ListTreasuryAccountsUseCase,
    ListTreasuryAccountsRequest,
    ListTreasuryAccountsResponse
)
from app.domain.entities.treasury import TreasuryAccount


class TestListTreasuryAccountsUseCase:
    """Test suite for ListTreasuryAccounts use case."""

    @pytest.fixture
    def mock_accounts(self):
        """Create mock treasury accounts."""
        return [
            TreasuryAccount(
                id="1",
                name="Bank Account",
                type="bank",
                balance=10000.0
            ),
            TreasuryAccount(
                id="2",
                name="Cash",
                type="cash",
                balance=500.0
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_accounts):
        """Create mock Holded client."""
        client = MagicMock()
        client.list_treasury_accounts = AsyncMock(return_value=mock_accounts)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return ListTreasuryAccountsUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_list_treasury_accounts_success(self, use_case, mock_client, mock_accounts):
        """Test successful treasury accounts listing."""
        request = ListTreasuryAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.accounts) == 2
        assert response.error is None
        mock_client.list_treasury_accounts.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_treasury_accounts_with_max_results(self, use_case, mock_client):
        """Test listing treasury accounts with max results."""
        request = ListTreasuryAccountsRequest(max_results=50)

        await use_case.execute(request)

        mock_client.list_treasury_accounts.assert_called_once_with(max_results=50)

    @pytest.mark.asyncio
    async def test_list_treasury_accounts_empty_results(self, use_case, mock_client):
        """Test listing with no accounts."""
        mock_client.list_treasury_accounts = AsyncMock(return_value=[])

        request = ListTreasuryAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.accounts) == 0

    @pytest.mark.asyncio
    async def test_list_treasury_accounts_failure(self, use_case, mock_client):
        """Test treasury accounts listing failure."""
        mock_client.list_treasury_accounts.side_effect = Exception("Network error")

        request = ListTreasuryAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "Network error" in response.error

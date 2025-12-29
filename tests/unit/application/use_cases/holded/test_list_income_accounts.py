"""
Unit tests for ListIncomeAccounts use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.list_income_accounts import (
    ListIncomeAccountsUseCase,
    ListIncomeAccountsRequest,
    ListIncomeAccountsResponse
)
from app.domain.entities.accounting import IncomeAccount


class TestListIncomeAccountsUseCase:
    """Test suite for ListIncomeAccounts use case."""

    @pytest.fixture
    def mock_accounts(self):
        """Create mock income accounts."""
        return [
            IncomeAccount(
                id="1",
                code="700",
                name="Sales Revenue",
                description="Revenue from sales"
            ),
            IncomeAccount(
                id="2",
                code="701",
                name="Service Revenue",
                description="Revenue from services"
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_accounts):
        """Create mock Holded client."""
        client = MagicMock()
        client.list_income_accounts = AsyncMock(return_value=mock_accounts)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return ListIncomeAccountsUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_list_income_accounts_success(self, use_case, mock_client, mock_accounts):
        """Test successful income accounts listing."""
        request = ListIncomeAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.accounts) == 2
        assert response.error is None
        mock_client.list_income_accounts.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_income_accounts_with_max_results(self, use_case, mock_client):
        """Test listing income accounts with max results."""
        request = ListIncomeAccountsRequest(max_results=50)

        await use_case.execute(request)

        mock_client.list_income_accounts.assert_called_once_with(max_results=50)

    @pytest.mark.asyncio
    async def test_list_income_accounts_empty_results(self, use_case, mock_client):
        """Test listing with no accounts."""
        mock_client.list_income_accounts = AsyncMock(return_value=[])

        request = ListIncomeAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.accounts) == 0

    @pytest.mark.asyncio
    async def test_list_income_accounts_failure(self, use_case, mock_client):
        """Test income accounts listing failure."""
        mock_client.list_income_accounts.side_effect = Exception("Network error")

        request = ListIncomeAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "Network error" in response.error

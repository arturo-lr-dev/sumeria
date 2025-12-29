"""
Unit tests for ListExpenseAccounts use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.list_expense_accounts import (
    ListExpenseAccountsUseCase,
    ListExpenseAccountsRequest,
    ListExpenseAccountsResponse
)
from app.domain.entities.accounting import ExpenseAccount


class TestListExpenseAccountsUseCase:
    """Test suite for ListExpenseAccounts use case."""

    @pytest.fixture
    def mock_accounts(self):
        """Create mock expense accounts."""
        return [
            ExpenseAccount(
                id="1",
                code="600",
                name="Office Supplies",
                description="Supplies for office"
            ),
            ExpenseAccount(
                id="2",
                code="601",
                name="Travel Expenses",
                description="Business travel costs"
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_accounts):
        """Create mock Holded client."""
        client = MagicMock()
        client.list_expense_accounts = AsyncMock(return_value=mock_accounts)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return ListExpenseAccountsUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_list_expense_accounts_success(self, use_case, mock_client, mock_accounts):
        """Test successful expense accounts listing."""
        request = ListExpenseAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.accounts) == 2
        assert response.error is None
        mock_client.list_expense_accounts.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_expense_accounts_with_max_results(self, use_case, mock_client):
        """Test listing expense accounts with max results."""
        request = ListExpenseAccountsRequest(max_results=50)

        await use_case.execute(request)

        mock_client.list_expense_accounts.assert_called_once_with(max_results=50)

    @pytest.mark.asyncio
    async def test_list_expense_accounts_empty_results(self, use_case, mock_client):
        """Test listing with no accounts."""
        mock_client.list_expense_accounts = AsyncMock(return_value=[])

        request = ListExpenseAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.accounts) == 0

    @pytest.mark.asyncio
    async def test_list_expense_accounts_failure(self, use_case, mock_client):
        """Test expense accounts listing failure."""
        mock_client.list_expense_accounts.side_effect = Exception("API error")

        request = ListExpenseAccountsRequest()

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "API error" in response.error

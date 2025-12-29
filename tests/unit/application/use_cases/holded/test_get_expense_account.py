"""
Unit tests for GetExpenseAccount use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.get_expense_account import (
    GetExpenseAccountUseCase,
    GetExpenseAccountRequest,
    GetExpenseAccountResponse
)
from app.domain.entities.accounting import ExpenseAccount


class TestGetExpenseAccountUseCase:
    """Test suite for GetExpenseAccount use case."""

    @pytest.fixture
    def mock_account(self):
        """Create mock expense account."""
        return ExpenseAccount(
            id="account123",
            code="600",
            name="Office Supplies",
            description="Office supplies and materials"
        )

    @pytest.fixture
    def mock_client(self, mock_account):
        """Create mock Holded client."""
        client = MagicMock()
        client.get_expense_account = AsyncMock(return_value=mock_account)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return GetExpenseAccountUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_expense_account_success(self, use_case, mock_client, mock_account):
        """Test successful expense account retrieval."""
        request = GetExpenseAccountRequest(account_id="account123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.account == mock_account
        assert response.error is None
        mock_client.get_expense_account.assert_called_once_with("account123")

    @pytest.mark.asyncio
    async def test_get_expense_account_not_found(self, use_case, mock_client):
        """Test expense account not found."""
        mock_client.get_expense_account.return_value = None

        request = GetExpenseAccountRequest(account_id="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.account is None

    @pytest.mark.asyncio
    async def test_get_expense_account_failure(self, use_case, mock_client):
        """Test expense account retrieval failure."""
        mock_client.get_expense_account.side_effect = Exception("API error")

        request = GetExpenseAccountRequest(account_id="account123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.account is None
        assert "API error" in response.error

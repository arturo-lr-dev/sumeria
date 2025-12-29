"""
Unit tests for GetIncomeAccount use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.get_income_account import (
    GetIncomeAccountUseCase,
    GetIncomeAccountRequest,
    GetIncomeAccountResponse
)
from app.domain.entities.accounting import IncomeAccount


class TestGetIncomeAccountUseCase:
    """Test suite for GetIncomeAccount use case."""

    @pytest.fixture
    def mock_account(self):
        """Create mock income account."""
        return IncomeAccount(
            id="account123",
            code="700",
            name="Sales Revenue",
            description="Revenue from product sales"
        )

    @pytest.fixture
    def mock_client(self, mock_account):
        """Create mock Holded client."""
        client = MagicMock()
        client.get_income_account = AsyncMock(return_value=mock_account)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return GetIncomeAccountUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_get_income_account_success(self, use_case, mock_client, mock_account):
        """Test successful income account retrieval."""
        request = GetIncomeAccountRequest(account_id="account123")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.account == mock_account
        assert response.error is None
        mock_client.get_income_account.assert_called_once_with("account123")

    @pytest.mark.asyncio
    async def test_get_income_account_not_found(self, use_case, mock_client):
        """Test income account not found."""
        mock_client.get_income_account.return_value = None

        request = GetIncomeAccountRequest(account_id="nonexistent")

        response = await use_case.execute(request)

        assert response.success is True
        assert response.account is None

    @pytest.mark.asyncio
    async def test_get_income_account_failure(self, use_case, mock_client):
        """Test income account retrieval failure."""
        mock_client.get_income_account.side_effect = Exception("API error")

        request = GetIncomeAccountRequest(account_id="account123")

        response = await use_case.execute(request)

        assert response.success is False
        assert response.account is None
        assert "API error" in response.error

"""
Unit tests for CreateTreasuryAccount use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.create_treasury_account import (
    CreateTreasuryAccountUseCase,
    CreateTreasuryAccountRequest,
    CreateTreasuryAccountResponse
)


class TestCreateTreasuryAccountUseCase:
    """Test suite for CreateTreasuryAccount use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Holded client."""
        client = MagicMock()
        client.create_treasury_account = AsyncMock(return_value="account123")
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return CreateTreasuryAccountUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_create_treasury_account_basic(self, use_case, mock_client):
        """Test creating a basic treasury account."""
        request = CreateTreasuryAccountRequest(
            name="Main Bank Account",
            type="bank"
        )

        response = await use_case.execute(request)

        assert response.success is True
        assert response.treasury_id == "account123"
        assert response.error is None
        mock_client.create_treasury_account.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_treasury_account_with_details(self, use_case, mock_client):
        """Test creating treasury account with details."""
        request = CreateTreasuryAccountRequest(
            name="Business Checking",
            type="bank",
            iban="ES1234567890",
            swift="ABCDESXX",
            initial_balance=10000.0
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_treasury_account.call_args[0][0]
        assert draft.name == "Business Checking"
        assert draft.iban == "ES1234567890"

    @pytest.mark.asyncio
    async def test_create_treasury_account_cash_type(self, use_case, mock_client):
        """Test creating cash treasury account."""
        request = CreateTreasuryAccountRequest(
            name="Petty Cash",
            type="cash",
            initial_balance=500.0
        )

        response = await use_case.execute(request)

        assert response.success is True

        draft = mock_client.create_treasury_account.call_args[0][0]
        assert draft.type == "cash"

    @pytest.mark.asyncio
    async def test_create_treasury_account_failure(self, use_case, mock_client):
        """Test treasury account creation failure."""
        mock_client.create_treasury_account.side_effect = Exception("API error")

        request = CreateTreasuryAccountRequest(
            name="Test Account",
            type="bank"
        )

        response = await use_case.execute(request)

        assert response.success is False
        assert response.treasury_id is None
        assert "API error" in response.error

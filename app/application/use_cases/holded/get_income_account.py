"""
Get Income Account use case.
Handles retrieving income account details from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.accounting import IncomeAccount


@dataclass
class GetIncomeAccountRequest:
    """Request to get an income account."""
    account_id: str


@dataclass
class GetIncomeAccountResponse:
    """Response from getting an income account."""
    success: bool
    account: Optional[IncomeAccount] = None
    error: Optional[str] = None


class GetIncomeAccountUseCase:
    """Use case for getting income account details."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: GetIncomeAccountRequest) -> GetIncomeAccountResponse:
        """
        Execute the use case.

        Args:
            request: Get income account request

        Returns:
            Response with income account or error
        """
        try:
            account = await self.client.get_income_account(request.account_id)

            return GetIncomeAccountResponse(
                success=True,
                account=account
            )

        except Exception as e:
            return GetIncomeAccountResponse(
                success=False,
                error=str(e)
            )

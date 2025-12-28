"""
List Income Accounts use case.
Handles listing income accounts from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.accounting import IncomeAccount


@dataclass
class ListIncomeAccountsRequest:
    """Request to list income accounts."""
    max_results: int = 100


@dataclass
class ListIncomeAccountsResponse:
    """Response from listing income accounts."""
    success: bool
    accounts: list[IncomeAccount] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.accounts is None:
            self.accounts = []


class ListIncomeAccountsUseCase:
    """Use case for listing income accounts."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: ListIncomeAccountsRequest) -> ListIncomeAccountsResponse:
        """
        Execute the use case.

        Args:
            request: List income accounts request

        Returns:
            Response with income accounts or error
        """
        try:
            accounts = await self.client.list_income_accounts(
                max_results=request.max_results
            )

            return ListIncomeAccountsResponse(
                success=True,
                accounts=accounts,
                count=len(accounts)
            )

        except Exception as e:
            return ListIncomeAccountsResponse(
                success=False,
                error=str(e)
            )

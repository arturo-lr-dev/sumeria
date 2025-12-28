"""
List Expense Accounts use case.
Handles listing expense accounts from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.accounting import ExpenseAccount


@dataclass
class ListExpenseAccountsRequest:
    """Request to list expense accounts."""
    max_results: int = 100


@dataclass
class ListExpenseAccountsResponse:
    """Response from listing expense accounts."""
    success: bool
    accounts: list[ExpenseAccount] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.accounts is None:
            self.accounts = []


class ListExpenseAccountsUseCase:
    """Use case for listing expense accounts."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: ListExpenseAccountsRequest) -> ListExpenseAccountsResponse:
        """
        Execute the use case.

        Args:
            request: List expense accounts request

        Returns:
            Response with expense accounts or error
        """
        try:
            accounts = await self.client.list_expense_accounts(
                max_results=request.max_results
            )

            return ListExpenseAccountsResponse(
                success=True,
                accounts=accounts,
                count=len(accounts)
            )

        except Exception as e:
            return ListExpenseAccountsResponse(
                success=False,
                error=str(e)
            )

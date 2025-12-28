"""
Get Expense Account use case.
Handles retrieving expense account details from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.accounting import ExpenseAccount


@dataclass
class GetExpenseAccountRequest:
    """Request to get an expense account."""
    account_id: str


@dataclass
class GetExpenseAccountResponse:
    """Response from getting an expense account."""
    success: bool
    account: Optional[ExpenseAccount] = None
    error: Optional[str] = None


class GetExpenseAccountUseCase:
    """Use case for getting expense account details."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: GetExpenseAccountRequest) -> GetExpenseAccountResponse:
        """
        Execute the use case.

        Args:
            request: Get expense account request

        Returns:
            Response with expense account or error
        """
        try:
            account = await self.client.get_expense_account(request.account_id)

            return GetExpenseAccountResponse(
                success=True,
                account=account
            )

        except Exception as e:
            return GetExpenseAccountResponse(
                success=False,
                error=str(e)
            )

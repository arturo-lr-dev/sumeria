"""
List Treasury Accounts use case.
Handles listing treasury accounts from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.treasury import TreasuryAccount


@dataclass
class ListTreasuryAccountsRequest:
    """Request to list treasury accounts."""
    max_results: int = 100


@dataclass
class ListTreasuryAccountsResponse:
    """Response from listing treasury accounts."""
    success: bool
    accounts: list[TreasuryAccount] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.accounts is None:
            self.accounts = []


class ListTreasuryAccountsUseCase:
    """Use case for listing treasury accounts."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: ListTreasuryAccountsRequest) -> ListTreasuryAccountsResponse:
        """
        Execute the use case.

        Args:
            request: List treasury accounts request

        Returns:
            Response with treasury accounts or error
        """
        try:
            accounts = await self.client.list_treasury_accounts(
                max_results=request.max_results
            )

            return ListTreasuryAccountsResponse(
                success=True,
                accounts=accounts,
                count=len(accounts)
            )

        except Exception as e:
            return ListTreasuryAccountsResponse(
                success=False,
                error=str(e)
            )

"""
Get Treasury Account use case.
Handles retrieving treasury account details from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.treasury import TreasuryAccount


@dataclass
class GetTreasuryAccountRequest:
    """Request to get a treasury account."""
    treasury_id: str


@dataclass
class GetTreasuryAccountResponse:
    """Response from getting a treasury account."""
    success: bool
    treasury_account: Optional[TreasuryAccount] = None
    error: Optional[str] = None


class GetTreasuryAccountUseCase:
    """Use case for getting treasury account details."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: GetTreasuryAccountRequest) -> GetTreasuryAccountResponse:
        """
        Execute the use case.

        Args:
            request: Get treasury account request

        Returns:
            Response with treasury account or error
        """
        try:
            treasury_account = await self.client.get_treasury_account(request.treasury_id)

            return GetTreasuryAccountResponse(
                success=True,
                treasury_account=treasury_account
            )

        except Exception as e:
            return GetTreasuryAccountResponse(
                success=False,
                error=str(e)
            )

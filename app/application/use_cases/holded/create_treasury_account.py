"""
Create Treasury Account use case.
Handles creating new treasury accounts in Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.treasury import TreasuryAccountDraft


@dataclass
class CreateTreasuryAccountRequest:
    """Request to create a treasury account."""
    name: str
    iban: Optional[str] = None
    swift: Optional[str] = None
    bank_name: Optional[str] = None
    accounting_account_number: Optional[str] = None
    initial_balance: float = 0.0
    type: str = "bank"
    notes: Optional[str] = None


@dataclass
class CreateTreasuryAccountResponse:
    """Response from creating a treasury account."""
    success: bool
    treasury_id: Optional[str] = None
    error: Optional[str] = None


class CreateTreasuryAccountUseCase:
    """Use case for creating treasury accounts."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: CreateTreasuryAccountRequest) -> CreateTreasuryAccountResponse:
        """
        Execute the use case.

        Args:
            request: Create treasury account request

        Returns:
            Response with treasury ID or error
        """
        try:
            # Create draft
            draft = TreasuryAccountDraft(
                name=request.name,
                iban=request.iban,
                swift=request.swift,
                bank_name=request.bank_name,
                accounting_account_number=request.accounting_account_number,
                initial_balance=request.initial_balance,
                type=request.type,
                notes=request.notes
            )

            # Create treasury account
            treasury_id = await self.client.create_treasury_account(draft)

            return CreateTreasuryAccountResponse(
                success=True,
                treasury_id=treasury_id
            )

        except Exception as e:
            return CreateTreasuryAccountResponse(
                success=False,
                error=str(e)
            )

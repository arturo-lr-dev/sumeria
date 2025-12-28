"""
Treasury domain entity for Holded integration.
Represents treasury/bank accounts in Holded.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TreasuryAccount:
    """
    Treasury account entity representing a bank or cash account.
    Maps to Holded treasury API.
    """
    id: Optional[str] = None
    name: str = ""

    # Account details
    iban: Optional[str] = None
    swift: Optional[str] = None
    bank_name: Optional[str] = None

    # Accounting integration
    accounting_account: Optional[str] = None
    accounting_account_number: Optional[str] = None

    # Balance
    balance: float = 0.0
    initial_balance: float = 0.0

    # Status
    active: bool = True

    # Type
    type: str = "bank"  # bank, cash, other

    # Additional info
    notes: Optional[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class TreasuryAccountDraft:
    """Draft for creating a new treasury account."""
    name: str
    iban: Optional[str] = None
    swift: Optional[str] = None
    bank_name: Optional[str] = None
    accounting_account_number: Optional[str] = None
    initial_balance: float = 0.0
    type: str = "bank"
    notes: Optional[str] = None

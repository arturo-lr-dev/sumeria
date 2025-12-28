"""
Accounting domain entities for Holded integration.
Represents expense and income accounts.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ExpenseAccount:
    """
    Expense account entity from chart of accounts.
    Maps to Holded expenses accounts API.
    """
    id: Optional[str] = None
    name: str = ""

    # Account number in chart of accounts
    account_number: Optional[str] = None
    code: Optional[str] = None

    # Category
    category: Optional[str] = None
    subcategory: Optional[str] = None

    # Description
    description: Optional[str] = None

    # Status
    active: bool = True

    # Balance
    balance: float = 0.0

    # Parent account (for hierarchical chart of accounts)
    parent_id: Optional[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class IncomeAccount:
    """
    Income account entity from chart of accounts.
    Maps to Holded income accounts API.
    """
    id: Optional[str] = None
    name: str = ""

    # Account number in chart of accounts
    account_number: Optional[str] = None
    code: Optional[str] = None

    # Category
    category: Optional[str] = None
    subcategory: Optional[str] = None

    # Description
    description: Optional[str] = None

    # Status
    active: bool = True

    # Balance
    balance: float = 0.0

    # Parent account
    parent_id: Optional[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AccountingEntry:
    """
    Accounting entry (journal entry).
    Represents a transaction in the accounting system.
    """
    id: Optional[str] = None

    # Entry details
    date: Optional[datetime] = None
    description: str = ""
    reference: Optional[str] = None

    # Accounts involved
    debit_account: Optional[str] = None
    credit_account: Optional[str] = None

    # Amount
    amount: float = 0.0

    # Status
    posted: bool = False

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

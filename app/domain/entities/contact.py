"""
Contact domain entity for Holded integration.
Represents a customer or supplier in Holded.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ContactAddress:
    """Contact address information."""
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


@dataclass
class Contact:
    """
    Contact entity representing a customer or supplier.
    Maps to Holded contacts API.
    """
    id: Optional[str] = None
    name: str = ""
    code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None

    # Tax information
    vat_number: Optional[str] = None

    # Address
    billing_address: Optional[ContactAddress] = None
    shipping_address: Optional[ContactAddress] = None

    # Type
    type: str = "client"  # client or supplier

    # Additional info
    notes: Optional[str] = None
    tags: list[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ContactDraft:
    """Draft for creating a new contact."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    vat_number: Optional[str] = None
    type: str = "client"
    notes: Optional[str] = None
    billing_address: Optional[ContactAddress] = None
    shipping_address: Optional[ContactAddress] = None
    tags: Optional[list[str]] = None

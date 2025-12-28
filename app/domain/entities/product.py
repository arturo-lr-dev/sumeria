"""
Product domain entity for Holded integration.
Represents a product or service in Holded.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Product entity representing an item or service.
    Maps to Holded products API.
    """
    id: Optional[str] = None
    name: str = ""
    code: Optional[str] = None
    description: Optional[str] = None

    # Pricing
    price: float = 0.0
    cost: Optional[float] = None

    # Tax
    tax_rate: Optional[float] = None

    # Type
    type: str = "product"  # product or service

    # Stock
    stock: Optional[int] = None
    track_stock: bool = False

    # Status
    active: bool = True

    # Categories
    category: Optional[str] = None
    tags: list[str] = None

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

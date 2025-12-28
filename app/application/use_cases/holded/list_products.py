"""
List Products use case.
Handles listing products from Holded.
"""
from dataclasses import dataclass
from typing import Optional

from app.infrastructure.connectors.holded.client import HoldedClient
from app.domain.entities.product import Product


@dataclass
class ListProductsRequest:
    """Request to list products."""
    active_only: bool = True
    max_results: int = 100


@dataclass
class ListProductsResponse:
    """Response from listing products."""
    success: bool
    products: list[Product] = None
    count: int = 0
    error: Optional[str] = None

    def __post_init__(self):
        if self.products is None:
            self.products = []


class ListProductsUseCase:
    """Use case for listing products."""

    def __init__(self, client: Optional[HoldedClient] = None):
        """Initialize use case."""
        self.client = client or HoldedClient()

    async def execute(self, request: ListProductsRequest) -> ListProductsResponse:
        """
        Execute the use case.

        Args:
            request: List products request

        Returns:
            Response with products or error
        """
        try:
            products = await self.client.list_products(
                active_only=request.active_only,
                max_results=request.max_results
            )

            return ListProductsResponse(
                success=True,
                products=products,
                count=len(products)
            )

        except Exception as e:
            return ListProductsResponse(
                success=False,
                error=str(e)
            )

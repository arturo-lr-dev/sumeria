"""
Unit tests for ListProducts use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.application.use_cases.holded.list_products import (
    ListProductsUseCase,
    ListProductsRequest,
    ListProductsResponse
)
from app.domain.entities.product import Product


class TestListProductsUseCase:
    """Test suite for ListProducts use case."""

    @pytest.fixture
    def mock_products(self):
        """Create mock products."""
        return [
            Product(
                id="1",
                name="Product 1",
                code="SKU001",
                price=100.0
            ),
            Product(
                id="2",
                name="Product 2",
                code="SKU002",
                price=200.0
            )
        ]

    @pytest.fixture
    def mock_client(self, mock_products):
        """Create mock Holded client."""
        client = MagicMock()
        client.list_products = AsyncMock(return_value=mock_products)
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return ListProductsUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_list_products_success(self, use_case, mock_client, mock_products):
        """Test successful product listing."""
        request = ListProductsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 2
        assert len(response.products) == 2
        assert response.error is None
        mock_client.list_products.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_products_with_max_results(self, use_case, mock_client):
        """Test listing products with max results."""
        request = ListProductsRequest(max_results=50)

        await use_case.execute(request)

        mock_client.list_products.assert_called_once_with(
            active_only=True,
            max_results=50
        )

    @pytest.mark.asyncio
    async def test_list_products_empty_results(self, use_case, mock_client):
        """Test listing with no products."""
        mock_client.list_products = AsyncMock(return_value=[])

        request = ListProductsRequest()

        response = await use_case.execute(request)

        assert response.success is True
        assert response.count == 0
        assert len(response.products) == 0

    @pytest.mark.asyncio
    async def test_list_products_failure(self, use_case, mock_client):
        """Test product listing failure."""
        mock_client.list_products.side_effect = Exception("API error")

        request = ListProductsRequest()

        response = await use_case.execute(request)

        assert response.success is False
        assert response.count == 0
        assert "API error" in response.error

"""
Holded API client implementation.
Handles all interactions with Holded API.
"""
from typing import Optional, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.infrastructure.connectors.holded.schemas import HoldedMapper
from app.domain.entities.invoice import Invoice, InvoiceDraft, InvoiceSearchCriteria
from app.domain.entities.contact import Contact, ContactDraft
from app.domain.entities.product import Product


class HoldedClient:
    """
    Holded API client for business operations.
    Handles authentication and API communication.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Holded client.

        Args:
            api_key: Holded API key (will use settings if not provided)
        """
        self.api_key = api_key or settings.holded_api_key
        self.base_url = settings.holded_api_base_url

        self.headers = {
            "key": self.api_key or "",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> Any:
        """
        Make HTTP request to Holded API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.api_key:
            raise ValueError("Holded API key is required to make requests")

        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )

            response.raise_for_status()

            if response.status_code == 204:
                return None

            return response.json()

    # ============ Invoice Operations ============

    async def create_invoice(self, draft: InvoiceDraft) -> str:
        """
        Create a new invoice.

        Args:
            draft: Invoice draft

        Returns:
            Invoice ID

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            data = HoldedMapper.from_invoice_draft(draft)

            result = await self._request(
                method="POST",
                endpoint="/api/invoicing/v1/documents",
                data=data
            )

            return result.get("id", "")

        except Exception as error:
            raise Exception(f"Failed to create invoice: {error}")

    async def get_invoice(self, invoice_id: str) -> Invoice:
        """
        Get invoice by ID.

        Args:
            invoice_id: Invoice ID

        Returns:
            Invoice entity

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            data = await self._request(
                method="GET",
                endpoint=f"/api/invoicing/v1/documents/{invoice_id}"
            )

            return HoldedMapper.to_invoice_entity(data)

        except Exception as error:
            raise Exception(f"Failed to get invoice: {error}")

    async def list_invoices(
        self,
        criteria: Optional[InvoiceSearchCriteria] = None
    ) -> list[Invoice]:
        """
        List invoices based on criteria.

        Args:
            criteria: Search criteria

        Returns:
            List of invoices

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            params = {}

            if criteria:
                if criteria.contact_id:
                    params["contact"] = criteria.contact_id
                if criteria.status:
                    params["status"] = criteria.status
                if criteria.doc_type:
                    params["docType"] = criteria.doc_type
                if criteria.from_date:
                    params["fromDate"] = criteria.from_date.isoformat()
                if criteria.to_date:
                    params["toDate"] = criteria.to_date.isoformat()

            data = await self._request(
                method="GET",
                endpoint="/api/invoicing/v1/documents",
                params=params
            )

            invoices = []
            for item in data:
                invoices.append(HoldedMapper.to_invoice_entity(item))

            return invoices[:criteria.max_results] if criteria else invoices

        except Exception as error:
            raise Exception(f"Failed to list invoices: {error}")

    # ============ Contact Operations ============

    async def create_contact(self, draft: ContactDraft) -> str:
        """
        Create a new contact.

        Args:
            draft: Contact draft

        Returns:
            Contact ID

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            data = HoldedMapper.from_contact_draft(draft)

            result = await self._request(
                method="POST",
                endpoint="/api/invoicing/v1/contacts",
                data=data
            )

            return result.get("id", "")

        except Exception as error:
            raise Exception(f"Failed to create contact: {error}")

    async def get_contact(self, contact_id: str) -> Contact:
        """
        Get contact by ID.

        Args:
            contact_id: Contact ID

        Returns:
            Contact entity

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            data = await self._request(
                method="GET",
                endpoint=f"/api/invoicing/v1/contacts/{contact_id}"
            )

            return HoldedMapper.to_contact_entity(data)

        except Exception as error:
            raise Exception(f"Failed to get contact: {error}")

    async def list_contacts(
        self,
        contact_type: Optional[str] = None,
        max_results: int = 100
    ) -> list[Contact]:
        """
        List contacts.

        Args:
            contact_type: Filter by type (client or supplier)
            max_results: Maximum number of results

        Returns:
            List of contacts

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            params = {}
            if contact_type:
                params["type"] = contact_type

            data = await self._request(
                method="GET",
                endpoint="/api/invoicing/v1/contacts",
                params=params
            )

            contacts = []
            for item in data:
                contacts.append(HoldedMapper.to_contact_entity(item))

            return contacts[:max_results]

        except Exception as error:
            raise Exception(f"Failed to list contacts: {error}")

    # ============ Product Operations ============

    async def list_products(
        self,
        active_only: bool = True,
        max_results: int = 100
    ) -> list[Product]:
        """
        List products.

        Args:
            active_only: Only return active products
            max_results: Maximum number of results

        Returns:
            List of products

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            params = {}
            if active_only:
                params["active"] = "true"

            data = await self._request(
                method="GET",
                endpoint="/api/invoicing/v1/products",
                params=params
            )

            products = []
            for item in data:
                products.append(HoldedMapper.to_product_entity(item))

            return products[:max_results]

        except Exception as error:
            raise Exception(f"Failed to list products: {error}")

    async def get_product(self, product_id: str) -> Product:
        """
        Get product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product entity

        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            data = await self._request(
                method="GET",
                endpoint=f"/api/invoicing/v1/products/{product_id}"
            )

            return HoldedMapper.to_product_entity(data)

        except Exception as error:
            raise Exception(f"Failed to get product: {error}")

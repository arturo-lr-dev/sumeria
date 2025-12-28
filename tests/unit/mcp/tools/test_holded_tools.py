"""
Unit tests for Holded MCP tools.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.mcp.tools.holded_tools import HoldedTools
from app.domain.entities.invoice import Invoice, InvoiceItem
from app.domain.entities.contact import Contact
from app.domain.entities.product import Product
from app.domain.entities.treasury import TreasuryAccount
from app.domain.entities.accounting import ExpenseAccount, IncomeAccount


@pytest.fixture
def mock_settings():
    """Mock settings for Holded API."""
    with patch('app.infrastructure.connectors.holded.client.settings') as mock:
        mock.holded_api_key = "test_api_key"
        mock.holded_api_base_url = "https://api.holded.com"
        yield mock


@pytest.fixture
def holded_tools(mock_settings):
    """Create HoldedTools instance with mocked client."""
    return HoldedTools()


@pytest.mark.asyncio
async def test_create_invoice_tool(holded_tools):
    """Test create invoice tool."""
    # Arrange
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.invoice_id = "invoice123"
    mock_response.error = None

    # Act
    with patch.object(holded_tools.create_invoice_uc, 'execute', return_value=mock_response):
        result = await holded_tools.create_invoice(
            contact_id="contact123",
            items=[{"name": "Test", "quantity": 1, "price": 100.0}]
        )

    # Assert
    assert result.success is True
    assert result.invoice_id == "invoice123"


@pytest.mark.asyncio
async def test_get_invoice_tool(holded_tools):
    """Test get invoice tool."""
    # Arrange
    mock_invoice = Invoice(
        id="invoice123",
        doc_type="invoice",
        total=121.0,
        status="draft",
        items=[]
    )
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.invoice = mock_invoice
    mock_response.error = None

    # Act
    with patch.object(holded_tools.get_invoice_uc, 'execute', return_value=mock_response):
        result = await holded_tools.get_invoice("invoice123")

    # Assert
    assert result.success is True
    assert result.invoice.id == "invoice123"


@pytest.mark.asyncio
async def test_list_invoices_tool(holded_tools):
    """Test list invoices tool."""
    # Arrange
    mock_invoices = [
        Invoice(id="inv1", doc_type="invoice", total=100.0, status="draft", items=[]),
        Invoice(id="inv2", doc_type="invoice", total=200.0, status="paid", items=[])
    ]
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.invoices = mock_invoices
    mock_response.count = 2
    mock_response.error = None

    # Act
    with patch.object(holded_tools.list_invoices_uc, 'execute', return_value=mock_response):
        result = await holded_tools.list_invoices()

    # Assert
    assert result.success is True
    assert result.count == 2
    assert len(result.invoices) == 2


@pytest.mark.asyncio
async def test_create_contact_tool(holded_tools):
    """Test create contact tool."""
    # Arrange
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.contact_id = "contact123"
    mock_response.error = None

    # Act
    with patch.object(holded_tools.create_contact_uc, 'execute', return_value=mock_response):
        result = await holded_tools.create_contact(
            name="Test Customer",
            email="test@example.com"
        )

    # Assert
    assert result.success is True
    assert result.contact_id == "contact123"


@pytest.mark.asyncio
async def test_list_contacts_tool(holded_tools):
    """Test list contacts tool."""
    # Arrange
    mock_contacts = [
        Contact(id="contact1", name="Customer 1", type="client"),
        Contact(id="contact2", name="Customer 2", type="client")
    ]
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.contacts = mock_contacts
    mock_response.count = 2
    mock_response.error = None

    # Act
    with patch.object(holded_tools.list_contacts_uc, 'execute', return_value=mock_response):
        result = await holded_tools.list_contacts()

    # Assert
    assert result.success is True
    assert result.count == 2
    assert len(result.contacts) == 2


@pytest.mark.asyncio
async def test_list_products_tool(holded_tools):
    """Test list products tool."""
    # Arrange
    mock_products = [
        Product(id="prod1", name="Product 1", price=100.0, type="product", active=True),
        Product(id="prod2", name="Product 2", price=200.0, type="product", active=True)
    ]
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.products = mock_products
    mock_response.count = 2
    mock_response.error = None

    # Act
    with patch.object(holded_tools.list_products_uc, 'execute', return_value=mock_response):
        result = await holded_tools.list_products()

    # Assert
    assert result.success is True
    assert result.count == 2
    assert len(result.products) == 2


@pytest.mark.asyncio
async def test_list_treasury_accounts_tool(holded_tools):
    """Test list treasury accounts tool."""
    # Arrange
    mock_accounts = [
        TreasuryAccount(id="treasury1", name="Main Bank", balance=5000.0, type="bank", active=True),
        TreasuryAccount(id="treasury2", name="Cash", balance=1000.0, type="cash", active=True)
    ]
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.accounts = mock_accounts
    mock_response.count = 2
    mock_response.error = None

    # Act
    with patch.object(holded_tools.list_treasury_accounts_uc, 'execute', return_value=mock_response):
        result = await holded_tools.list_treasury_accounts()

    # Assert
    assert result.success is True
    assert result.count == 2
    assert len(result.accounts) == 2


@pytest.mark.asyncio
async def test_list_expense_accounts_tool(holded_tools):
    """Test list expense accounts tool."""
    # Arrange
    mock_accounts = [
        ExpenseAccount(id="expense1", name="Office Supplies", account_number="6000", balance=2500.0, active=True),
        ExpenseAccount(id="expense2", name="Rent", account_number="6100", balance=5000.0, active=True)
    ]
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.accounts = mock_accounts
    mock_response.count = 2
    mock_response.error = None

    # Act
    with patch.object(holded_tools.list_expense_accounts_uc, 'execute', return_value=mock_response):
        result = await holded_tools.list_expense_accounts()

    # Assert
    assert result.success is True
    assert result.count == 2
    assert len(result.accounts) == 2


@pytest.mark.asyncio
async def test_list_income_accounts_tool(holded_tools):
    """Test list income accounts tool."""
    # Arrange
    mock_accounts = [
        IncomeAccount(id="income1", name="Sales Revenue", account_number="7000", balance=15000.0, active=True),
        IncomeAccount(id="income2", name="Service Revenue", account_number="7100", balance=10000.0, active=True)
    ]
    mock_response = AsyncMock()
    mock_response.success = True
    mock_response.accounts = mock_accounts
    mock_response.count = 2
    mock_response.error = None

    # Act
    with patch.object(holded_tools.list_income_accounts_uc, 'execute', return_value=mock_response):
        result = await holded_tools.list_income_accounts()

    # Assert
    assert result.success is True
    assert result.count == 2
    assert len(result.accounts) == 2

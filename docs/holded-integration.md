# Holded Integration

This document describes the Holded integration in the Sumeria Personal Assistant MCP server.

## Overview

The Holded integration provides MCP tools to interact with the Holded API, enabling you to:

- Manage invoices, quotes, and proforma documents
- Create and manage customer and supplier contacts
- View product catalogs with pricing information
- Filter and search invoices by various criteria

## Getting Started

### 1. Obtain Holded API Key

1. Log in to your Holded account
2. Navigate to **Settings** → **Developers**
3. Click on **API Documentation**
4. Generate an API key
5. Copy the API key

### 2. Configure Environment Variables

Add your Holded API key to your `.env` file:

```bash
HOLDED_API_KEY=your-holded-api-key-here
HOLDED_API_BASE_URL=https://api.holded.com
```

### 3. Test the Integration

Run the MCP server and test the Holded tools:

```bash
python -m app.main
```

## Available Tools

### Invoice Management

#### `holded_create_invoice`

Create a new invoice, quote, or proforma document.

**Parameters:**
- `contact_id` (required): Holded contact ID
- `items` (required): List of invoice items
  - `name`: Item name
  - `description`: Item description (optional)
  - `quantity`: Quantity (default: 1.0)
  - `price`: Unit price
  - `tax_rate`: Tax rate percentage
  - `discount`: Discount percentage (optional)
  - `product_id`: Link to product catalog (optional)
- `doc_type`: Document type (default: "invoice")
  - Options: invoice, quote, proforma, delivery_note
- `date`: Invoice date (YYYY-MM-DD format, optional)
- `due_date`: Due date (YYYY-MM-DD format, optional)
- `notes`: Additional notes (optional)
- `tags`: List of tags (optional)
- `payment_method`: Payment method (optional)

**Example:**
```python
{
    "contact_id": "63f8a1234567890abcdef123",
    "items": [
        {
            "name": "Web Development Services",
            "description": "Frontend development - 40 hours",
            "quantity": 40,
            "price": 50.0,
            "tax_rate": 21.0
        }
    ],
    "doc_type": "invoice",
    "date": "2025-01-15",
    "due_date": "2025-02-15",
    "notes": "Payment terms: 30 days"
}
```

#### `holded_get_invoice`

Get detailed information about a specific invoice.

**Parameters:**
- `invoice_id` (required): Holded invoice/document ID

**Returns:**
- Complete invoice details including items, amounts, status, and payment information

#### `holded_list_invoices`

List and filter invoices.

**Parameters:**
- `contact_id`: Filter by contact (optional)
- `status`: Filter by status (optional)
  - Options: draft, sent, paid, cancelled
- `doc_type`: Filter by document type (optional)
  - Options: invoice, quote, proforma, delivery_note
- `from_date`: Filter from date (YYYY-MM-DD, optional)
- `to_date`: Filter to date (YYYY-MM-DD, optional)
- `paid`: Filter by payment status (boolean, optional)
- `max_results`: Maximum results to return (default: 10, max: 100)

**Example:**
```python
{
    "status": "unpaid",
    "from_date": "2025-01-01",
    "max_results": 20
}
```

### Contact Management

#### `holded_create_contact`

Create a new customer or supplier contact.

**Parameters:**
- `name` (required): Contact name
- `email`: Contact email (optional)
- `phone`: Contact phone (optional)
- `mobile`: Contact mobile (optional)
- `vat_number`: VAT/Tax identification number (optional)
- `type`: Contact type (default: "client")
  - Options: client, supplier
- `notes`: Additional notes (optional)
- `billing_address`: Billing address object (optional)
  - `street`: Street address
  - `city`: City
  - `province`: Province/State
  - `postal_code`: Postal code
  - `country`: Country
- `shipping_address`: Shipping address object (optional, same structure as billing)
- `tags`: List of tags (optional)

**Example:**
```python
{
    "name": "Acme Corporation",
    "email": "contact@acme.com",
    "phone": "+34912345678",
    "vat_number": "ESB12345678",
    "type": "client",
    "billing_address": {
        "street": "Calle Mayor 1",
        "city": "Madrid",
        "province": "Madrid",
        "postal_code": "28001",
        "country": "Spain"
    }
}
```

#### `holded_get_contact`

Get detailed information about a specific contact.

**Parameters:**
- `contact_id` (required): Holded contact ID

**Returns:**
- Complete contact details including addresses and tax information

#### `holded_list_contacts`

List all contacts (customers and suppliers).

**Parameters:**
- `contact_type`: Filter by type (optional)
  - Options: client, supplier
- `max_results`: Maximum results to return (default: 100)

### Product Catalog

#### `holded_list_products`

List products from your Holded catalog.

**Parameters:**
- `active_only`: Only show active products (default: true)
- `max_results`: Maximum results to return (default: 100)

**Returns:**
- List of products with pricing, tax rates, and stock information

### Treasury Management

#### `holded_create_treasury_account`

Create a new treasury account (bank account, cash account, etc.).

**Parameters:**
- `name` (required): Account name
- `iban`: IBAN number (optional)
- `swift`: SWIFT/BIC code (optional)
- `bank_name`: Bank name (optional)
- `accounting_account_number`: Accounting account number (optional)
- `initial_balance`: Initial balance (default: 0.0)
- `type`: Account type (default: "bank")
  - Options: bank, cash, other
- `notes`: Additional notes (optional)

**Example:**
```python
{
    "name": "Business Checking Account",
    "iban": "ES9121000418450200051332",
    "swift": "BBVAESMMXXX",
    "bank_name": "BBVA",
    "initial_balance": 10000.0,
    "type": "bank"
}
```

#### `holded_get_treasury_account`

Get detailed information about a specific treasury account.

**Parameters:**
- `treasury_id` (required): Holded treasury account ID

**Returns:**
- Complete treasury account details including balance, IBAN, and bank information

#### `holded_list_treasury_accounts`

List all treasury accounts.

**Parameters:**
- `max_results`: Maximum results to return (default: 100)

**Returns:**
- List of treasury accounts with their balances and details

### Accounting

#### `holded_list_expense_accounts`

List expense accounts from the chart of accounts.

**Parameters:**
- `max_results`: Maximum results to return (default: 100)

**Returns:**
- List of expense accounts with account numbers and balances

#### `holded_get_expense_account`

Get detailed information about a specific expense account.

**Parameters:**
- `account_id` (required): Holded expense account ID

**Returns:**
- Complete expense account details including account number and balance

#### `holded_list_income_accounts`

List income accounts from the chart of accounts.

**Parameters:**
- `max_results`: Maximum results to return (default: 100)

**Returns:**
- List of income accounts with account numbers and balances

#### `holded_get_income_account`

Get detailed information about a specific income account.

**Parameters:**
- `account_id` (required): Holded income account ID

**Returns:**
- Complete income account details including account number and balance

## Architecture

The Holded integration follows the clean architecture pattern:

```
app/
├── domain/entities/           # Domain entities
│   ├── invoice.py            # Invoice, InvoiceItem, InvoiceDraft
│   ├── contact.py            # Contact, ContactAddress, ContactDraft
│   └── product.py            # Product
├── infrastructure/
│   └── connectors/holded/    # Holded API integration
│       ├── client.py         # HTTP client with retry logic
│       └── schemas.py        # Data mappers
├── application/
│   └── use_cases/holded/     # Business logic
│       ├── create_invoice.py
│       ├── get_invoice.py
│       ├── list_invoices.py
│       ├── create_contact.py
│       ├── get_contact.py
│       ├── list_contacts.py
│       └── list_products.py
└── mcp/
    └── tools/
        └── holded_tools.py   # MCP tool implementations
```

## API Rate Limits

The Holded API has rate limits. The client includes automatic retry logic with exponential backoff:

- Maximum 3 retry attempts
- Exponential backoff: 2s, 4s, 8s
- Automatic handling of transient failures

## Error Handling

All tools return structured responses with success status and error messages:

```python
{
    "success": true,
    "invoice_id": "63f8a1234567890abcdef123",
    "error": null
}
```

Or on failure:

```python
{
    "success": false,
    "invoice_id": null,
    "error": "Failed to create invoice: Invalid contact_id"
}
```

## Testing

Run the test suite:

```bash
# Run all Holded tests
pytest tests/unit/infrastructure/connectors/holded/
pytest tests/unit/application/use_cases/holded/
pytest tests/unit/mcp/tools/test_holded_tools.py

# Run with coverage
pytest --cov=app.infrastructure.connectors.holded
pytest --cov=app.application.use_cases.holded
pytest --cov=app.mcp.tools.holded_tools
```

## Common Use Cases

### Creating an Invoice for a New Customer

1. Create the contact first:
```python
holded_create_contact(
    name="New Customer",
    email="customer@example.com",
    type="client"
)
# Returns: {"success": true, "contact_id": "contact123"}
```

2. Create the invoice:
```python
holded_create_invoice(
    contact_id="contact123",
    items=[
        {
            "name": "Service",
            "quantity": 1,
            "price": 1000.0,
            "tax_rate": 21.0
        }
    ]
)
```

### Listing Unpaid Invoices

```python
holded_list_invoices(
    paid=false,
    status="sent",
    max_results=50
)
```

### Finding Products for an Invoice

```python
# List active products
products = holded_list_products(active_only=true)

# Use product_id when creating invoice items
holded_create_invoice(
    contact_id="contact123",
    items=[
        {
            "name": "Product Name",
            "product_id": "product123",
            "quantity": 2,
            "price": 100.0,
            "tax_rate": 21.0
        }
    ]
)
```

## Troubleshooting

### Authentication Errors

If you receive authentication errors:

1. Verify your API key is correct
2. Check that the API key is properly set in `.env`
3. Ensure the API key has not expired
4. Regenerate the API key if necessary

### Invalid Contact ID

Make sure the contact exists in Holded before creating invoices. Use `holded_list_contacts` to find the correct contact ID.

### Date Format Errors

Always use ISO format for dates: `YYYY-MM-DD` (e.g., "2025-01-15")

## Resources

- [Holded API Documentation](https://developers.holded.com/)
- [Holded Support](https://help.holded.com/)
- [API Key Management](https://app.holded.com/settings/developers)

## Future Enhancements

Potential future additions to the Holded integration:

- Payment tracking and reconciliation
- Expense management
- Project management integration
- Advanced reporting and analytics
- Webhook support for real-time updates
- Batch operations for bulk data import/export

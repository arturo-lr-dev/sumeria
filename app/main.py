from app.config.settings import settings

"""
Main MCP Server implementation.
Registers all tools and configures the server.
"""
from fastmcp import FastMCP
from app.config.settings import settings
from app.config.mcp_config import mcp_config
from app.mcp.tools.gmail_tools import gmail_tools
from app.mcp.tools.holded_tools import holded_tools
from app.mcp.tools.notion_tools import notion_tools
from app.mcp.tools.whatsapp_tools import whatsapp_tools


# Initialize MCP server
# Note: no_auth=True disables SSO authentication for the MCP server
# We only need Gmail OAuth, not MCP server authentication
mcp = FastMCP(
    name=settings.mcp_server_name
)


# Register Gmail tools
@mcp.tool()
async def send_email(
    to: list[str],
    subject: str,
    body_text: str = None,
    body_html: str = None,
    cc: list[str] = None,
    bcc: list[str] = None,
    account_id: str = None
):
    """
    Send an email via Gmail.

    Supports multiple Gmail accounts. If account_id is not provided,
    the default account will be used.
    """
    return await gmail_tools.send_email(
        to=to,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        cc=cc,
        bcc=bcc,
        account_id=account_id
    )


@mcp.tool()
async def search_emails(
    query: str = None,
    from_address: str = None,
    to_address: str = None,
    subject: str = None,
    has_attachment: bool = None,
    is_unread: bool = None,
    label: str = None,
    max_results: int = 10,
    account_id: str = None
):
    """
    Search emails in Gmail using various filters.

    You can use Gmail search syntax in the 'query' parameter,
    or use the specific filters. Supports multiple accounts.

    Common labels: INBOX, SENT, DRAFT, TRASH, SPAM, STARRED, IMPORTANT, UNREAD
    """
    return await gmail_tools.search_emails(
        query=query,
        from_address=from_address,
        to_address=to_address,
        subject=subject,
        has_attachment=has_attachment,
        is_unread=is_unread,
        label=label,
        max_results=max_results,
        account_id=account_id
    )


@mcp.tool()
async def get_email(
    message_id: str,
    account_id: str = None
):
    """
    Get detailed information about a specific email.

    Returns complete email details including body, headers, and attachments.
    Use message_id from search results.
    """
    return await gmail_tools.get_email(
        message_id=message_id,
        account_id=account_id
    )


@mcp.tool()
async def mark_email_as_read(
    message_id: str,
    account_id: str = None
):
    """
    Mark an email as read.

    Removes the UNREAD label from the specified email.
    """
    return await gmail_tools.mark_as_read(
        message_id=message_id,
        account_id=account_id
    )


@mcp.tool()
async def mark_email_as_unread(
    message_id: str,
    account_id: str = None
):
    """
    Mark an email as unread.

    Adds the UNREAD label to the specified email.
    """
    return await gmail_tools.mark_as_unread(
        message_id=message_id,
        account_id=account_id
    )


@mcp.tool()
async def add_email_label(
    message_id: str,
    label: str,
    account_id: str = None
):
    """
    Add a label to an email.

    Common labels: STARRED, IMPORTANT, TRASH
    You can also use custom labels if they exist in your Gmail.
    """
    return await gmail_tools.add_label(
        message_id=message_id,
        label=label,
        account_id=account_id
    )


# Account management tools
@mcp.tool()
def list_gmail_accounts() -> dict:
    """
    List all authenticated Gmail accounts.

    Returns a list of account identifiers (emails) that are currently
    authenticated and can be used with the account_id parameter.
    """
    from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager

    accounts = gmail_account_manager.list_accounts()
    default = gmail_account_manager.default_account

    return {
        "accounts": accounts,
        "default_account": default,
        "count": len(accounts)
    }


@mcp.tool()
def add_gmail_account(account_id: str) -> dict:
    """
    Add a new Gmail account.

    This will initiate the OAuth2 flow to authenticate a new Gmail account.
    The account_id should be the email address or a unique identifier.

    Follow the browser instructions to complete authentication.
    """
    from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager

    try:
        gmail_account_manager.add_account(account_id)
        return {
            "success": True,
            "message": f"Account {account_id} added successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def set_default_gmail_account(account_id: str) -> dict:
    """
    Set the default Gmail account.

    This account will be used when no account_id is specified in other tools.
    """
    from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager

    try:
        gmail_account_manager.set_default_account(account_id)
        return {
            "success": True,
            "message": f"Default account set to {account_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============ Holded Tools ============

@mcp.tool()
async def holded_create_invoice(
    contact_id: str,
    items: list[dict],
    doc_type: str = "invoice",
    date: str = None,
    due_date: str = None,
    notes: str = None,
    tags: list[str] = None,
    payment_method: str = None
):
    """
    Create a new invoice in Holded.

    Items should be a list of dicts with: name, description, quantity, price, tax_rate, discount, product_id
    Date format: YYYY-MM-DD
    """
    return await holded_tools.create_invoice(
        contact_id=contact_id,
        items=items,
        doc_type=doc_type,
        date=date,
        due_date=due_date,
        notes=notes,
        tags=tags,
        payment_method=payment_method
    )


@mcp.tool()
async def holded_get_invoice(invoice_id: str):
    """
    Get detailed information about a specific invoice.

    Returns complete invoice details including items, amounts, and status.
    """
    return await holded_tools.get_invoice(invoice_id=invoice_id)


@mcp.tool()
async def holded_list_invoices(
    contact_id: str = None,
    status: str = None,
    doc_type: str = None,
    from_date: str = None,
    to_date: str = None,
    paid: bool = None,
    max_results: int = 10
):
    """
    List invoices from Holded with optional filters.

    Status options: draft, sent, paid, cancelled
    Doc type options: invoice, quote, proforma, delivery_note, etc.
    Date format: YYYY-MM-DD
    """
    return await holded_tools.list_invoices(
        contact_id=contact_id,
        status=status,
        doc_type=doc_type,
        from_date=from_date,
        to_date=to_date,
        paid=paid,
        max_results=max_results
    )


@mcp.tool()
async def holded_create_contact(
    name: str,
    email: str = None,
    phone: str = None,
    mobile: str = None,
    vat_number: str = None,
    type: str = "client",
    notes: str = None,
    billing_address: dict = None,
    shipping_address: dict = None,
    tags: list[str] = None
):
    """
    Create a new contact (customer or supplier) in Holded.

    Type options: client, supplier
    Address format: dict with keys: street, city, province, postal_code, country
    """
    return await holded_tools.create_contact(
        name=name,
        email=email,
        phone=phone,
        mobile=mobile,
        vat_number=vat_number,
        type=type,
        notes=notes,
        billing_address=billing_address,
        shipping_address=shipping_address,
        tags=tags
    )


@mcp.tool()
async def holded_get_contact(contact_id: str):
    """
    Get detailed information about a specific contact.

    Returns complete contact details including addresses and tax info.
    """
    return await holded_tools.get_contact(contact_id=contact_id)


@mcp.tool()
async def holded_list_contacts(
    contact_type: str = None,
    max_results: int = 100
):
    """
    List contacts from Holded.

    Type options: client, supplier (leave empty for all)
    """
    return await holded_tools.list_contacts(
        contact_type=contact_type,
        max_results=max_results
    )


@mcp.tool()
async def holded_list_products(
    active_only: bool = True,
    max_results: int = 100
):
    """
    List products from Holded.

    Returns products with pricing, tax info, and stock status.
    """
    return await holded_tools.list_products(
        active_only=active_only,
        max_results=max_results
    )


@mcp.tool()
async def holded_create_treasury_account(
    name: str,
    iban: str | None = None,
    swift: str | None = None,
    bank_name: str | None = None,
    accounting_account_number: str | None = None,
    initial_balance: float = 0.0,
    type: str = "bank",
    notes: str | None = None
):
    """
    Create a new treasury account in Holded.

    Treasury accounts represent bank accounts, cash accounts, or other payment methods.
    """
    return await holded_tools.create_treasury_account(
        name=name,
        iban=iban,
        swift=swift,
        bank_name=bank_name,
        accounting_account_number=accounting_account_number,
        initial_balance=initial_balance,
        type=type,
        notes=notes
    )


@mcp.tool()
async def holded_get_treasury_account(treasury_id: str):
    """
    Get detailed information about a specific treasury account.

    Returns account details including balance, IBAN, and bank information.
    """
    return await holded_tools.get_treasury_account(treasury_id=treasury_id)


@mcp.tool()
async def holded_list_treasury_accounts(max_results: int = 100):
    """
    List treasury accounts from Holded.

    Returns all treasury accounts with their balances and details.
    """
    return await holded_tools.list_treasury_accounts(max_results=max_results)


@mcp.tool()
async def holded_list_expense_accounts(max_results: int = 100):
    """
    List expense accounts from Holded.

    Returns expense accounts from the chart of accounts with balances.
    """
    return await holded_tools.list_expense_accounts(max_results=max_results)


@mcp.tool()
async def holded_get_expense_account(account_id: str):
    """
    Get detailed information about a specific expense account.

    Returns account details including account number and balance.
    """
    return await holded_tools.get_expense_account(account_id=account_id)


@mcp.tool()
async def holded_list_income_accounts(max_results: int = 100):
    """
    List income accounts from Holded.

    Returns income accounts from the chart of accounts with balances.
    """
    return await holded_tools.list_income_accounts(max_results=max_results)


@mcp.tool()
async def holded_get_income_account(account_id: str):
    """
    Get detailed information about a specific income account.

    Returns account details including account number and balance.
    """
    return await holded_tools.get_income_account(account_id=account_id)


# ============ Notion Tools ============

@mcp.tool()
async def notion_create_page(
    title: str,
    parent_id: str,
    parent_type: str = "page_id",
    properties: dict = None,
    children: list = None,
    icon: dict = None,
    cover: dict = None
):
    """
    Create a new page in Notion.

    Parent types: page_id, database_id, workspace
    Properties are optional for regular pages, required for database pages.
    Children are initial content blocks.
    """
    return await notion_tools.create_page(
        title=title,
        parent_id=parent_id,
        parent_type=parent_type,
        properties=properties,
        children=children,
        icon=icon,
        cover=cover
    )


@mcp.tool()
async def notion_get_page(page_id: str):
    """
    Get detailed information about a Notion page.

    Returns page details including title, properties, and metadata.
    """
    return await notion_tools.get_page(page_id=page_id)


@mcp.tool()
async def notion_update_page(
    page_id: str,
    properties: dict = None,
    archived: bool = None,
    icon: dict = None,
    cover: dict = None
):
    """
    Update a Notion page.

    Can update properties, archive status, icon, or cover.
    Only provide the fields you want to update.
    """
    return await notion_tools.update_page(
        page_id=page_id,
        properties=properties,
        archived=archived,
        icon=icon,
        cover=cover
    )


@mcp.tool()
async def notion_search(
    query: str = None,
    filter_type: str = None,
    sort_direction: str = "descending",
    sort_timestamp: str = "last_edited_time",
    max_results: int = 100
):
    """
    Search for pages in Notion workspace.

    Filter types: page, database
    Sort timestamps: last_edited_time, created_time
    Sort directions: ascending, descending
    """
    return await notion_tools.search_pages(
        query=query,
        filter_type=filter_type,
        sort_direction=sort_direction,
        sort_timestamp=sort_timestamp,
        max_results=max_results
    )


@mcp.tool()
async def notion_create_database_entry(
    database_id: str,
    properties: dict,
    icon: dict = None,
    cover: dict = None,
    children: list = None
):
    """
    Create a new entry in a Notion database.

    Properties must match the database schema.
    Example property format:
    {
        "Name": {"title": [{"text": {"content": "Task name"}}]},
        "Status": {"select": {"name": "In Progress"}},
        "Due Date": {"date": {"start": "2025-01-15"}}
    }
    """
    return await notion_tools.create_database_entry(
        database_id=database_id,
        properties=properties,
        icon=icon,
        cover=cover,
        children=children
    )


@mcp.tool()
async def notion_query_database(
    database_id: str,
    filter: dict = None,
    sorts: list = None,
    start_cursor: str = None,
    page_size: int = 100
):
    """
    Query a Notion database with filters and sorting.

    Filter example:
    {"property": "Status", "select": {"equals": "In Progress"}}

    Sorts example:
    [{"property": "Due Date", "direction": "ascending"}]
    """
    return await notion_tools.query_database(
        database_id=database_id,
        filter=filter,
        sorts=sorts,
        start_cursor=start_cursor,
        page_size=page_size
    )


@mcp.tool()
async def notion_append_content(
    page_id: str,
    blocks: list[dict]
):
    """
    Append content blocks to a Notion page.

    Block examples:
    [
        {
            "type": "paragraph",
            "content": {"rich_text": [{"type": "text", "text": {"content": "Hello"}}]}
        },
        {
            "type": "heading_1",
            "content": {"rich_text": [{"type": "text", "text": {"content": "Title"}}]}
        },
        {
            "type": "to_do",
            "content": {
                "rich_text": [{"type": "text", "text": {"content": "Task"}}],
                "checked": false
            }
        }
    ]

    Block types: paragraph, heading_1, heading_2, heading_3, bulleted_list_item,
                 numbered_list_item, to_do, toggle, quote, callout
    """
    return await notion_tools.append_content(
        page_id=page_id,
        blocks=blocks
    )


@mcp.tool()
async def notion_get_page_content(
    page_id: str,
    page_size: int = 100
):
    """
    Get content blocks from a Notion page.

    Returns all blocks (paragraphs, headings, lists, etc.) in the page.
    """
    return await notion_tools.get_page_content(
        page_id=page_id,
        page_size=page_size
    )


# ============ WhatsApp Tools ============

@mcp.tool()
async def whatsapp_send_text(
    to: str,
    text: str,
    preview_url: bool = False
):
    """
    Send a WhatsApp text message.

    The recipient phone number must be in E.164 format (with country code).
    Example: +14155552671 for a US number.

    Text can be up to 4096 characters.
    Set preview_url=True to show link previews for URLs in the message.
    """
    return await whatsapp_tools().send_text_message(
        to=to,
        text=text,
        preview_url=preview_url
    )


@mcp.tool()
async def whatsapp_send_image(
    to: str,
    image_url: str = None,
    image_path: str = None,
    caption: str = None
):
    """
    Send an image via WhatsApp.

    Provide EITHER image_url (publicly accessible URL) OR image_path (local file).
    Do not provide both.

    Supported formats: JPG, PNG
    Maximum size: 5MB
    Caption max: 1024 characters

    Phone number must be in E.164 format (+14155552671).
    """
    return await whatsapp_tools().send_image(
        to=to,
        image_url=image_url,
        image_path=image_path,
        caption=caption
    )


@mcp.tool()
async def whatsapp_send_document(
    to: str,
    document_url: str = None,
    document_path: str = None,
    filename: str = None,
    caption: str = None
):
    """
    Send a document via WhatsApp.

    Provide EITHER document_url OR document_path.

    Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, and more
    Maximum size: 100MB
    Caption max: 1024 characters

    The filename will be displayed in WhatsApp.
    Phone number must be in E.164 format.
    """
    return await whatsapp_tools().send_document(
        to=to,
        document_url=document_url,
        document_path=document_path,
        filename=filename,
        caption=caption
    )


@mcp.tool()
async def whatsapp_send_template(
    to: str,
    template_name: str,
    language: str = "en_US",
    parameters: list[str] = None
):
    """
    Send a pre-approved WhatsApp template message.

    Templates must be approved by Meta before they can be used.
    Use whatsapp_list_templates to see available templates.

    Parameters must match the template structure (e.g., ["John", "123"]).
    Language codes: en_US, es_ES, pt_BR, etc.

    Phone number must be in E.164 format.
    """
    return await whatsapp_tools().send_template(
        to=to,
        template_name=template_name,
        language=language,
        parameters=parameters or []
    )


@mcp.tool()
async def whatsapp_list_templates(status_filter: str = None):
    """
    List all WhatsApp message templates.

    Status filter options: APPROVED, PENDING, REJECTED
    Leave empty to see all templates.

    Only APPROVED templates can be used to send messages.
    Templates must be created and approved in Meta Business Manager.
    """
    return await whatsapp_tools().list_templates(status_filter=status_filter)


@mcp.tool()
async def whatsapp_download_media(
    media_id: str,
    save_path: str = None
):
    """
    Download media from a WhatsApp message.

    Media ID is provided in incoming webhook messages.
    If save_path is provided, file will be saved locally.
    Otherwise, returns media data for processing.

    Useful for downloading images, videos, documents, or audio
    received in WhatsApp messages.
    """
    return await whatsapp_tools().download_media(
        media_id=media_id,
        save_path=save_path
    )


# Add a prompt for common email workflows
@mcp.prompt()
def email_assistant():
    """Helpful email management assistant prompt."""
    from mcp.server.fastmcp.prompts import base

    return [
        base.UserMessage(
            "You are a helpful email management assistant. "
            "I can help you with:\n"
            "- Searching emails with various filters\n"
            "- Reading email content\n"
            "- Sending emails (plain text or HTML)\n"
            "- Managing labels (read/unread, starred, etc.)\n"
            "- Working with multiple Gmail accounts\n\n"
            "What would you like to do with your emails?"
        )
    ]


@mcp.prompt()
def holded_assistant():
    """Helpful Holded business management assistant prompt."""
    from mcp.server.fastmcp.prompts import base

    return [
        base.UserMessage(
            "You are a helpful Holded business management assistant. "
            "I can help you with:\n"
            "- Creating and managing invoices, quotes, and proformas\n"
            "- Managing customer and supplier contacts\n"
            "- Viewing product catalog with pricing\n"
            "- Filtering invoices by status, date, contact, etc.\n"
            "- Creating contacts with full address and tax information\n"
            "- Managing treasury accounts (bank accounts, cash accounts)\n"
            "- Viewing expense and income accounts from the chart of accounts\n"
            "- Checking account balances and financial information\n\n"
            "What would you like to do with your Holded account?"
        )
    ]


@mcp.prompt()
def notion_assistant():
    """Helpful Notion workspace management assistant prompt."""
    from mcp.server.fastmcp.prompts import base

    return [
        base.UserMessage(
            "You are a helpful Notion workspace management assistant. "
            "I can help you with:\n"
            "- Creating and updating pages\n"
            "- Searching across your Notion workspace\n"
            "- Managing database entries (create, query, filter)\n"
            "- Adding content to pages (paragraphs, headings, lists, to-dos)\n"
            "- Querying databases with complex filters and sorting\n"
            "- Organizing your workspace with parent-child page hierarchies\n"
            "- Working with page properties and metadata\n\n"
            "What would you like to do with your Notion workspace?"
        )
    ]


@mcp.prompt()
def whatsapp_assistant():
    """Helpful WhatsApp Business assistant prompt."""
    from mcp.server.fastmcp.prompts import base

    return [
        base.UserMessage(
            "You are a helpful WhatsApp Business assistant. "
            "I can help you with:\n"
            "- Sending text messages to customers (phone numbers in E.164 format: +1234567890)\n"
            "- Sending images, documents, and other media\n"
            "- Using pre-approved message templates for notifications\n"
            "- Listing available message templates\n"
            "- Downloading media from incoming messages\n"
            "- All phone numbers must be in E.164 format (+country code + number)\n"
            "- Templates must be created and approved in Meta Business Manager before use\n\n"
            "What would you like to do with WhatsApp?"
        )
    ]


def main():
    """Main entry point."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Transport: {settings.mcp_transport}")
    print("-" * 50)

    # Run the MCP server
    mcp.run(transport=settings.mcp_transport)


if __name__ == "__main__":
    main()
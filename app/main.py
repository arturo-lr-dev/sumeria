from app.config.settings import settings

"""
Main MCP Server implementation.
Registers all tools and configures the server.
"""
from fastmcp import FastMCP
from app.config.settings import settings
from app.config.mcp_config import mcp_config
from app.mcp.tools.gmail_tools import gmail_tools


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


def main():
    """Main entry point."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Transport: {settings.mcp_transport}")
    print("-" * 50)

    # Run the MCP server
    mcp.run(transport=settings.mcp_transport)


if __name__ == "__main__":
    main()
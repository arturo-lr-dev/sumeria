"""
MCP Server specific configuration.
"""
from mcp.server.fastmcp import Icon
from typing import Optional


class MCPConfig:
    """MCP Server configuration."""

    # Server metadata
    SERVER_NAME = "Sumeria Personal Assistant"
    SERVER_VERSION = "1.0.0"

    # Server icon (optional)
    SERVER_ICON: Optional[Icon] = None

    # Tool configurations
    GMAIL_TOOLS_ENABLED = True
    NOTION_TOOLS_ENABLED = False  # Future implementation
    CALENDAR_TOOLS_ENABLED = False  # Future implementation
    WHATSAPP_TOOLS_ENABLED = False  # Future implementation

    # Rate limiting (requests per minute)
    GMAIL_RATE_LIMIT = 60

    # Timeouts (seconds)
    DEFAULT_TIMEOUT = 30
    GMAIL_API_TIMEOUT = 10


mcp_config = MCPConfig()

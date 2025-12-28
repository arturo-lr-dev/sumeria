#!/bin/bash
source .venv/bin/activate

# Add project root to PYTHONPATH so 'app' module can be imported
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)"

# Run the MCP server with HTTP transport
# --no-auth disables SSO authentication (we only need Gmail OAuth)
fastmcp run app/main.py:mcp --transport http --port 8000

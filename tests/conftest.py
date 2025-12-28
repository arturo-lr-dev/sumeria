"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
from pathlib import Path

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from unittest.mock import MagicMock
    settings = MagicMock()
    settings.gmail_credentials_file = Path("/tmp/credentials.json")
    settings.gmail_tokens_dir = Path("/tmp/tokens")
    settings.gmail_default_account = "test@example.com"
    settings.gmail_scopes = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    return settings

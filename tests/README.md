# Sumeria Tests

Comprehensive test suite for the Sumeria Personal Assistant MCP server.

## Structure

```
tests/
├── unit/               # Unit tests for individual components
│   ├── infrastructure/ # Infrastructure layer tests
│   │   └── connectors/
│   │       └── gmail/  # Gmail connector tests
│   ├── application/    # Application layer tests
│   │   └── use_cases/
│   │       └── gmail/  # Gmail use cases tests
│   └── mcp/           # MCP tools tests
│       └── tools/
├── integration/       # Integration tests for complete flows
├── e2e/              # End-to-end tests
└── fixtures/         # Test data and fixtures
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Gmail tests only
pytest -m gmail

# Run with coverage
pytest --cov=app --cov-report=html
```

### Run specific test files
```bash
# Test Gmail client
pytest tests/unit/infrastructure/connectors/gmail/test_client.py

# Test Gmail tools
pytest tests/unit/mcp/tools/test_gmail_tools.py
```

### Run specific test functions
```bash
pytest tests/unit/infrastructure/connectors/gmail/test_client.py::TestGmailClient::test_send_email_success
```

## Test Coverage

Generate coverage report:
```bash
pytest --cov=app --cov-report=html
```

View HTML report:
```bash
open htmlcov/index.html
```

## Gmail Tests

### Unit Tests

#### Infrastructure Layer
- **test_schemas.py**: Tests for Gmail message mapping and schema conversion
- **test_oauth.py**: Tests for OAuth authentication handling
- **test_client.py**: Tests for Gmail API client operations
- **test_account_manager.py**: Tests for multi-account management

#### Application Layer
- **test_send_email.py**: Tests for send email use case
- **test_search_emails.py**: Tests for search emails use case
- **test_get_email.py**: Tests for get email use case
- **test_manage_labels.py**: Tests for label management use cases

#### MCP Layer
- **test_gmail_tools.py**: Tests for Gmail MCP tools

### Integration Tests
- **test_gmail_flow.py**: End-to-end flow tests for Gmail functionality

## Writing Tests

### Test Conventions

1. **File naming**: `test_<module_name>.py`
2. **Class naming**: `Test<ClassName>`
3. **Function naming**: `test_<description>`
4. **Use fixtures**: Leverage pytest fixtures for setup
5. **Mock external services**: Use `unittest.mock` for API calls
6. **Async tests**: Mark with `@pytest.mark.asyncio`

### Example Test

```python
import pytest
from unittest.mock import MagicMock, AsyncMock

class TestMyFeature:
    """Test suite for my feature."""

    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        client = MagicMock()
        client.some_method = AsyncMock(return_value="result")
        return client

    @pytest.mark.asyncio
    async def test_my_feature(self, mock_client):
        """Test my feature works correctly."""
        result = await mock_client.some_method()
        assert result == "result"
```

## Fixtures

Common fixtures are defined in:
- `tests/conftest.py`: Global fixtures
- `tests/fixtures/gmail_fixtures.py`: Gmail-specific test data

## Continuous Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Scheduled nightly builds

## Troubleshooting

### Import Errors
Ensure you're running tests from the project root:
```bash
cd /path/to/sumeria
pytest
```

### Async Test Issues
Make sure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Coverage Issues
Install coverage dependencies:
```bash
pip install pytest-cov
```

## Dependencies

Test dependencies are listed in `pyproject.toml` under `[project.optional-dependencies]`:
- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock

Install test dependencies:
```bash
pip install -e ".[test]"
```

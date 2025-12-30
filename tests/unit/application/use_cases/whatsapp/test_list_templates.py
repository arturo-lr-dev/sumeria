"""
Unit tests for ListTemplates use case.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from app.application.use_cases.whatsapp.list_templates import (
    ListTemplatesUseCase,
    ListTemplatesRequest,
    ListTemplatesResponse
)
from tests.fixtures.whatsapp_fixtures import SAMPLE_TEMPLATES_RESPONSE


class TestListTemplatesUseCase:
    """Test suite for ListTemplates use case."""

    @pytest.fixture
    def mock_client(self):
        """Create mock WhatsApp client."""
        client = MagicMock()
        client.list_templates = AsyncMock(return_value=SAMPLE_TEMPLATES_RESPONSE["data"])
        return client

    @pytest.fixture
    def use_case(self, mock_client):
        """Create use case instance."""
        return ListTemplatesUseCase(client=mock_client)

    @pytest.mark.asyncio
    async def test_list_all_templates(self, use_case, mock_client):
        """Test listing all templates without filter."""
        # Arrange
        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        assert len(response.templates) == 2
        assert response.error is None
        mock_client.list_templates.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_templates_filter_approved(self, use_case, mock_client):
        """Test listing only approved templates."""
        # Arrange
        request = ListTemplatesRequest(status_filter="APPROVED")

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        approved_templates = [t for t in response.templates if t.status == "APPROVED"]
        assert len(approved_templates) == 1
        assert approved_templates[0].name == "order_confirmation"

    @pytest.mark.asyncio
    async def test_list_templates_filter_pending(self, use_case, mock_client):
        """Test listing only pending templates."""
        # Arrange
        request = ListTemplatesRequest(status_filter="PENDING")

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        pending_templates = [t for t in response.templates if t.status == "PENDING"]
        assert len(pending_templates) == 1
        assert pending_templates[0].name == "appointment_reminder"

    @pytest.mark.asyncio
    async def test_list_templates_filter_rejected(self, use_case, mock_client):
        """Test listing rejected templates."""
        # Arrange
        request = ListTemplatesRequest(status_filter="REJECTED")

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        rejected_templates = [t for t in response.templates if t.status == "REJECTED"]
        assert len(rejected_templates) == 0  # No rejected templates in sample data

    @pytest.mark.asyncio
    async def test_list_templates_empty_result(self, use_case, mock_client):
        """Test when no templates are returned."""
        # Arrange
        mock_client.list_templates.return_value = []
        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        assert len(response.templates) == 0

    @pytest.mark.asyncio
    async def test_list_templates_with_components(self, use_case, mock_client):
        """Test that templates include component information."""
        # Arrange
        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        template_with_components = response.templates[0]
        assert len(template_with_components.components) == 3
        assert template_with_components.components[0].type == "HEADER"
        assert template_with_components.components[1].type == "BODY"
        assert template_with_components.components[2].type == "FOOTER"

    @pytest.mark.asyncio
    async def test_list_templates_categories(self, use_case, mock_client):
        """Test that templates include category information."""
        # Arrange
        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        for template in response.templates:
            assert template.category in ["MARKETING", "UTILITY", "AUTHENTICATION"]

    @pytest.mark.asyncio
    async def test_list_templates_languages(self, use_case, mock_client):
        """Test that templates include language information."""
        # Arrange
        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        for template in response.templates:
            assert template.language is not None
            assert "_" in template.language  # e.g., en_US, es_ES

    @pytest.mark.asyncio
    async def test_list_templates_failure(self, use_case, mock_client):
        """Test handling of template listing failure."""
        # Arrange
        mock_client.list_templates.side_effect = Exception("API error: Unauthorized")

        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert len(response.templates) == 0
        assert "API error" in response.error

    @pytest.mark.asyncio
    async def test_list_templates_network_error(self, use_case, mock_client):
        """Test handling of network errors."""
        # Arrange
        mock_client.list_templates.side_effect = Exception("Connection timeout")

        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is False
        assert "Connection timeout" in response.error

    @pytest.mark.asyncio
    async def test_list_templates_parameter_count(self, use_case, mock_client):
        """Test that parameter count is correctly calculated."""
        # Arrange
        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        # order_confirmation template has 3 parameters: {{1}}, {{2}}, {{3}}
        template = next(t for t in response.templates if t.name == "order_confirmation")
        param_count = template.get_parameter_count()
        assert param_count == 3

    @pytest.mark.asyncio
    async def test_list_templates_approved_check(self, use_case, mock_client):
        """Test is_approved() method on templates."""
        # Arrange
        request = ListTemplatesRequest()

        # Act
        response = await use_case.execute(request)

        # Assert
        assert response.success is True
        approved = next(t for t in response.templates if t.name == "order_confirmation")
        pending = next(t for t in response.templates if t.name == "appointment_reminder")
        assert approved.is_approved() is True
        assert pending.is_approved() is False

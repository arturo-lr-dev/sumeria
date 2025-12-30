"""
List WhatsApp templates use case.
Retrieves all message templates for the WhatsApp Business account.
"""
from dataclasses import dataclass, field
from typing import Optional

from app.infrastructure.connectors.whatsapp.client import WhatsAppClient
from app.infrastructure.connectors.whatsapp.schemas import WhatsAppTemplateMapper
from app.domain.entities.whatsapp_template import WhatsAppTemplate


@dataclass
class ListTemplatesRequest:
    """
    Request to list message templates.

    Attributes:
        status_filter: Optional status filter (APPROVED, PENDING, REJECTED)
    """
    status_filter: Optional[str] = None


@dataclass
class ListTemplatesResponse:
    """
    Response with templates list.

    Attributes:
        success: Whether the request was successful
        templates: List of WhatsAppTemplate entities
        count: Number of templates returned
        error: Error message if failed
    """
    success: bool
    templates: list[WhatsAppTemplate] = field(default_factory=list)
    count: int = 0
    error: Optional[str] = None


class ListTemplatesUseCase:
    """
    Use case for listing WhatsApp message templates.

    Retrieves all templates and optionally filters by status.
    """

    def __init__(self, client: Optional[WhatsAppClient] = None):
        """
        Initialize use case.

        Args:
            client: WhatsAppClient instance (creates new if not provided)
        """
        self.client = client or WhatsAppClient()

    async def execute(
        self,
        request: ListTemplatesRequest
    ) -> ListTemplatesResponse:
        """
        Execute the use case to list templates.

        Args:
            request: List templates request

        Returns:
            Response with templates list or error
        """
        try:
            # Validate status filter if provided
            if request.status_filter:
                valid_statuses = ['APPROVED', 'PENDING', 'REJECTED']
                if request.status_filter not in valid_statuses:
                    return ListTemplatesResponse(
                        success=False,
                        error=f"Invalid status_filter. Must be one of: {valid_statuses}"
                    )

            # Get templates from API
            api_templates = await self.client.list_templates()

            # Convert to domain entities
            templates = WhatsAppTemplateMapper.to_template_list(api_templates)

            # Filter by status if requested
            if request.status_filter:
                templates = [
                    t for t in templates
                    if t.status == request.status_filter
                ]

            return ListTemplatesResponse(
                success=True,
                templates=templates,
                count=len(templates)
            )

        except Exception as e:
            return ListTemplatesResponse(
                success=False,
                error=str(e)
            )

"""
WhatsApp message template domain entities.
Represents WhatsApp Business message templates (pre-approved by Meta).
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WhatsAppTemplateComponent:
    """
    Represents a component of a WhatsApp message template.

    Templates consist of multiple components like HEADER, BODY, FOOTER, BUTTONS.
    Each component can have parameters that are filled when sending the message.

    Attributes:
        type: Component type (HEADER, BODY, FOOTER, BUTTONS)
        text: Component text content (with {{1}}, {{2}} placeholders)
        parameters: List of parameter placeholders
        format: Format of the component (TEXT, IMAGE, VIDEO, DOCUMENT for headers)
    """
    type: str  # HEADER, BODY, FOOTER, BUTTONS
    text: Optional[str] = None
    parameters: list[str] = field(default_factory=list)
    format: Optional[str] = None  # TEXT, IMAGE, VIDEO, DOCUMENT (for headers)

    def __post_init__(self):
        """Validate component type."""
        valid_types = ['HEADER', 'BODY', 'FOOTER', 'BUTTONS']
        if self.type not in valid_types:
            raise ValueError(f"Invalid component type. Must be one of: {valid_types}")

    def get_parameter_count(self) -> int:
        """Get number of parameters in this component."""
        return len(self.parameters)

    def has_parameters(self) -> bool:
        """Check if component has parameters."""
        return len(self.parameters) > 0


@dataclass
class WhatsAppTemplate:
    """
    WhatsApp message template entity.

    Templates must be pre-approved by Meta before they can be used to send messages.
    They are used for customer notifications and marketing messages.

    Template Structure:
    - HEADER (optional): Title or media
    - BODY (required): Main message text with parameters {{1}}, {{2}}, etc.
    - FOOTER (optional): Additional info
    - BUTTONS (optional): Call-to-action or quick reply buttons

    Attributes:
        id: Template ID
        name: Template name (used when sending messages)
        language: Language code (e.g., en_US, es_ES, pt_BR)
        status: Approval status (APPROVED, PENDING, REJECTED)
        category: Template category (MARKETING, UTILITY, AUTHENTICATION)
        components: List of template components
        namespace: Template namespace (optional, from Meta)
    """
    id: str
    name: str
    language: str  # Language code: en_US, es_ES, etc.
    status: str  # APPROVED, PENDING, REJECTED
    category: str  # MARKETING, UTILITY, AUTHENTICATION
    components: list[WhatsAppTemplateComponent] = field(default_factory=list)
    namespace: Optional[str] = None

    def __post_init__(self):
        """Validate template data."""
        # Validate status
        valid_statuses = ['APPROVED', 'PENDING', 'REJECTED']
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        # Validate category
        valid_categories = ['MARKETING', 'UTILITY', 'AUTHENTICATION']
        if self.category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")

    def is_approved(self) -> bool:
        """Check if template is approved and ready to use."""
        return self.status == 'APPROVED'

    def is_pending(self) -> bool:
        """Check if template is pending approval."""
        return self.status == 'PENDING'

    def is_rejected(self) -> bool:
        """Check if template was rejected."""
        return self.status == 'REJECTED'

    def get_parameter_count(self) -> int:
        """
        Get total number of parameters needed for this template.

        Returns:
            Total count of all parameters across all components
        """
        return sum(component.get_parameter_count() for component in self.components)

    def get_body_component(self) -> Optional[WhatsAppTemplateComponent]:
        """Get the BODY component (required component)."""
        for component in self.components:
            if component.type == 'BODY':
                return component
        return None

    def get_header_component(self) -> Optional[WhatsAppTemplateComponent]:
        """Get the HEADER component (optional)."""
        for component in self.components:
            if component.type == 'HEADER':
                return component
        return None

    def get_footer_component(self) -> Optional[WhatsAppTemplateComponent]:
        """Get the FOOTER component (optional)."""
        for component in self.components:
            if component.type == 'FOOTER':
                return component
        return None

    def has_header(self) -> bool:
        """Check if template has a header."""
        return self.get_header_component() is not None

    def has_footer(self) -> bool:
        """Check if template has a footer."""
        return self.get_footer_component() is not None

    def has_buttons(self) -> bool:
        """Check if template has buttons."""
        return any(component.type == 'BUTTONS' for component in self.components)

    def validate_parameters(self, parameters: list[str]) -> bool:
        """
        Validate that provided parameters match template requirements.

        Args:
            parameters: List of parameter values

        Returns:
            True if parameters are valid

        Raises:
            ValueError: If parameter count doesn't match
        """
        required_count = self.get_parameter_count()
        provided_count = len(parameters)

        if provided_count != required_count:
            raise ValueError(
                f"Template '{self.name}' requires {required_count} parameters, "
                f"but {provided_count} were provided"
            )

        return True

    def get_description(self) -> str:
        """
        Get a human-readable description of the template.

        Returns:
            Description string with template details
        """
        param_count = self.get_parameter_count()
        components_info = ", ".join(c.type for c in self.components)

        return (
            f"Template '{self.name}' ({self.language}) - {self.status}\n"
            f"Category: {self.category}\n"
            f"Parameters: {param_count}\n"
            f"Components: {components_info}"
        )

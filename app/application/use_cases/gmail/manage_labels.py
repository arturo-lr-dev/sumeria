"""
Use case: Manage email labels (mark as read/unread, add labels).
"""
from dataclasses import dataclass
from typing import Optional
from app.infrastructure.connectors.gmail.account_manager import gmail_account_manager


@dataclass
class MarkAsReadRequest:
    """Request to mark email as read."""
    message_id: str
    account_id: Optional[str] = None


@dataclass
class MarkAsUnreadRequest:
    """Request to mark email as unread."""
    message_id: str
    account_id: Optional[str] = None


@dataclass
class AddLabelRequest:
    """Request to add label to email."""
    message_id: str
    label: str
    account_id: Optional[str] = None


@dataclass
class ManageLabelResponse:
    """Response for label management operations."""
    success: bool
    error: Optional[str] = None


class MarkAsReadUseCase:
    """Use case for marking email as read."""

    async def execute(self, request: MarkAsReadRequest) -> ManageLabelResponse:
        """Mark an email as read."""
        try:
            client = gmail_account_manager.get_client(request.account_id)
            await client.mark_as_read(request.message_id)
            return ManageLabelResponse(success=True)
        except Exception as e:
            return ManageLabelResponse(success=False, error=str(e))


class MarkAsUnreadUseCase:
    """Use case for marking email as unread."""

    async def execute(self, request: MarkAsUnreadRequest) -> ManageLabelResponse:
        """Mark an email as unread."""
        try:
            client = gmail_account_manager.get_client(request.account_id)
            await client.mark_as_unread(request.message_id)
            return ManageLabelResponse(success=True)
        except Exception as e:
            return ManageLabelResponse(success=False, error=str(e))


class AddLabelUseCase:
    """Use case for adding label to email."""

    async def execute(self, request: AddLabelRequest) -> ManageLabelResponse:
        """Add a label to an email."""
        try:
            client = gmail_account_manager.get_client(request.account_id)
            await client.add_label(request.message_id, request.label)
            return ManageLabelResponse(success=True)
        except Exception as e:
            return ManageLabelResponse(success=False, error=str(e))

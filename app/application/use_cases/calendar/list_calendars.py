"""
Use case: List available calendars.
Supports both Google Calendar and Apple Calendar.
"""
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.calendar import Calendar


@dataclass
class ListCalendarsRequest:
    """Request to list calendars."""
    provider: str = "google"  # google or apple
    account_id: Optional[str] = None


@dataclass
class ListCalendarsResponse:
    """Response with list of calendars."""
    success: bool
    calendars: list[Calendar] = None
    error: Optional[str] = None


class ListCalendarsUseCase:
    """Use case for listing calendars."""

    async def execute(self, request: ListCalendarsRequest) -> ListCalendarsResponse:
        """
        List available calendars.

        Args:
            request: List calendars request

        Returns:
            ListCalendarsResponse with calendars
        """
        try:
            # Choose provider
            if request.provider == "google":
                from app.infrastructure.connectors.google_calendar.account_manager import (
                    google_calendar_account_manager
                )
                client = google_calendar_account_manager.get_client(request.account_id)
            else:  # apple
                from app.infrastructure.connectors.apple_calendar.client import (
                    AppleCalendarClient
                )
                client = AppleCalendarClient(account_id=request.account_id or "default")

            # List calendars
            calendars = await client.list_calendars()

            return ListCalendarsResponse(
                success=True,
                calendars=calendars if calendars else []
            )

        except Exception as e:
            return ListCalendarsResponse(
                success=False,
                calendars=[],
                error=str(e)
            )

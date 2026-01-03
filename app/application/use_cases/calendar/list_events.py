"""
Use case: List calendar events.
Supports both Google Calendar and Apple Calendar.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from app.domain.entities.calendar_event import CalendarEvent, EventSearchCriteria


@dataclass
class ListEventsRequest:
    """Request to list calendar events."""
    calendar_id: str = "primary"
    time_min: Optional[datetime] = None
    time_max: Optional[datetime] = None
    query: Optional[str] = None
    max_results: int = 10
    provider: str = "google"  # google or apple
    account_id: Optional[str] = None


@dataclass
class ListEventsResponse:
    """Response with list of events."""
    success: bool
    events: list[CalendarEvent] = None
    count: int = 0
    error: Optional[str] = None


class ListEventsUseCase:
    """Use case for listing calendar events."""

    async def execute(self, request: ListEventsRequest) -> ListEventsResponse:
        """
        List calendar events.

        Args:
            request: List events request

        Returns:
            ListEventsResponse with events
        """
        try:
            # Build search criteria
            criteria = EventSearchCriteria(
                calendar_id=request.calendar_id,
                time_min=request.time_min,
                time_max=request.time_max,
                query=request.query,
                max_results=request.max_results
            )

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

            # List events
            events = await client.list_events(criteria)

            return ListEventsResponse(
                success=True,
                events=events,
                count=len(events)
            )

        except Exception as e:
            return ListEventsResponse(
                success=False,
                events=[],
                count=0,
                error=str(e)
            )

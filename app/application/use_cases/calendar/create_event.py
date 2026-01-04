"""
Use case: Create a calendar event.
Supports both Google Calendar and Apple Calendar.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from app.domain.entities.calendar_event import (
    CalendarEventDraft,
    EventDateTime,
    CalendarAttendee,
    EventReminder,
    EventRecurrence
)
from app.domain.entities.calendar import CalendarProvider


@dataclass
class CreateEventRequest:
    """Request to create a calendar event."""
    summary: str
    start_datetime: Optional[datetime] = None
    start_date: Optional[str] = None
    end_datetime: Optional[datetime] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: list[str] = field(default_factory=list)
    reminders_minutes: list[int] = field(default_factory=list)
    calendar_id: str = "primary"
    account_id: Optional[str] = None
    provider: str = "google"  # google or apple


@dataclass
class CreateEventResponse:
    """Response after creating an event."""
    success: bool
    event_id: Optional[str] = None
    html_link: Optional[str] = None
    error: Optional[str] = None


class CreateEventUseCase:
    """Use case for creating calendar events."""

    async def execute(self, request: CreateEventRequest) -> CreateEventResponse:
        """
        Create a calendar event.

        Args:
            request: Create event request

        Returns:
            CreateEventResponse with result
        """
        try:
            # Build event draft
            draft = CalendarEventDraft(
                summary=request.summary,
                start=EventDateTime(
                    datetime=request.start_datetime,
                    date=request.start_date
                ),
                end=EventDateTime(
                    datetime=request.end_datetime,
                    date=request.end_date
                ),
                description=request.description,
                location=request.location,
                attendees=[CalendarAttendee(email=e) for e in request.attendees],
                reminders=[EventReminder(minutes=m) for m in request.reminders_minutes]
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

            # Create event
            event_id = await client.create_event(request.calendar_id, draft)

            # Get event details for link
            try:
                event = await client.get_event(request.calendar_id, event_id)
                html_link = event.html_link
            except Exception:
                html_link = None

            return CreateEventResponse(
                success=True,
                event_id=event_id,
                html_link=html_link
            )

        except Exception as e:
            return CreateEventResponse(
                success=False,
                error=str(e)
            )

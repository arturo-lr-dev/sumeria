"""
MCP Tools for Calendar operations (Google Calendar & Apple Calendar).
Unified interface for both providers.
"""
from typing import Optional, Literal
from pydantic import BaseModel

from app.application.use_cases.calendar.create_event import (
    CreateEventUseCase,
    CreateEventRequest
)
from app.application.use_cases.calendar.list_events import (
    ListEventsUseCase,
    ListEventsRequest
)
from app.application.use_cases.calendar.list_calendars import (
    ListCalendarsUseCase,
    ListCalendarsRequest
)


class EventSummary(BaseModel):
    """Summary of a calendar event."""
    id: str
    summary: str
    start: str
    end: str
    location: Optional[str] = None
    attendees_count: int = 0
    is_recurring: bool = False
    html_link: Optional[str] = None


class CreateEventResult(BaseModel):
    """Result of creating an event."""
    success: bool
    event_id: Optional[str] = None
    html_link: Optional[str] = None
    error: Optional[str] = None


class ListEventsResult(BaseModel):
    """Result of listing events."""
    success: bool
    count: int
    events: list[EventSummary]
    error: Optional[str] = None


class CalendarSummary(BaseModel):
    """Summary of a calendar."""
    id: str
    name: str
    timezone: str
    provider: str
    is_primary: bool = False


class ListCalendarsResult(BaseModel):
    """Result of listing calendars."""
    success: bool
    calendars: list[CalendarSummary]
    error: Optional[str] = None


class CalendarTools:
    """Collection of unified Calendar MCP tools."""

    def __init__(self):
        """Initialize use cases."""
        self.create_event_uc = CreateEventUseCase()
        self.list_events_uc = ListEventsUseCase()
        self.list_calendars_uc = ListCalendarsUseCase()

    async def create_event(
        self,
        summary: str,
        start_datetime: Optional[str] = None,
        start_date: Optional[str] = None,
        end_datetime: Optional[str] = None,
        end_date: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        reminders_minutes: Optional[list[int]] = None,
        calendar_id: str = "primary",
        provider: Literal["google", "apple"] = "google",
        account_id: Optional[str] = None
    ) -> CreateEventResult:
        """
        Create a calendar event.

        Args:
            summary: Event title
            start_datetime: Start datetime in ISO format (for timed events)
            start_date: Start date in YYYY-MM-DD format (for all-day events)
            end_datetime: End datetime in ISO format
            end_date: End date in YYYY-MM-DD format
            description: Event description (optional)
            location: Event location (optional)
            attendees: List of attendee emails (optional)
            reminders_minutes: List of reminder times in minutes before event (optional)
            calendar_id: Calendar ID (default: 'primary')
            provider: Calendar provider ('google' or 'apple')
            account_id: Account to use (optional, uses default if not specified)

        Returns:
            CreateEventResult with success status and event details
        """
        from datetime import datetime as dt

        # Parse datetimes
        start_dt = dt.fromisoformat(start_datetime) if start_datetime else None
        end_dt = dt.fromisoformat(end_datetime) if end_datetime else None

        request = CreateEventRequest(
            summary=summary,
            start_datetime=start_dt,
            start_date=start_date,
            end_datetime=end_dt,
            end_date=end_date,
            description=description,
            location=location,
            attendees=attendees or [],
            reminders_minutes=reminders_minutes or [30],
            calendar_id=calendar_id,
            provider=provider,
            account_id=account_id
        )

        response = await self.create_event_uc.execute(request)

        return CreateEventResult(
            success=response.success,
            event_id=response.event_id,
            html_link=response.html_link,
            error=response.error
        )

    async def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        query: Optional[str] = None,
        max_results: int = 10,
        provider: Literal["google", "apple"] = "google",
        account_id: Optional[str] = None
    ) -> ListEventsResult:
        """
        List calendar events.

        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start of time range (ISO format)
            time_max: End of time range (ISO format)
            query: Search query (optional)
            max_results: Maximum number of results (default: 10)
            provider: Calendar provider ('google' or 'apple')
            account_id: Account to use (optional)

        Returns:
            ListEventsResult with matching events
        """
        from datetime import datetime as dt

        time_min_dt = dt.fromisoformat(time_min) if time_min else None
        time_max_dt = dt.fromisoformat(time_max) if time_max else None

        request = ListEventsRequest(
            calendar_id=calendar_id,
            time_min=time_min_dt,
            time_max=time_max_dt,
            query=query,
            max_results=max_results,
            provider=provider,
            account_id=account_id
        )

        response = await self.list_events_uc.execute(request)

        # Convert to summaries
        events = []
        if response.events:
            for event in response.events:
                start_str = ""
                end_str = ""

                if event.start:
                    start_str = event.start.to_iso_string()
                if event.end:
                    end_str = event.end.to_iso_string()

                events.append(EventSummary(
                    id=event.id or "",
                    summary=event.summary,
                    start=start_str,
                    end=end_str,
                    location=event.location,
                    attendees_count=len(event.attendees),
                    is_recurring=event.recurrence is not None,
                    html_link=event.html_link
                ))

        return ListEventsResult(
            success=response.success,
            count=len(events),
            events=events,
            error=response.error
        )

    async def list_calendars(
        self,
        provider: Literal["google", "apple"] = "google",
        account_id: Optional[str] = None
    ) -> ListCalendarsResult:
        """
        List available calendars.

        Args:
            provider: Calendar provider ('google' or 'apple')
            account_id: Account to use (optional)

        Returns:
            ListCalendarsResult with available calendars
        """
        request = ListCalendarsRequest(
            provider=provider,
            account_id=account_id
        )

        response = await self.list_calendars_uc.execute(request)

        calendars = []
        if response.calendars:
            calendars = [
                CalendarSummary(
                    id=cal.id,
                    name=cal.summary,
                    timezone=cal.timezone,
                    provider=cal.provider.value,
                    is_primary=cal.is_primary
                )
                for cal in response.calendars
            ]

        return ListCalendarsResult(
            success=response.success,
            calendars=calendars,
            error=response.error
        )


# Global instance
calendar_tools = CalendarTools()

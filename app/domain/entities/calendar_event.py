"""
Calendar Event domain entities.
Represents calendar events with support for recurrence, attendees, and reminders.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum

from app.domain.entities.calendar import CalendarProvider


class AttendeeResponseStatus(str, Enum):
    """Attendee response status."""
    NEEDS_ACTION = "needsAction"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"


@dataclass
class EventDateTime:
    """Event date/time with timezone support."""
    datetime: Optional[datetime] = None
    date: Optional[str] = None  # For all-day events (YYYY-MM-DD)
    timezone: str = "UTC"

    def to_iso_string(self) -> str:
        """Convert to ISO string representation."""
        if self.datetime:
            return self.datetime.isoformat()
        elif self.date:
            return self.date
        return ""


@dataclass
class EventRecurrence:
    """Recurrence rule for events."""
    rrule: str  # RFC 5545 format
    exdates: list[datetime] = field(default_factory=list)  # Exception dates


@dataclass
class CalendarAttendee:
    """Event attendee entity."""
    email: str
    display_name: Optional[str] = None
    response_status: AttendeeResponseStatus = AttendeeResponseStatus.NEEDS_ACTION
    optional: bool = False
    organizer: bool = False
    comment: Optional[str] = None


@dataclass
class EventReminder:
    """Event reminder entity."""
    method: str = "popup"  # popup, email
    minutes: int = 30  # Minutes before event


@dataclass
class CalendarEventDraft:
    """Draft for creating a new calendar event."""
    summary: str  # Event title
    start: EventDateTime
    end: EventDateTime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: list[CalendarAttendee] = field(default_factory=list)
    reminders: list[EventReminder] = field(default_factory=list)
    recurrence: Optional[EventRecurrence] = None
    color_id: Optional[str] = None
    visibility: str = "default"  # default, public, private


@dataclass
class CalendarEvent:
    """Calendar event entity."""
    id: Optional[str] = None
    summary: str = ""
    start: Optional[EventDateTime] = None
    end: Optional[EventDateTime] = None
    description: Optional[str] = None
    location: Optional[str] = None
    creator: Optional[str] = None
    organizer: Optional[str] = None
    attendees: list[CalendarAttendee] = field(default_factory=list)
    reminders: list[EventReminder] = field(default_factory=list)
    recurrence: Optional[EventRecurrence] = None
    status: str = "confirmed"  # confirmed, tentative, cancelled
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    html_link: Optional[str] = None
    calendar_id: str = "primary"
    provider: CalendarProvider = CalendarProvider.GOOGLE


@dataclass
class EventSearchCriteria:
    """Search criteria for events."""
    calendar_id: str = "primary"
    query: Optional[str] = None
    time_min: Optional[datetime] = None
    time_max: Optional[datetime] = None
    show_deleted: bool = False
    single_events: bool = True  # Expand recurring events
    max_results: int = 100
    order_by: str = "startTime"  # startTime, updated

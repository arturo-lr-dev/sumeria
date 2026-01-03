"""
Apple Calendar (CalDAV) client implementation.
Uses caldav library for CalDAV protocol.
"""
from typing import Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

# CalDAV will be imported conditionally
try:
    import caldav
    from caldav.elements import dav, cdav
    CALDAV_AVAILABLE = True
except ImportError:
    CALDAV_AVAILABLE = False

from app.infrastructure.connectors.apple_calendar.auth import AppleCalendarAuthHandler
from app.domain.entities.calendar import Calendar
from app.domain.entities.calendar_event import (
    CalendarEvent,
    CalendarEventDraft,
    EventSearchCriteria
)


class AppleCalendarClient:
    """Apple Calendar (CalDAV) client for calendar operations."""

    def __init__(
        self,
        account_id: str,
        auth_handler: Optional[AppleCalendarAuthHandler] = None
    ):
        """
        Initialize Apple Calendar client.

        Args:
            account_id: Account identifier
            auth_handler: Auth handler (created if not provided)

        Raises:
            ImportError: If caldav library is not installed
        """
        if not CALDAV_AVAILABLE:
            raise ImportError(
                "caldav library is required for Apple Calendar support. "
                "Install it with: pip install caldav"
            )

        self.account_id = account_id
        self.auth_handler = auth_handler or AppleCalendarAuthHandler(account_id=account_id)
        self._client: Optional[caldav.DAVClient] = None
        self._principal = None

    def _get_client(self) -> caldav.DAVClient:
        """
        Get or create CalDAV client.

        Returns:
            CalDAV client instance
        """
        if self._client is None:
            username, password, url = self.auth_handler.load_credentials()
            self._client = caldav.DAVClient(
                url=url,
                username=username,
                password=password
            )
            self._principal = self._client.principal()
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def create_event(
        self,
        calendar_id: str,
        draft: CalendarEventDraft
    ) -> str:
        """
        Create a calendar event via CalDAV.

        Args:
            calendar_id: Calendar ID or 'primary'
            draft: Event draft

        Returns:
            Event ID (UID)

        Raises:
            Exception: If creation fails
        """
        try:
            from app.infrastructure.connectors.apple_calendar.schemas import AppleCalendarMapper

            client = self._get_client()

            # Get calendar
            calendar = self._get_caldav_calendar(calendar_id)

            # Create iCalendar event
            ical = AppleCalendarMapper.from_event_draft(draft)

            # Save to calendar
            event = calendar.save_event(ical.to_ical())

            # Extract UID from saved event
            return str(event.id) if hasattr(event, 'id') else str(event.url).split('/')[-1].replace('.ics', '')

        except Exception as error:
            raise Exception(f"Failed to create event: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> CalendarEvent:
        """
        Get a specific event by ID.

        Args:
            calendar_id: Calendar ID
            event_id: Event UID

        Returns:
            CalendarEvent entity

        Raises:
            Exception: If retrieval fails
        """
        try:
            from app.infrastructure.connectors.apple_calendar.schemas import AppleCalendarMapper

            calendar = self._get_caldav_calendar(calendar_id)
            event = calendar.event_by_uid(event_id)

            return AppleCalendarMapper.to_event_entity(event.data, calendar_id)

        except Exception as error:
            raise Exception(f"Failed to get event: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def update_event(
        self,
        calendar_id: str,
        event_id: str,
        draft: CalendarEventDraft
    ) -> None:
        """
        Update an existing event.

        Args:
            calendar_id: Calendar ID
            event_id: Event UID
            draft: Updated event data

        Raises:
            Exception: If update fails
        """
        try:
            from app.infrastructure.connectors.apple_calendar.schemas import AppleCalendarMapper

            calendar = self._get_caldav_calendar(calendar_id)
            event = calendar.event_by_uid(event_id)

            # Update with new data
            ical = AppleCalendarMapper.from_event_draft(draft, event_id)
            event.data = ical.to_ical()
            event.save()

        except Exception as error:
            raise Exception(f"Failed to update event: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def delete_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> None:
        """
        Delete an event.

        Args:
            calendar_id: Calendar ID
            event_id: Event UID

        Raises:
            Exception: If deletion fails
        """
        try:
            calendar = self._get_caldav_calendar(calendar_id)
            event = calendar.event_by_uid(event_id)
            event.delete()

        except Exception as error:
            raise Exception(f"Failed to delete event: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def list_events(
        self,
        criteria: EventSearchCriteria
    ) -> list[CalendarEvent]:
        """
        List events based on criteria.

        Args:
            criteria: Search criteria

        Returns:
            List of matching events

        Raises:
            Exception: If listing fails
        """
        try:
            from app.infrastructure.connectors.apple_calendar.schemas import AppleCalendarMapper

            calendar = self._get_caldav_calendar(criteria.calendar_id)

            # Date range search
            events = calendar.date_search(
                start=criteria.time_min,
                end=criteria.time_max,
                expand=criteria.single_events
            )

            result = []
            for event in events:
                try:
                    cal_event = AppleCalendarMapper.to_event_entity(event.data, criteria.calendar_id)

                    # Filter by query if provided
                    if criteria.query:
                        if criteria.query.lower() in cal_event.summary.lower():
                            result.append(cal_event)
                    else:
                        result.append(cal_event)

                    if len(result) >= criteria.max_results:
                        break
                except Exception:
                    # Skip events that fail to parse
                    continue

            return result

        except Exception as error:
            raise Exception(f"Failed to list events: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def list_calendars(self) -> list[Calendar]:
        """
        List all calendars for this account.

        Returns:
            List of calendars

        Raises:
            Exception: If listing fails
        """
        try:
            from app.infrastructure.connectors.apple_calendar.schemas import AppleCalendarMapper

            client = self._get_client()
            calendars = self._principal.calendars()

            result = []
            for cal in calendars:
                try:
                    result.append(AppleCalendarMapper.to_calendar_entity(cal))
                except Exception:
                    # Skip calendars that fail to parse
                    continue

            return result

        except Exception as error:
            raise Exception(f"Failed to list calendars: {error}")

    def _get_caldav_calendar(self, calendar_id: str):
        """
        Get CalDAV calendar by ID.

        Args:
            calendar_id: Calendar ID or 'primary'

        Returns:
            CalDAV calendar object

        Raises:
            ValueError: If calendar not found
        """
        if calendar_id == "primary":
            # Get default calendar
            calendars = self._principal.calendars()
            if not calendars:
                raise ValueError("No calendars found")
            return calendars[0]
        else:
            # Find calendar by ID or name
            for cal in self._principal.calendars():
                # Try matching by URL component or name
                if calendar_id in str(cal.url) or (hasattr(cal, 'name') and cal.name == calendar_id):
                    return cal

        raise ValueError(f"Calendar not found: {calendar_id}")

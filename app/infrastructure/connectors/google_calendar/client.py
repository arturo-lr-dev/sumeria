"""
Google Calendar API client implementation.
Handles all interactions with Google Calendar API.
"""
from typing import Optional
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.infrastructure.connectors.google_calendar.oauth import GoogleCalendarOAuthHandler
from app.domain.entities.calendar import Calendar
from app.domain.entities.calendar_event import (
    CalendarEvent,
    CalendarEventDraft,
    EventSearchCriteria
)


class GoogleCalendarClient:
    """
    Google Calendar API client for calendar operations.
    Handles authentication and API communication for a specific account.
    """

    def __init__(
        self,
        account_id: str,
        oauth_handler: Optional[GoogleCalendarOAuthHandler] = None
    ):
        """
        Initialize Google Calendar client for a specific account.

        Args:
            account_id: Google account identifier (email or alias)
            oauth_handler: OAuth handler for authentication (will be created if not provided)
        """
        self.account_id = account_id
        self.oauth_handler = oauth_handler or GoogleCalendarOAuthHandler(account_id=account_id)
        self._service = None

    def _get_service(self):
        """Get or create Google Calendar API service."""
        if self._service is None:
            creds = self.oauth_handler.get_credentials()
            self._service = build('calendar', 'v3', credentials=creds)
        return self._service

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
        Create a calendar event.

        Args:
            calendar_id: Calendar ID (use 'primary' for default)
            draft: Event draft

        Returns:
            Event ID

        Raises:
            Exception: If Google Calendar API request fails
        """
        try:
            from app.infrastructure.connectors.google_calendar.schemas import GoogleCalendarMapper

            service = self._get_service()
            event_data = GoogleCalendarMapper.from_event_draft(draft)

            event = service.events().insert(
                calendarId=calendar_id,
                body=event_data,
                sendUpdates='all'  # Send invitations to attendees
            ).execute()

            return event['id']

        except HttpError as error:
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
            event_id: Event ID

        Returns:
            CalendarEvent entity

        Raises:
            Exception: If Google Calendar API request fails
        """
        try:
            from app.infrastructure.connectors.google_calendar.schemas import GoogleCalendarMapper

            service = self._get_service()

            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            return GoogleCalendarMapper.to_event_entity(event)

        except HttpError as error:
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
            event_id: Event ID
            draft: Updated event data

        Raises:
            Exception: If Google Calendar API request fails
        """
        try:
            from app.infrastructure.connectors.google_calendar.schemas import GoogleCalendarMapper

            service = self._get_service()
            event_data = GoogleCalendarMapper.from_event_draft(draft)

            service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data,
                sendUpdates='all'
            ).execute()

        except HttpError as error:
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
            event_id: Event ID

        Raises:
            Exception: If Google Calendar API request fails
        """
        try:
            service = self._get_service()

            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()

        except HttpError as error:
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
            Exception: If Google Calendar API request fails
        """
        try:
            from app.infrastructure.connectors.google_calendar.schemas import GoogleCalendarMapper

            service = self._get_service()

            params = {
                'calendarId': criteria.calendar_id,
                'maxResults': criteria.max_results,
                'singleEvents': criteria.single_events,
                'orderBy': criteria.order_by
            }

            if criteria.time_min:
                params['timeMin'] = criteria.time_min.isoformat() + 'Z'
            if criteria.time_max:
                params['timeMax'] = criteria.time_max.isoformat() + 'Z'
            if criteria.query:
                params['q'] = criteria.query

            events_result = service.events().list(**params).execute()
            events = events_result.get('items', [])

            return [GoogleCalendarMapper.to_event_entity(e) for e in events]

        except HttpError as error:
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
            Exception: If Google Calendar API request fails
        """
        try:
            from app.infrastructure.connectors.google_calendar.schemas import GoogleCalendarMapper

            service = self._get_service()

            calendars_result = service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])

            return [GoogleCalendarMapper.to_calendar_entity(c) for c in calendars]

        except HttpError as error:
            raise Exception(f"Failed to list calendars: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_free_busy(
        self,
        calendar_ids: list[str],
        time_min: datetime,
        time_max: datetime
    ) -> dict:
        """
        Get free/busy information for calendars.

        Args:
            calendar_ids: List of calendar IDs
            time_min: Start of time range
            time_max: End of time range

        Returns:
            Free/busy data

        Raises:
            Exception: If Google Calendar API request fails
        """
        try:
            service = self._get_service()

            body = {
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'items': [{'id': cal_id} for cal_id in calendar_ids]
            }

            return service.freebusy().query(body=body).execute()

        except HttpError as error:
            raise Exception(f"Failed to get free/busy: {error}")

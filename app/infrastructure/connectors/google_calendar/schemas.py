"""
Mappers between Google Calendar API responses and domain entities.
"""
from datetime import datetime
from typing import Optional
from app.domain.entities.calendar import Calendar, CalendarProvider
from app.domain.entities.calendar_event import (
    CalendarEvent,
    CalendarEventDraft,
    EventDateTime,
    EventRecurrence,
    CalendarAttendee,
    EventReminder,
    AttendeeResponseStatus
)


class GoogleCalendarMapper:
    """Maps between Google Calendar API and domain entities."""

    @staticmethod
    def to_calendar_entity(api_data: dict) -> Calendar:
        """
        Convert Google Calendar API calendar to domain entity.

        Args:
            api_data: Calendar data from Google Calendar API

        Returns:
            Calendar entity
        """
        return Calendar(
            id=api_data['id'],
            summary=api_data.get('summary', ''),
            description=api_data.get('description'),
            timezone=api_data.get('timeZone', 'UTC'),
            provider=CalendarProvider.GOOGLE,
            is_primary=api_data.get('primary', False),
            color=api_data.get('backgroundColor'),
            access_role=api_data.get('accessRole')
        )

    @staticmethod
    def to_event_entity(api_data: dict) -> CalendarEvent:
        """
        Convert Google Calendar API event to domain entity.

        Args:
            api_data: Event data from Google Calendar API

        Returns:
            CalendarEvent entity
        """
        # Parse start/end times
        start = GoogleCalendarMapper._parse_event_datetime(api_data.get('start', {}))
        end = GoogleCalendarMapper._parse_event_datetime(api_data.get('end', {}))

        # Parse attendees
        attendees = [
            GoogleCalendarMapper._parse_attendee(att)
            for att in api_data.get('attendees', [])
        ]

        # Parse reminders
        reminders = []
        if 'reminders' in api_data and 'overrides' in api_data['reminders']:
            reminders = [
                EventReminder(
                    method=rem['method'],
                    minutes=rem['minutes']
                )
                for rem in api_data['reminders']['overrides']
            ]

        # Parse recurrence
        recurrence = None
        if 'recurrence' in api_data and api_data['recurrence']:
            recurrence = EventRecurrence(
                rrule=api_data['recurrence'][0]  # First rule
            )

        # Parse timestamps
        created = None
        if 'created' in api_data:
            created = datetime.fromisoformat(api_data['created'].replace('Z', '+00:00'))

        updated = None
        if 'updated' in api_data:
            updated = datetime.fromisoformat(api_data['updated'].replace('Z', '+00:00'))

        return CalendarEvent(
            id=api_data.get('id'),
            summary=api_data.get('summary', ''),
            start=start,
            end=end,
            description=api_data.get('description'),
            location=api_data.get('location'),
            creator=api_data.get('creator', {}).get('email'),
            organizer=api_data.get('organizer', {}).get('email'),
            attendees=attendees,
            reminders=reminders,
            recurrence=recurrence,
            status=api_data.get('status', 'confirmed'),
            created=created,
            updated=updated,
            html_link=api_data.get('htmlLink'),
            provider=CalendarProvider.GOOGLE
        )

    @staticmethod
    def from_event_draft(draft: CalendarEventDraft) -> dict:
        """
        Convert domain event draft to Google Calendar API format.

        Args:
            draft: CalendarEventDraft entity

        Returns:
            Dict in Google Calendar API format
        """
        event_data = {
            'summary': draft.summary,
            'start': GoogleCalendarMapper._format_event_datetime(draft.start),
            'end': GoogleCalendarMapper._format_event_datetime(draft.end),
        }

        if draft.description:
            event_data['description'] = draft.description
        if draft.location:
            event_data['location'] = draft.location

        if draft.attendees:
            event_data['attendees'] = [
                {
                    'email': att.email,
                    'optional': att.optional,
                    'displayName': att.display_name
                } if att.display_name else {
                    'email': att.email,
                    'optional': att.optional
                }
                for att in draft.attendees
            ]

        if draft.reminders:
            event_data['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': rem.method, 'minutes': rem.minutes}
                    for rem in draft.reminders
                ]
            }
        else:
            event_data['reminders'] = {'useDefault': True}

        if draft.recurrence:
            event_data['recurrence'] = [draft.recurrence.rrule]

        if draft.color_id:
            event_data['colorId'] = draft.color_id

        if draft.visibility:
            event_data['visibility'] = draft.visibility

        return event_data

    @staticmethod
    def _parse_event_datetime(data: dict) -> EventDateTime:
        """
        Parse event datetime from API response.

        Args:
            data: DateTime data from API

        Returns:
            EventDateTime entity
        """
        if 'dateTime' in data:
            dt = datetime.fromisoformat(data['dateTime'].replace('Z', '+00:00'))
            return EventDateTime(
                datetime=dt,
                timezone=data.get('timeZone', 'UTC')
            )
        elif 'date' in data:
            return EventDateTime(
                date=data['date'],
                timezone=data.get('timeZone', 'UTC')
            )
        return EventDateTime()

    @staticmethod
    def _format_event_datetime(dt: EventDateTime) -> dict:
        """
        Format event datetime for API request.

        Args:
            dt: EventDateTime entity

        Returns:
            Dict in Google Calendar API format
        """
        if dt.datetime:
            return {
                'dateTime': dt.datetime.isoformat(),
                'timeZone': dt.timezone
            }
        elif dt.date:
            return {'date': dt.date}
        return {}

    @staticmethod
    def _parse_attendee(data: dict) -> CalendarAttendee:
        """
        Parse attendee from API response.

        Args:
            data: Attendee data from API

        Returns:
            CalendarAttendee entity
        """
        response_status = data.get('responseStatus', 'needsAction')
        try:
            status = AttendeeResponseStatus(response_status)
        except ValueError:
            status = AttendeeResponseStatus.NEEDS_ACTION

        return CalendarAttendee(
            email=data['email'],
            display_name=data.get('displayName'),
            response_status=status,
            optional=data.get('optional', False),
            organizer=data.get('organizer', False),
            comment=data.get('comment')
        )

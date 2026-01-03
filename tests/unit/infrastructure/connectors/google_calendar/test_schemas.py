"""
Unit tests for Google Calendar schemas/mappers.
"""
import pytest
from datetime import datetime

from app.infrastructure.connectors.google_calendar.schemas import GoogleCalendarMapper
from app.domain.entities.calendar import Calendar, CalendarProvider
from app.domain.entities.calendar_event import (
    CalendarEvent,
    CalendarEventDraft,
    EventDateTime,
    CalendarAttendee,
    EventReminder,
    EventRecurrence,
    AttendeeResponseStatus
)


class TestGoogleCalendarMapper:
    """Test suite for GoogleCalendarMapper."""

    def test_to_calendar_entity(self):
        """Test converting API calendar to domain entity."""
        api_data = {
            'id': 'primary',
            'summary': 'My Calendar',
            'description': 'Test calendar',
            'timeZone': 'America/New_York',
            'primary': True,
            'backgroundColor': '#9fc6e7',
            'accessRole': 'owner'
        }

        calendar = GoogleCalendarMapper.to_calendar_entity(api_data)

        assert calendar.id == 'primary'
        assert calendar.summary == 'My Calendar'
        assert calendar.description == 'Test calendar'
        assert calendar.timezone == 'America/New_York'
        assert calendar.provider == CalendarProvider.GOOGLE
        assert calendar.is_primary is True
        assert calendar.color == '#9fc6e7'
        assert calendar.access_role == 'owner'

    def test_to_event_entity_full(self):
        """Test converting API event to domain entity with all fields."""
        api_data = {
            'id': 'event123',
            'summary': 'Test Event',
            'description': 'Test description',
            'location': 'Test location',
            'start': {'dateTime': '2026-01-15T10:00:00Z', 'timeZone': 'UTC'},
            'end': {'dateTime': '2026-01-15T11:00:00Z', 'timeZone': 'UTC'},
            'creator': {'email': 'creator@example.com'},
            'organizer': {'email': 'organizer@example.com'},
            'attendees': [
                {
                    'email': 'attendee1@example.com',
                    'displayName': 'Attendee One',
                    'responseStatus': 'accepted',
                    'optional': False,
                    'organizer': False
                }
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'email', 'minutes': 60}
                ]
            },
            'recurrence': ['RRULE:FREQ=WEEKLY;BYDAY=MO'],
            'status': 'confirmed',
            'created': '2026-01-01T00:00:00Z',
            'updated': '2026-01-02T00:00:00Z',
            'htmlLink': 'https://calendar.google.com/event123'
        }

        event = GoogleCalendarMapper.to_event_entity(api_data)

        assert event.id == 'event123'
        assert event.summary == 'Test Event'
        assert event.description == 'Test description'
        assert event.location == 'Test location'
        assert event.creator == 'creator@example.com'
        assert event.organizer == 'organizer@example.com'
        assert len(event.attendees) == 1
        assert event.attendees[0].email == 'attendee1@example.com'
        assert event.attendees[0].response_status == AttendeeResponseStatus.ACCEPTED
        assert len(event.reminders) == 2
        assert event.recurrence is not None
        assert event.recurrence.rrule == 'RRULE:FREQ=WEEKLY;BYDAY=MO'
        assert event.html_link == 'https://calendar.google.com/event123'

    def test_to_event_entity_all_day(self):
        """Test converting all-day event to domain entity."""
        api_data = {
            'id': 'event456',
            'summary': 'All Day Event',
            'start': {'date': '2026-01-15'},
            'end': {'date': '2026-01-16'},
            'status': 'confirmed'
        }

        event = GoogleCalendarMapper.to_event_entity(api_data)

        assert event.id == 'event456'
        assert event.summary == 'All Day Event'
        assert event.start.date == '2026-01-15'
        assert event.start.datetime is None
        assert event.end.date == '2026-01-16'

    def test_from_event_draft_full(self):
        """Test converting domain draft to API format with all fields."""
        draft = CalendarEventDraft(
            summary='Test Event',
            start=EventDateTime(datetime=datetime(2026, 1, 15, 10, 0, 0), timezone='UTC'),
            end=EventDateTime(datetime=datetime(2026, 1, 15, 11, 0, 0), timezone='UTC'),
            description='Test description',
            location='Test location',
            attendees=[
                CalendarAttendee(
                    email='attendee@example.com',
                    display_name='Attendee',
                    optional=False
                )
            ],
            reminders=[
                EventReminder(method='popup', minutes=30)
            ],
            recurrence=EventRecurrence(rrule='RRULE:FREQ=WEEKLY'),
            color_id='1',
            visibility='private'
        )

        api_data = GoogleCalendarMapper.from_event_draft(draft)

        assert api_data['summary'] == 'Test Event'
        assert api_data['description'] == 'Test description'
        assert api_data['location'] == 'Test location'
        assert 'dateTime' in api_data['start']
        assert 'dateTime' in api_data['end']
        assert len(api_data['attendees']) == 1
        assert api_data['attendees'][0]['email'] == 'attendee@example.com'
        assert api_data['reminders']['useDefault'] is False
        assert len(api_data['reminders']['overrides']) == 1
        assert api_data['recurrence'] == ['RRULE:FREQ=WEEKLY']
        assert api_data['colorId'] == '1'
        assert api_data['visibility'] == 'private'

    def test_from_event_draft_all_day(self):
        """Test converting all-day draft to API format."""
        draft = CalendarEventDraft(
            summary='All Day Event',
            start=EventDateTime(date='2026-01-15'),
            end=EventDateTime(date='2026-01-16')
        )

        api_data = GoogleCalendarMapper.from_event_draft(draft)

        assert api_data['summary'] == 'All Day Event'
        assert 'date' in api_data['start']
        assert api_data['start']['date'] == '2026-01-15'
        assert 'date' in api_data['end']
        assert api_data['end']['date'] == '2026-01-16'

    def test_from_event_draft_minimal(self):
        """Test converting minimal draft to API format."""
        draft = CalendarEventDraft(
            summary='Minimal Event',
            start=EventDateTime(datetime=datetime(2026, 1, 15, 10, 0, 0)),
            end=EventDateTime(datetime=datetime(2026, 1, 15, 11, 0, 0))
        )

        api_data = GoogleCalendarMapper.from_event_draft(draft)

        assert api_data['summary'] == 'Minimal Event'
        assert 'start' in api_data
        assert 'end' in api_data
        # Should have default reminder
        assert api_data['reminders']['useDefault'] is True

    def test_parse_attendee(self):
        """Test parsing attendee from API."""
        api_data = {
            'email': 'test@example.com',
            'displayName': 'Test User',
            'responseStatus': 'tentative',
            'optional': True,
            'organizer': False,
            'comment': 'Maybe'
        }

        attendee = GoogleCalendarMapper._parse_attendee(api_data)

        assert attendee.email == 'test@example.com'
        assert attendee.display_name == 'Test User'
        assert attendee.response_status == AttendeeResponseStatus.TENTATIVE
        assert attendee.optional is True
        assert attendee.organizer is False
        assert attendee.comment == 'Maybe'

    def test_parse_attendee_minimal(self):
        """Test parsing minimal attendee from API."""
        api_data = {
            'email': 'test@example.com'
        }

        attendee = GoogleCalendarMapper._parse_attendee(api_data)

        assert attendee.email == 'test@example.com'
        assert attendee.response_status == AttendeeResponseStatus.NEEDS_ACTION
        assert attendee.optional is False

    def test_parse_event_datetime_with_datetime(self):
        """Test parsing datetime with time."""
        api_data = {
            'dateTime': '2026-01-15T10:00:00-05:00',
            'timeZone': 'America/New_York'
        }

        event_dt = GoogleCalendarMapper._parse_event_datetime(api_data)

        assert event_dt.datetime is not None
        assert event_dt.timezone == 'America/New_York'
        assert event_dt.date is None

    def test_parse_event_datetime_with_date(self):
        """Test parsing date-only (all-day event)."""
        api_data = {
            'date': '2026-01-15',
            'timeZone': 'UTC'
        }

        event_dt = GoogleCalendarMapper._parse_event_datetime(api_data)

        assert event_dt.date == '2026-01-15'
        assert event_dt.datetime is None
        assert event_dt.timezone == 'UTC'

    def test_format_event_datetime_with_datetime(self):
        """Test formatting datetime."""
        event_dt = EventDateTime(
            datetime=datetime(2026, 1, 15, 10, 0, 0),
            timezone='America/New_York'
        )

        api_data = GoogleCalendarMapper._format_event_datetime(event_dt)

        assert 'dateTime' in api_data
        assert 'timeZone' in api_data
        assert api_data['timeZone'] == 'America/New_York'

    def test_format_event_datetime_with_date(self):
        """Test formatting date-only."""
        event_dt = EventDateTime(date='2026-01-15')

        api_data = GoogleCalendarMapper._format_event_datetime(event_dt)

        assert 'date' in api_data
        assert api_data['date'] == '2026-01-15'
        assert 'dateTime' not in api_data

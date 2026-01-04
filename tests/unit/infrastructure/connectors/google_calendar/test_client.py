"""
Unit tests for Google Calendar API client.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from googleapiclient.errors import HttpError

from app.infrastructure.connectors.google_calendar.client import GoogleCalendarClient
from app.domain.entities.calendar_event import (
    CalendarEventDraft,
    EventDateTime,
    EventSearchCriteria,
    CalendarAttendee,
    EventReminder
)


@pytest.fixture
def mock_oauth_handler():
    """Create mock OAuth handler."""
    handler = MagicMock()
    mock_creds = MagicMock()
    handler.get_credentials.return_value = mock_creds
    return handler


@pytest.fixture
def mock_service():
    """Create mock Google Calendar service."""
    return MagicMock()


@pytest.fixture
def google_calendar_client(mock_oauth_handler):
    """Create Google Calendar client instance with mocked OAuth."""
    return GoogleCalendarClient(
        account_id="test@example.com",
        oauth_handler=mock_oauth_handler
    )


@pytest.fixture
def sample_event_draft():
    """Create sample event draft."""
    return CalendarEventDraft(
        summary="Test Event",
        start=EventDateTime(datetime=datetime(2026, 1, 15, 10, 0, 0)),
        end=EventDateTime(datetime=datetime(2026, 1, 15, 11, 0, 0)),
        description="Test description",
        location="Test location",
        attendees=[CalendarAttendee(email="attendee@example.com")],
        reminders=[EventReminder(minutes=30)]
    )


@pytest.fixture
def sample_api_event():
    """Sample event from Google Calendar API."""
    return {
        'id': 'event123',
        'summary': 'Test Event',
        'start': {'dateTime': '2026-01-15T10:00:00Z', 'timeZone': 'UTC'},
        'end': {'dateTime': '2026-01-15T11:00:00Z', 'timeZone': 'UTC'},
        'description': 'Test description',
        'location': 'Test location',
        'status': 'confirmed',
        'htmlLink': 'https://calendar.google.com/event123',
        'attendees': [
            {'email': 'attendee@example.com', 'responseStatus': 'needsAction'}
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [{'method': 'popup', 'minutes': 30}]
        }
    }


@pytest.fixture
def sample_api_calendar():
    """Sample calendar from Google Calendar API."""
    return {
        'id': 'primary',
        'summary': 'My Calendar',
        'timeZone': 'America/New_York',
        'primary': True,
        'backgroundColor': '#9fc6e7',
        'accessRole': 'owner'
    }


class TestGoogleCalendarClient:
    """Test suite for GoogleCalendarClient."""

    def test_init(self, mock_oauth_handler):
        """Test client initialization."""
        client = GoogleCalendarClient(
            account_id="test@example.com",
            oauth_handler=mock_oauth_handler
        )

        assert client.account_id == "test@example.com"
        assert client.oauth_handler == mock_oauth_handler
        assert client._service is None

    def test_init_creates_oauth_handler(self):
        """Test that OAuth handler is created if not provided."""
        with patch('app.infrastructure.connectors.google_calendar.client.GoogleCalendarOAuthHandler') as mock_handler_class:
            client = GoogleCalendarClient(account_id="test@example.com")
            mock_handler_class.assert_called_once_with(account_id="test@example.com")

    @patch('app.infrastructure.connectors.google_calendar.client.build')
    def test_get_service_creates_service(self, mock_build, google_calendar_client, mock_oauth_handler):
        """Test that _get_service creates Calendar service."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        service = google_calendar_client._get_service()

        assert service == mock_service
        mock_oauth_handler.get_credentials.assert_called_once()
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_oauth_handler.get_credentials())

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.google_calendar.schemas.GoogleCalendarMapper')
    async def test_create_event_success(self, mock_mapper, google_calendar_client, mock_service, sample_event_draft):
        """Test successful event creation."""
        google_calendar_client._service = mock_service

        # Mock mapper
        mock_mapper.from_event_draft.return_value = {'summary': 'Test Event'}

        # Mock service response
        mock_insert = MagicMock()
        mock_insert.execute.return_value = {'id': 'event123'}
        mock_service.events().insert.return_value = mock_insert

        event_id = await google_calendar_client.create_event('primary', sample_event_draft)

        assert event_id == 'event123'
        mock_mapper.from_event_draft.assert_called_once_with(sample_event_draft)
        mock_service.events().insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_event_failure(self, google_calendar_client, mock_service, sample_event_draft):
        """Test event creation failure."""
        google_calendar_client._service = mock_service

        mock_service.events().insert.side_effect = HttpError(
            resp=MagicMock(status=400),
            content=b"Bad request"
        )

        with pytest.raises(Exception):
            await google_calendar_client.create_event('primary', sample_event_draft)

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.google_calendar.schemas.GoogleCalendarMapper')
    async def test_get_event_success(self, mock_mapper, google_calendar_client, mock_service, sample_api_event):
        """Test successful event retrieval."""
        google_calendar_client._service = mock_service

        # Mock service response
        mock_get = MagicMock()
        mock_get.execute.return_value = sample_api_event
        mock_service.events().get.return_value = mock_get

        # Mock mapper
        mock_event = MagicMock()
        mock_mapper.to_event_entity.return_value = mock_event

        event = await google_calendar_client.get_event('primary', 'event123')

        assert event == mock_event
        mock_service.events().get.assert_called_once_with(
            calendarId='primary',
            eventId='event123'
        )

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.google_calendar.schemas.GoogleCalendarMapper')
    async def test_list_events_success(self, mock_mapper, google_calendar_client, mock_service, sample_api_event):
        """Test successful event listing."""
        google_calendar_client._service = mock_service

        # Mock list response
        mock_list = MagicMock()
        mock_list.execute.return_value = {
            'items': [sample_api_event, sample_api_event]
        }
        mock_service.events().list.return_value = mock_list

        # Mock mapper
        mock_event = MagicMock()
        mock_mapper.to_event_entity.return_value = mock_event

        criteria = EventSearchCriteria(
            calendar_id='primary',
            time_min=datetime(2026, 1, 15, 0, 0, 0),
            time_max=datetime(2026, 1, 16, 0, 0, 0),
            max_results=10
        )

        events = await google_calendar_client.list_events(criteria)

        assert len(events) == 2
        assert all(e == mock_event for e in events)
        mock_service.events().list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_events_empty(self, google_calendar_client, mock_service):
        """Test event listing with no results."""
        google_calendar_client._service = mock_service

        mock_list = MagicMock()
        mock_list.execute.return_value = {'items': []}
        mock_service.events().list.return_value = mock_list

        criteria = EventSearchCriteria(calendar_id='primary')
        events = await google_calendar_client.list_events(criteria)

        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_delete_event_success(self, google_calendar_client, mock_service):
        """Test successful event deletion."""
        google_calendar_client._service = mock_service

        mock_delete = MagicMock()
        mock_delete.execute.return_value = {}
        mock_service.events().delete.return_value = mock_delete

        await google_calendar_client.delete_event('primary', 'event123')

        mock_service.events().delete.assert_called_once_with(
            calendarId='primary',
            eventId='event123',
            sendUpdates='all'
        )

    @pytest.mark.asyncio
    @patch('app.infrastructure.connectors.google_calendar.schemas.GoogleCalendarMapper')
    async def test_list_calendars_success(self, mock_mapper, google_calendar_client, mock_service, sample_api_calendar):
        """Test successful calendar listing."""
        google_calendar_client._service = mock_service

        mock_list = MagicMock()
        mock_list.execute.return_value = {
            'items': [sample_api_calendar]
        }
        mock_service.calendarList().list.return_value = mock_list

        mock_calendar = MagicMock()
        mock_mapper.to_calendar_entity.return_value = mock_calendar

        calendars = await google_calendar_client.list_calendars()

        assert len(calendars) == 1
        assert calendars[0] == mock_calendar
        mock_service.calendarList().list.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_free_busy_success(self, google_calendar_client, mock_service):
        """Test successful free/busy query."""
        google_calendar_client._service = mock_service

        mock_query = MagicMock()
        mock_query.execute.return_value = {
            'calendars': {
                'primary': {
                    'busy': [
                        {
                            'start': '2026-01-15T10:00:00Z',
                            'end': '2026-01-15T11:00:00Z'
                        }
                    ]
                }
            }
        }
        mock_service.freebusy().query.return_value = mock_query

        time_min = datetime(2026, 1, 15, 0, 0, 0)
        time_max = datetime(2026, 1, 16, 0, 0, 0)

        result = await google_calendar_client.get_free_busy(['primary'], time_min, time_max)

        assert 'calendars' in result
        mock_service.freebusy().query.assert_called_once()

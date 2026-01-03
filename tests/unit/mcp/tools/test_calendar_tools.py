"""
Unit tests for Calendar MCP Tools.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.mcp.tools.calendar_tools import (
    CalendarTools,
    EventSummary,
    CreateEventResult,
    ListEventsResult,
    CalendarSummary,
    ListCalendarsResult
)


@pytest.fixture
def calendar_tools():
    """Create CalendarTools instance."""
    return CalendarTools()


class TestCalendarTools:
    """Test suite for CalendarTools."""

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.CreateEventUseCase')
    async def test_create_event_success(self, mock_use_case_class, calendar_tools):
        """Test successful event creation."""
        # Mock use case
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.event_id = "event123"
        mock_response.html_link = "https://calendar.google.com/event123"
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        # Re-instantiate to get mocked use case
        tools = CalendarTools()

        result = await tools.create_event(
            summary="Test Event",
            start_datetime="2026-01-15T10:00:00",
            end_datetime="2026-01-15T11:00:00",
            provider="google"
        )

        assert isinstance(result, CreateEventResult)
        assert result.success is True
        assert result.event_id == "event123"
        assert result.html_link == "https://calendar.google.com/event123"
        assert result.error is None

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.CreateEventUseCase')
    async def test_create_event_all_day(self, mock_use_case_class, calendar_tools):
        """Test creating all-day event."""
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.event_id = "event456"
        mock_response.html_link = None
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.create_event(
            summary="All Day Event",
            start_date="2026-01-15",
            end_date="2026-01-16",
            provider="google"
        )

        assert result.success is True
        assert result.event_id == "event456"

        # Verify request was created correctly
        call_args = mock_use_case.execute.call_args
        request = call_args[0][0]
        assert request.start_date == "2026-01-15"
        assert request.end_date == "2026-01-16"
        assert request.start_datetime is None

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.CreateEventUseCase')
    async def test_create_event_with_attendees(self, mock_use_case_class, calendar_tools):
        """Test creating event with attendees."""
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.event_id = "event789"
        mock_response.html_link = None
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.create_event(
            summary="Team Meeting",
            start_datetime="2026-01-15T10:00:00",
            end_datetime="2026-01-15T11:00:00",
            attendees=["alice@example.com", "bob@example.com"],
            reminders_minutes=[15, 30],
            provider="google"
        )

        assert result.success is True

        # Verify attendees and reminders
        call_args = mock_use_case.execute.call_args
        request = call_args[0][0]
        assert request.attendees == ["alice@example.com", "bob@example.com"]
        assert request.reminders_minutes == [15, 30]

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.CreateEventUseCase')
    async def test_create_event_failure(self, mock_use_case_class, calendar_tools):
        """Test event creation failure."""
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.event_id = None
        mock_response.html_link = None
        mock_response.error = "API Error"
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.create_event(
            summary="Failed Event",
            start_datetime="2026-01-15T10:00:00",
            end_datetime="2026-01-15T11:00:00",
            provider="google"
        )

        assert result.success is False
        assert result.error == "API Error"

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.ListEventsUseCase')
    async def test_list_events_success(self, mock_use_case_class, calendar_tools):
        """Test successful event listing."""
        # Create mock events
        mock_event1 = MagicMock()
        mock_event1.id = "event1"
        mock_event1.summary = "Event 1"
        mock_event1.start = MagicMock()
        mock_event1.start.to_iso_string.return_value = "2026-01-15T10:00:00"
        mock_event1.end = MagicMock()
        mock_event1.end.to_iso_string.return_value = "2026-01-15T11:00:00"
        mock_event1.location = "Office"
        mock_event1.attendees = []
        mock_event1.recurrence = None
        mock_event1.html_link = "https://calendar.google.com/event1"

        mock_event2 = MagicMock()
        mock_event2.id = "event2"
        mock_event2.summary = "Event 2"
        mock_event2.start = MagicMock()
        mock_event2.start.to_iso_string.return_value = "2026-01-15T14:00:00"
        mock_event2.end = MagicMock()
        mock_event2.end.to_iso_string.return_value = "2026-01-15T15:00:00"
        mock_event2.location = None
        mock_event2.attendees = [MagicMock(), MagicMock()]
        mock_event2.recurrence = MagicMock()
        mock_event2.html_link = None

        # Mock use case
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.events = [mock_event1, mock_event2]
        mock_response.count = 2
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.list_events(
            calendar_id="primary",
            time_min="2026-01-15T00:00:00",
            time_max="2026-01-16T00:00:00",
            provider="google"
        )

        assert isinstance(result, ListEventsResult)
        assert result.success is True
        assert result.count == 2
        assert len(result.events) == 2
        assert result.events[0].id == "event1"
        assert result.events[0].summary == "Event 1"
        assert result.events[0].attendees_count == 0
        assert result.events[0].is_recurring is False
        assert result.events[1].attendees_count == 2
        assert result.events[1].is_recurring is True

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.ListEventsUseCase')
    async def test_list_events_empty(self, mock_use_case_class, calendar_tools):
        """Test listing events with no results."""
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.events = []
        mock_response.count = 0
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.list_events(
            calendar_id="primary",
            provider="google"
        )

        assert result.success is True
        assert result.count == 0
        assert len(result.events) == 0

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.ListEventsUseCase')
    async def test_list_events_with_query(self, mock_use_case_class, calendar_tools):
        """Test listing events with search query."""
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.events = []
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.list_events(
            query="meeting",
            max_results=20,
            provider="google"
        )

        # Verify query parameters
        call_args = mock_use_case.execute.call_args
        request = call_args[0][0]
        assert request.query == "meeting"
        assert request.max_results == 20

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.ListCalendarsUseCase')
    async def test_list_calendars_success(self, mock_use_case_class, calendar_tools):
        """Test successful calendar listing."""
        # Create mock calendars
        mock_cal1 = MagicMock()
        mock_cal1.id = "primary"
        mock_cal1.summary = "My Calendar"
        mock_cal1.timezone = "America/New_York"
        mock_cal1.provider.value = "google"
        mock_cal1.is_primary = True

        mock_cal2 = MagicMock()
        mock_cal2.id = "work"
        mock_cal2.summary = "Work Calendar"
        mock_cal2.timezone = "America/New_York"
        mock_cal2.provider.value = "google"
        mock_cal2.is_primary = False

        # Mock use case
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.calendars = [mock_cal1, mock_cal2]
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.list_calendars(provider="google")

        assert isinstance(result, ListCalendarsResult)
        assert result.success is True
        assert len(result.calendars) == 2
        assert result.calendars[0].id == "primary"
        assert result.calendars[0].name == "My Calendar"
        assert result.calendars[0].is_primary is True
        assert result.calendars[1].id == "work"
        assert result.calendars[1].is_primary is False

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.ListCalendarsUseCase')
    async def test_list_calendars_apple(self, mock_use_case_class, calendar_tools):
        """Test listing Apple calendars."""
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.calendars = []
        mock_response.error = None
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.list_calendars(
            provider="apple",
            account_id="test@icloud.com"
        )

        # Verify provider parameter
        call_args = mock_use_case.execute.call_args
        request = call_args[0][0]
        assert request.provider == "apple"
        assert request.account_id == "test@icloud.com"

    @pytest.mark.asyncio
    @patch('app.mcp.tools.calendar_tools.ListCalendarsUseCase')
    async def test_list_calendars_failure(self, mock_use_case_class, calendar_tools):
        """Test calendar listing failure."""
        mock_use_case = AsyncMock()
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.calendars = []
        mock_response.error = "Authentication failed"
        mock_use_case.execute.return_value = mock_response
        mock_use_case_class.return_value = mock_use_case

        tools = CalendarTools()

        result = await tools.list_calendars(provider="google")

        assert result.success is False
        assert result.error == "Authentication failed"
        assert len(result.calendars) == 0

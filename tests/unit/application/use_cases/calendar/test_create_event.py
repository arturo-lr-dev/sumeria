"""
Unit tests for CreateEventUseCase.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.application.use_cases.calendar.create_event import (
    CreateEventUseCase,
    CreateEventRequest,
    CreateEventResponse
)


@pytest.fixture
def create_event_use_case():
    """Create CreateEventUseCase instance."""
    return CreateEventUseCase()


@pytest.fixture
def google_request():
    """Sample create event request for Google Calendar."""
    return CreateEventRequest(
        summary="Test Meeting",
        start_datetime=datetime(2026, 1, 15, 10, 0, 0),
        end_datetime=datetime(2026, 1, 15, 11, 0, 0),
        description="Test description",
        location="Test location",
        attendees=["attendee@example.com"],
        reminders_minutes=[30],
        calendar_id="primary",
        provider="google",
        account_id="test@gmail.com"
    )


@pytest.fixture
def apple_request():
    """Sample create event request for Apple Calendar."""
    return CreateEventRequest(
        summary="Test Event",
        start_datetime=datetime(2026, 1, 15, 14, 0, 0),
        end_datetime=datetime(2026, 1, 15, 15, 0, 0),
        provider="apple",
        account_id="test@icloud.com"
    )


class TestCreateEventUseCase:
    """Test suite for CreateEventUseCase."""

    @pytest.mark.asyncio
    @patch('app.application.use_cases.calendar.create_event.google_calendar_account_manager')
    async def test_create_google_event_success(self, mock_manager, create_event_use_case, google_request):
        """Test successful event creation in Google Calendar."""
        # Mock client
        mock_client = AsyncMock()
        mock_client.create_event.return_value = "event123"
        mock_event = MagicMock()
        mock_event.id = "event123"
        mock_event.html_link = "https://calendar.google.com/event123"
        mock_client.get_event.return_value = mock_event
        mock_manager.get_client.return_value = mock_client

        response = await create_event_use_case.execute(google_request)

        assert response.success is True
        assert response.event_id == "event123"
        assert response.html_link == "https://calendar.google.com/event123"
        assert response.error is None

        mock_manager.get_client.assert_called_once_with("test@gmail.com")
        mock_client.create_event.assert_called_once()
        mock_client.get_event.assert_called_once_with("primary", "event123")

    @pytest.mark.asyncio
    @patch('app.application.use_cases.calendar.create_event.AppleCalendarClient')
    async def test_create_apple_event_success(self, mock_client_class, create_event_use_case, apple_request):
        """Test successful event creation in Apple Calendar."""
        # Mock client
        mock_client = AsyncMock()
        mock_client.create_event.return_value = "apple-event-123"
        mock_event = MagicMock()
        mock_event.id = "apple-event-123"
        mock_event.html_link = None
        mock_client.get_event.return_value = mock_event
        mock_client_class.return_value = mock_client

        response = await create_event_use_case.execute(apple_request)

        assert response.success is True
        assert response.event_id == "apple-event-123"
        assert response.error is None

        mock_client_class.assert_called_once_with(account_id="test@icloud.com")
        mock_client.create_event.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.application.use_cases.calendar.create_event.google_calendar_account_manager')
    async def test_create_event_failure(self, mock_manager, create_event_use_case, google_request):
        """Test event creation failure."""
        # Mock client to raise error
        mock_client = AsyncMock()
        mock_client.create_event.side_effect = Exception("API Error")
        mock_manager.get_client.return_value = mock_client

        response = await create_event_use_case.execute(google_request)

        assert response.success is False
        assert response.event_id is None
        assert response.error == "API Error"

    @pytest.mark.asyncio
    @patch('app.application.use_cases.calendar.create_event.google_calendar_account_manager')
    async def test_create_event_all_day(self, mock_manager, create_event_use_case):
        """Test creating all-day event."""
        request = CreateEventRequest(
            summary="All Day Event",
            start_date="2026-01-15",
            end_date="2026-01-16",
            provider="google"
        )

        mock_client = AsyncMock()
        mock_client.create_event.return_value = "event456"
        mock_event = MagicMock()
        mock_event.id = "event456"
        mock_event.html_link = "https://calendar.google.com/event456"
        mock_client.get_event.return_value = mock_event
        mock_manager.get_client.return_value = mock_client

        response = await create_event_use_case.execute(request)

        assert response.success is True
        assert response.event_id == "event456"

        # Verify event draft was created correctly
        call_args = mock_client.create_event.call_args
        draft = call_args[0][1]  # Second argument is the draft
        assert draft.start.date == "2026-01-15"
        assert draft.start.datetime is None
        assert draft.end.date == "2026-01-16"

    @pytest.mark.asyncio
    @patch('app.application.use_cases.calendar.create_event.google_calendar_account_manager')
    async def test_create_event_with_attendees(self, mock_manager, create_event_use_case):
        """Test creating event with multiple attendees."""
        request = CreateEventRequest(
            summary="Team Meeting",
            start_datetime=datetime(2026, 1, 15, 10, 0, 0),
            end_datetime=datetime(2026, 1, 15, 11, 0, 0),
            attendees=["alice@example.com", "bob@example.com", "charlie@example.com"],
            provider="google"
        )

        mock_client = AsyncMock()
        mock_client.create_event.return_value = "event789"
        mock_event = MagicMock()
        mock_event.id = "event789"
        mock_event.html_link = None
        mock_client.get_event.return_value = mock_event
        mock_manager.get_client.return_value = mock_client

        response = await create_event_use_case.execute(request)

        assert response.success is True

        # Verify attendees were added
        call_args = mock_client.create_event.call_args
        draft = call_args[0][1]
        assert len(draft.attendees) == 3
        assert draft.attendees[0].email == "alice@example.com"
        assert draft.attendees[1].email == "bob@example.com"
        assert draft.attendees[2].email == "charlie@example.com"

    @pytest.mark.asyncio
    @patch('app.application.use_cases.calendar.create_event.google_calendar_account_manager')
    async def test_create_event_with_multiple_reminders(self, mock_manager, create_event_use_case):
        """Test creating event with multiple reminders."""
        request = CreateEventRequest(
            summary="Important Meeting",
            start_datetime=datetime(2026, 1, 15, 10, 0, 0),
            end_datetime=datetime(2026, 1, 15, 11, 0, 0),
            reminders_minutes=[15, 30, 60],
            provider="google"
        )

        mock_client = AsyncMock()
        mock_client.create_event.return_value = "event101"
        mock_event = MagicMock()
        mock_event.id = "event101"
        mock_event.html_link = None
        mock_client.get_event.return_value = mock_event
        mock_manager.get_client.return_value = mock_client

        response = await create_event_use_case.execute(request)

        assert response.success is True

        # Verify reminders were added
        call_args = mock_client.create_event.call_args
        draft = call_args[0][1]
        assert len(draft.reminders) == 3
        assert draft.reminders[0].minutes == 15
        assert draft.reminders[1].minutes == 30
        assert draft.reminders[2].minutes == 60

"""
Mappers between CalDAV/iCalendar and domain entities.
"""
from datetime import datetime, date
from typing import Optional
import uuid

# iCalendar will be imported conditionally
try:
    from icalendar import Calendar as iCalendar, Event as iEvent, vText
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False

from app.domain.entities.calendar import Calendar, CalendarProvider
from app.domain.entities.calendar_event import (
    CalendarEvent,
    CalendarEventDraft,
    EventDateTime,
    EventRecurrence,
    CalendarAttendee,
    EventReminder
)


class AppleCalendarMapper:
    """Maps between CalDAV/iCalendar and domain entities."""

    @staticmethod
    def to_calendar_entity(caldav_calendar) -> Calendar:
        """
        Convert CalDAV calendar to domain entity.

        Args:
            caldav_calendar: CalDAV calendar object

        Returns:
            Calendar entity
        """
        calendar_id = str(caldav_calendar.url).split('/')[-2] if hasattr(caldav_calendar, 'url') else 'unknown'
        calendar_name = caldav_calendar.name if hasattr(caldav_calendar, 'name') else calendar_id

        return Calendar(
            id=calendar_id,
            summary=calendar_name,
            timezone='UTC',  # CalDAV doesn't always expose timezone easily
            provider=CalendarProvider.APPLE,
            is_primary=False  # CalDAV doesn't have primary concept
        )

    @staticmethod
    def to_event_entity(ical_data: str, calendar_id: str = 'primary') -> CalendarEvent:
        """
        Convert iCalendar event to domain entity.

        Args:
            ical_data: iCalendar data as string
            calendar_id: Calendar ID

        Returns:
            CalendarEvent entity

        Raises:
            ValueError: If no VEVENT found
        """
        if not ICALENDAR_AVAILABLE:
            raise ImportError("icalendar library required")

        ical = iCalendar.from_ical(ical_data)

        for component in ical.walk():
            if component.name == "VEVENT":
                return AppleCalendarMapper._parse_vevent(component, calendar_id)

        raise ValueError("No VEVENT found in iCalendar data")

    @staticmethod
    def from_event_draft(draft: CalendarEventDraft, event_uid: Optional[str] = None) -> iCalendar:
        """
        Convert domain event draft to iCalendar format.

        Args:
            draft: CalendarEventDraft entity
            event_uid: Optional UID for updating existing event

        Returns:
            iCalendar object

        Raises:
            ImportError: If icalendar library not available
        """
        if not ICALENDAR_AVAILABLE:
            raise ImportError("icalendar library required")

        cal = iCalendar()
        cal.add('prodid', '-//Sumeria Personal Assistant//EN')
        cal.add('version', '2.0')

        event = iEvent()

        # Add summary
        event.add('summary', draft.summary)

        # Add start/end times
        if draft.start.datetime:
            event.add('dtstart', draft.start.datetime)
        elif draft.start.date:
            event.add('dtstart', datetime.strptime(draft.start.date, '%Y-%m-%d').date())

        if draft.end.datetime:
            event.add('dtend', draft.end.datetime)
        elif draft.end.date:
            event.add('dtend', datetime.strptime(draft.end.date, '%Y-%m-%d').date())

        # Add optional fields
        if draft.description:
            event.add('description', draft.description)
        if draft.location:
            event.add('location', draft.location)

        # Add attendees
        for attendee in draft.attendees:
            attendee_value = f'mailto:{attendee.email}'
            params = {
                'cn': attendee.display_name or attendee.email,
                'role': 'OPT-PARTICIPANT' if attendee.optional else 'REQ-PARTICIPANT',
                'rsvp': 'TRUE'
            }
            event.add('attendee', attendee_value, parameters=params)

        # Add reminders (alarms) - Note: CalDAV alarm support varies
        for reminder in draft.reminders:
            from icalendar import Alarm
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', 'Reminder')
            # Trigger is negative duration before event
            from datetime import timedelta
            alarm.add('trigger', timedelta(minutes=-reminder.minutes))
            event.add_component(alarm)

        # Add recurrence
        if draft.recurrence:
            # Parse RRULE string and add it
            event.add('rrule', draft.recurrence.rrule)

        # Add UID
        if event_uid:
            event.add('uid', event_uid)
        else:
            event.add('uid', str(uuid.uuid4()))

        # Add timestamps
        event.add('dtstamp', datetime.now())

        cal.add_component(event)
        return cal

    @staticmethod
    def _parse_vevent(vevent, calendar_id: str = 'primary') -> CalendarEvent:
        """
        Parse VEVENT component to CalendarEvent.

        Args:
            vevent: VEVENT component
            calendar_id: Calendar ID

        Returns:
            CalendarEvent entity
        """
        # Extract basic fields
        summary = str(vevent.get('summary', ''))
        description = str(vevent.get('description', '')) if vevent.get('description') else None
        location = str(vevent.get('location', '')) if vevent.get('location') else None

        # Parse start/end
        start = AppleCalendarMapper._parse_ical_datetime(vevent.get('dtstart'))
        end = AppleCalendarMapper._parse_ical_datetime(vevent.get('dtend'))

        # Parse attendees
        attendees = []
        if 'attendee' in vevent:
            attendee_list = vevent['attendee']
            if not isinstance(attendee_list, list):
                attendee_list = [attendee_list]

            for att in attendee_list:
                email = str(att).replace('mailto:', '').replace('MAILTO:', '')
                # Extract display name from parameters if available
                display_name = None
                if hasattr(att, 'params') and 'CN' in att.params:
                    display_name = str(att.params['CN'])

                attendees.append(CalendarAttendee(
                    email=email,
                    display_name=display_name
                ))

        # Parse recurrence
        recurrence = None
        if 'rrule' in vevent:
            rrule_val = vevent['rrule']
            # Convert rrule to string format
            if hasattr(rrule_val, 'to_ical'):
                rrule_str = rrule_val.to_ical().decode('utf-8')
            else:
                rrule_str = str(rrule_val)
            recurrence = EventRecurrence(rrule=rrule_str)

        # Parse UID
        event_id = str(vevent.get('uid', ''))

        # Parse timestamps
        created = None
        if 'created' in vevent:
            created_val = vevent.get('created')
            if isinstance(created_val, datetime):
                created = created_val

        updated = None
        if 'last-modified' in vevent:
            updated_val = vevent.get('last-modified')
            if isinstance(updated_val, datetime):
                updated = updated_val

        return CalendarEvent(
            id=event_id,
            summary=summary,
            start=start,
            end=end,
            description=description,
            location=location,
            attendees=attendees,
            recurrence=recurrence,
            created=created,
            updated=updated,
            calendar_id=calendar_id,
            provider=CalendarProvider.APPLE
        )

    @staticmethod
    def _parse_ical_datetime(dt_prop) -> EventDateTime:
        """
        Parse iCalendar datetime property.

        Args:
            dt_prop: DateTime property from iCalendar

        Returns:
            EventDateTime entity
        """
        if dt_prop is None:
            return EventDateTime()

        dt = dt_prop.dt if hasattr(dt_prop, 'dt') else dt_prop

        if isinstance(dt, datetime):
            return EventDateTime(datetime=dt)
        elif isinstance(dt, date):
            return EventDateTime(date=dt.isoformat())
        else:
            return EventDateTime()

# Plan de Implementación: Integración con Google Calendar y Apple Calendar

## Resumen
Implementar integración completa con Google Calendar API y Apple Calendar (CalDAV) siguiendo la arquitectura DDD establecida en el proyecto, permitiendo gestionar eventos de calendario a través del MCP server con soporte multi-calendario.

## Objetivos
- Integrar Google Calendar API usando el SDK oficial de Python
- Integrar Apple Calendar mediante protocolo CalDAV
- Seguir la arquitectura DDD establecida (Domain, Application, Infrastructure)
- Implementar operaciones CRUD para eventos de calendario
- Soportar múltiples cuentas de calendario (similar a Gmail multi-account)
- Exponer funcionalidad a través de MCP tools unificados
- Mantener consistencia con las integraciones existentes (Gmail, Notion, Holded)

## Análisis de Requisitos

### Funcionalidades Principales de Calendarios

#### 1. **Events (Eventos)**
   - Crear eventos
   - Leer eventos por ID
   - Actualizar eventos
   - Eliminar eventos
   - Listar eventos en rango de fechas
   - Buscar eventos por query

#### 2. **Calendars (Calendarios)**
   - Listar calendarios disponibles
   - Obtener detalles de calendario
   - Crear calendarios (opcional)
   - Configurar calendario por defecto

#### 3. **Recurrence (Recurrencia)**
   - Soporte para eventos recurrentes
   - Reglas RRULE (RFC 5545)
   - Excepciones a recurrencias

#### 4. **Attendees (Participantes)**
   - Agregar/eliminar participantes
   - Gestión de respuestas (accepted, declined, tentative)
   - Envío de invitaciones

#### 5. **Reminders (Recordatorios)**
   - Agregar recordatorios a eventos
   - Múltiples recordatorios por evento
   - Diferentes tipos (email, popup)

## Diferencias entre Google Calendar y Apple Calendar

| Característica | Google Calendar | Apple Calendar (CalDAV) |
|----------------|-----------------|-------------------------|
| Autenticación | OAuth2 | Basic Auth / App-specific password |
| Protocolo | REST API | CalDAV (WebDAV extension) |
| SDK Oficial | ✅ google-api-python-client | ❌ Usar caldav library |
| Free/Busy | ✅ Nativo | ✅ Via CalDAV |
| Attachments | ✅ Soportado | ⚠️ Limitado |
| Color eventos | ✅ Nativo | ⚠️ Extensión propietaria |

## Estructura de Archivos

```
app/
├── config/
│   └── settings.py                              # ✏️ Agregar configuración de calendarios
├── domain/
│   └── entities/
│       ├── calendar.py                          # ✨ NUEVO - Calendar entity
│       ├── calendar_event.py                    # ✨ NUEVO - Event entity
│       └── calendar_attendee.py                 # ✨ NUEVO - Attendee entity
├── infrastructure/
│   └── connectors/
│       ├── google_calendar/
│       │   ├── __init__.py                      # ✨ NUEVO
│       │   ├── client.py                        # ✨ NUEVO - Google Calendar API client
│       │   ├── oauth.py                         # ✨ NUEVO - OAuth2 handler
│       │   ├── account_manager.py               # ✨ NUEVO - Multi-account manager
│       │   └── schemas.py                       # ✨ NUEVO - Mappers
│       └── apple_calendar/
│           ├── __init__.py                      # ✨ NUEVO
│           ├── client.py                        # ✨ NUEVO - CalDAV client
│           ├── auth.py                          # ✨ NUEVO - CalDAV auth
│           └── schemas.py                       # ✨ NUEVO - Mappers
├── application/
│   └── use_cases/
│       ├── google_calendar/
│       │   ├── __init__.py                      # ✨ NUEVO
│       │   ├── create_event.py                  # ✨ NUEVO
│       │   ├── get_event.py                     # ✨ NUEVO
│       │   ├── update_event.py                  # ✨ NUEVO
│       │   ├── delete_event.py                  # ✨ NUEVO
│       │   ├── list_events.py                   # ✨ NUEVO
│       │   ├── search_events.py                 # ✨ NUEVO
│       │   └── list_calendars.py                # ✨ NUEVO
│       └── apple_calendar/
│           ├── __init__.py                      # ✨ NUEVO
│           ├── create_event.py                  # ✨ NUEVO
│           ├── get_event.py                     # ✨ NUEVO
│           ├── update_event.py                  # ✨ NUEVO
│           ├── delete_event.py                  # ✨ NUEVO
│           ├── list_events.py                   # ✨ NUEVO
│           └── list_calendars.py                # ✨ NUEVO
├── mcp/
│   └── tools/
│       └── calendar_tools.py                    # ✨ NUEVO - Unified calendar tools
└── main.py                                      # ✏️ Registrar MCP tools

tests/
└── unit/
    ├── infrastructure/
    │   └── connectors/
    │       ├── google_calendar/
    │       │   ├── __init__.py                  # ✨ NUEVO
    │       │   ├── test_client.py               # ✨ NUEVO
    │       │   ├── test_oauth.py                # ✨ NUEVO
    │       │   └── test_schemas.py              # ✨ NUEVO
    │       └── apple_calendar/
    │           ├── __init__.py                  # ✨ NUEVO
    │           ├── test_client.py               # ✨ NUEVO
    │           └── test_schemas.py              # ✨ NUEVO
    ├── application/
    │   └── use_cases/
    │       ├── google_calendar/
    │       │   ├── __init__.py                  # ✨ NUEVO
    │       │   ├── test_create_event.py         # ✨ NUEVO
    │       │   └── test_list_events.py          # ✨ NUEVO
    │       └── apple_calendar/
    │           ├── __init__.py                  # ✨ NUEVO
    │           ├── test_create_event.py         # ✨ NUEVO
    │           └── test_list_events.py          # ✨ NUEVO
    └── mcp/
        └── tools/
            └── test_calendar_tools.py           # ✨ NUEVO

docs/
├── google-calendar-setup.md                     # ✨ NUEVO
└── apple-calendar-setup.md                      # ✨ NUEVO
```

## Implementación Detallada

### Fase 1: Configuración y Dependencias

#### 1.1. Actualizar pyproject.toml / requirements
```toml
# Agregar:
google-api-python-client = "^2.111.0"
google-auth-httplib2 = "^0.2.0"
google-auth-oauthlib = "^1.2.0"
caldav = "^1.3.9"
icalendar = "^5.0.11"
python-dateutil = "^2.8.2"
recurring-ical-events = "^2.2.3"  # Para manejar recurrencias
```

#### 1.2. Actualizar settings.py
```python
# Google Calendar Configuration
google_calendar_credentials_file: Path = Field(
    default=Path.home() / ".sumeria" / "google_calendar_credentials.json",
    description="Google Calendar OAuth2 credentials file"
)
google_calendar_tokens_dir: Path = Field(
    default=Path.home() / ".sumeria" / "tokens" / "google_calendar",
    description="Directory for Google Calendar OAuth tokens"
)
google_calendar_scopes: list[str] = Field(
    default=[
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    description="Google Calendar API scopes"
)

# Apple Calendar (CalDAV) Configuration
apple_calendar_url: Optional[str] = Field(
    default=None,
    description="Apple Calendar CalDAV URL (e.g., https://caldav.icloud.com)"
)
apple_calendar_username: Optional[str] = Field(
    default=None,
    description="Apple ID for CalDAV access"
)
apple_calendar_password: Optional[str] = Field(
    default=None,
    description="App-specific password for CalDAV"
)
apple_calendar_tokens_dir: Path = Field(
    default=Path.home() / ".sumeria" / "tokens" / "apple_calendar",
    description="Directory for Apple Calendar credentials"
)
```

### Fase 2: Domain Layer (Entidades)

#### 2.1. Domain Entity: Calendar (app/domain/entities/calendar.py)
```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class CalendarProvider(str, Enum):
    """Calendar provider types."""
    GOOGLE = "google"
    APPLE = "apple"


@dataclass
class Calendar:
    """Calendar entity."""
    id: str
    summary: str  # Calendar name
    description: Optional[str] = None
    timezone: str = "UTC"
    provider: CalendarProvider = CalendarProvider.GOOGLE
    is_primary: bool = False
    color: Optional[str] = None
    access_role: Optional[str] = None  # owner, reader, writer
    account_id: Optional[str] = None  # For multi-account support


@dataclass
class CalendarListRequest:
    """Request to list calendars."""
    provider: CalendarProvider
    account_id: Optional[str] = None
    show_hidden: bool = False
```

#### 2.2. Domain Entity: CalendarEvent (app/domain/entities/calendar_event.py)
```python
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class EventDateTime:
    """Event date/time with timezone support."""
    datetime: Optional[datetime] = None
    date: Optional[str] = None  # For all-day events (YYYY-MM-DD)
    timezone: str = "UTC"


@dataclass
class EventRecurrence:
    """Recurrence rule for events."""
    rrule: str  # RFC 5545 format
    exdates: list[datetime] = field(default_factory=list)  # Exception dates


@dataclass
class CalendarEventDraft:
    """Draft for creating a new calendar event."""
    summary: str  # Event title
    start: EventDateTime
    end: EventDateTime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: list['CalendarAttendee'] = field(default_factory=list)
    reminders: list['EventReminder'] = field(default_factory=list)
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
    attendees: list['CalendarAttendee'] = field(default_factory=list)
    reminders: list['EventReminder'] = field(default_factory=list)
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
```

#### 2.3. Domain Entity: CalendarAttendee (app/domain/entities/calendar_attendee.py)
```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AttendeeResponseStatus(str, Enum):
    """Attendee response status."""
    NEEDS_ACTION = "needsAction"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"


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
```

### Fase 3: Infrastructure Layer - Google Calendar

#### 3.1. Google Calendar OAuth (app/infrastructure/connectors/google_calendar/oauth.py)
```python
"""
Google Calendar OAuth2 authentication handler with multi-account support.
Similar to Gmail OAuth implementation.
"""
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from app.config.settings import settings


class GoogleCalendarOAuthHandler:
    """Handles OAuth2 authentication for Google Calendar API."""

    def __init__(
        self,
        account_id: str,
        credentials_file: Optional[Path] = None,
        tokens_dir: Optional[Path] = None,
        scopes: Optional[list[str]] = None
    ):
        self.account_id = account_id
        self.credentials_file = credentials_file or settings.google_calendar_credentials_file
        self.tokens_dir = tokens_dir or settings.google_calendar_tokens_dir
        self.scopes = scopes or settings.google_calendar_scopes
        self._creds: Optional[Credentials] = None

    def _ensure_tokens_dir(self) -> None:
        """Ensure tokens directory exists."""
        self.tokens_dir.mkdir(parents=True, exist_ok=True)

    @property
    def token_file(self) -> Path:
        """Get the token file path for this account."""
        safe_account_id = self.account_id.replace('@', '_at_').replace('.', '_')
        return self.tokens_dir / f"token_{safe_account_id}.json"

    def get_credentials(self) -> Credentials:
        """Get valid credentials, refreshing or requesting new ones if needed."""
        # Implementation similar to Gmail OAuth
        # Load existing token, refresh if needed, or initiate OAuth flow
        pass

    def revoke_credentials(self) -> None:
        """Revoke and delete stored credentials."""
        pass

    @property
    def is_authenticated(self) -> bool:
        """Check if valid credentials are available."""
        pass

    @staticmethod
    def list_authenticated_accounts(tokens_dir: Optional[Path] = None) -> list[str]:
        """List all authenticated accounts."""
        pass
```

#### 3.2. Google Calendar Client (app/infrastructure/connectors/google_calendar/client.py)
```python
"""
Google Calendar API client implementation.
Handles all interactions with Google Calendar API.
"""
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.infrastructure.connectors.google_calendar.oauth import GoogleCalendarOAuthHandler
from app.infrastructure.connectors.google_calendar.schemas import GoogleCalendarMapper
from app.domain.entities.calendar import Calendar
from app.domain.entities.calendar_event import (
    CalendarEvent,
    CalendarEventDraft,
    EventSearchCriteria
)


class GoogleCalendarClient:
    """Google Calendar API client for calendar operations."""

    def __init__(
        self,
        account_id: str,
        oauth_handler: Optional[GoogleCalendarOAuthHandler] = None
    ):
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
        """
        service = self._get_service()
        event_data = GoogleCalendarMapper.from_event_draft(draft)

        event = service.events().insert(
            calendarId=calendar_id,
            body=event_data,
            sendUpdates='all'  # Send invitations to attendees
        ).execute()

        return event['id']

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> CalendarEvent:
        """Get a specific event by ID."""
        service = self._get_service()

        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

        return GoogleCalendarMapper.to_event_entity(event)

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
        """Update an existing event."""
        service = self._get_service()
        event_data = GoogleCalendarMapper.from_event_draft(draft)

        service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_data,
            sendUpdates='all'
        ).execute()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def delete_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> None:
        """Delete an event."""
        service = self._get_service()

        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendUpdates='all'
        ).execute()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def list_events(
        self,
        criteria: EventSearchCriteria
    ) -> list[CalendarEvent]:
        """List events based on criteria."""
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def list_calendars(self) -> list[Calendar]:
        """List all calendars for this account."""
        service = self._get_service()

        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])

        return [GoogleCalendarMapper.to_calendar_entity(c) for c in calendars]

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
        """Get free/busy information for calendars."""
        service = self._get_service()

        body = {
            'timeMin': time_min.isoformat() + 'Z',
            'timeMax': time_max.isoformat() + 'Z',
            'items': [{'id': cal_id} for cal_id in calendar_ids]
        }

        return service.freebusy().query(body=body).execute()
```

#### 3.3. Google Calendar Account Manager (app/infrastructure/connectors/google_calendar/account_manager.py)
```python
"""
Multi-account manager for Google Calendar.
Similar to Gmail account manager.
"""
from typing import Optional, Dict
from app.infrastructure.connectors.google_calendar.client import GoogleCalendarClient


class GoogleCalendarAccountManager:
    """Manages multiple Google Calendar accounts."""

    def __init__(self):
        self._clients: Dict[str, GoogleCalendarClient] = {}
        self._default_account: Optional[str] = None

    def add_account(self, account_id: str) -> GoogleCalendarClient:
        """Add or get calendar client for an account."""
        if account_id not in self._clients:
            self._clients[account_id] = GoogleCalendarClient(account_id=account_id)

            if self._default_account is None:
                self._default_account = account_id

        return self._clients[account_id]

    def get_client(self, account_id: Optional[str] = None) -> GoogleCalendarClient:
        """Get client for specific account or default."""
        if account_id is None:
            account_id = self._default_account

        if account_id is None:
            raise ValueError("No default account set")

        if account_id not in self._clients:
            return self.add_account(account_id)

        return self._clients[account_id]

    def set_default_account(self, account_id: str) -> None:
        """Set default account."""
        if account_id not in self._clients:
            self.add_account(account_id)
        self._default_account = account_id

    def list_accounts(self) -> list[str]:
        """List all configured accounts."""
        return list(self._clients.keys())


# Global instance
google_calendar_account_manager = GoogleCalendarAccountManager()
```

#### 3.4. Google Calendar Schemas (app/infrastructure/connectors/google_calendar/schemas.py)
```python
"""
Mappers between Google Calendar API responses and domain entities.
"""
from datetime import datetime
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
        """Convert Google Calendar API calendar to domain entity."""
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
        """Convert Google Calendar API event to domain entity."""
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
        if 'recurrence' in api_data:
            recurrence = EventRecurrence(
                rrule=api_data['recurrence'][0]  # First rule
            )

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
            html_link=api_data.get('htmlLink'),
            provider=CalendarProvider.GOOGLE
        )

    @staticmethod
    def from_event_draft(draft: CalendarEventDraft) -> dict:
        """Convert domain event draft to Google Calendar API format."""
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
                {'email': att.email, 'optional': att.optional}
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
        if draft.recurrence:
            event_data['recurrence'] = [draft.recurrence.rrule]
        if draft.color_id:
            event_data['colorId'] = draft.color_id
        if draft.visibility:
            event_data['visibility'] = draft.visibility

        return event_data

    @staticmethod
    def _parse_event_datetime(data: dict) -> EventDateTime:
        """Parse event datetime from API response."""
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
        """Format event datetime for API request."""
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
        """Parse attendee from API response."""
        return CalendarAttendee(
            email=data['email'],
            display_name=data.get('displayName'),
            response_status=AttendeeResponseStatus(data.get('responseStatus', 'needsAction')),
            optional=data.get('optional', False),
            organizer=data.get('organizer', False),
            comment=data.get('comment')
        )
```

### Fase 4: Infrastructure Layer - Apple Calendar (CalDAV)

#### 4.1. Apple Calendar Auth (app/infrastructure/connectors/apple_calendar/auth.py)
```python
"""
Apple Calendar (CalDAV) authentication handler.
Uses app-specific passwords for iCloud.
"""
from pathlib import Path
from typing import Optional
import json
from app.config.settings import settings


class AppleCalendarAuthHandler:
    """Handles authentication for Apple Calendar (CalDAV)."""

    def __init__(
        self,
        account_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        caldav_url: Optional[str] = None,
        tokens_dir: Optional[Path] = None
    ):
        self.account_id = account_id
        self.username = username or settings.apple_calendar_username
        self.password = password or settings.apple_calendar_password
        self.caldav_url = caldav_url or settings.apple_calendar_url or "https://caldav.icloud.com"
        self.tokens_dir = tokens_dir or settings.apple_calendar_tokens_dir

    def _ensure_tokens_dir(self) -> None:
        """Ensure tokens directory exists."""
        self.tokens_dir.mkdir(parents=True, exist_ok=True)

    @property
    def credentials_file(self) -> Path:
        """Get the credentials file path for this account."""
        safe_account_id = self.account_id.replace('@', '_at_').replace('.', '_')
        return self.tokens_dir / f"credentials_{safe_account_id}.json"

    def save_credentials(self, username: str, password: str, url: str) -> None:
        """Save CalDAV credentials securely."""
        self._ensure_tokens_dir()
        credentials = {
            'username': username,
            'password': password,
            'url': url
        }
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f)

    def load_credentials(self) -> tuple[str, str, str]:
        """Load saved credentials."""
        if self.credentials_file.exists():
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)
                return creds['username'], creds['password'], creds['url']

        if self.username and self.password:
            return self.username, self.password, self.caldav_url

        raise ValueError("No credentials available for Apple Calendar")

    def revoke_credentials(self) -> None:
        """Delete stored credentials."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()

    @property
    def is_authenticated(self) -> bool:
        """Check if credentials are available."""
        try:
            self.load_credentials()
            return True
        except ValueError:
            return False
```

#### 4.2. Apple Calendar Client (app/infrastructure/connectors/apple_calendar/client.py)
```python
"""
Apple Calendar (CalDAV) client implementation.
Uses caldav library for CalDAV protocol.
"""
from typing import Optional
from datetime import datetime
import caldav
from caldav.elements import dav, cdav
from icalendar import Calendar as iCalendar, Event as iEvent
from tenacity import retry, stop_after_attempt, wait_exponential

from app.infrastructure.connectors.apple_calendar.auth import AppleCalendarAuthHandler
from app.infrastructure.connectors.apple_calendar.schemas import AppleCalendarMapper
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
        self.account_id = account_id
        self.auth_handler = auth_handler or AppleCalendarAuthHandler(account_id=account_id)
        self._client: Optional[caldav.DAVClient] = None
        self._principal = None

    def _get_client(self) -> caldav.DAVClient:
        """Get or create CalDAV client."""
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
        """Create a calendar event via CalDAV."""
        client = self._get_client()

        # Get calendar
        calendar = self._get_caldav_calendar(calendar_id)

        # Create iCalendar event
        ical = AppleCalendarMapper.from_event_draft(draft)

        # Save to calendar
        event = calendar.save_event(ical.to_ical())

        return event.id

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> CalendarEvent:
        """Get a specific event by ID."""
        calendar = self._get_caldav_calendar(calendar_id)
        event = calendar.event_by_uid(event_id)

        return AppleCalendarMapper.to_event_entity(event.data)

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
        """Update an existing event."""
        calendar = self._get_caldav_calendar(calendar_id)
        event = calendar.event_by_uid(event_id)

        # Update with new data
        ical = AppleCalendarMapper.from_event_draft(draft)
        event.data = ical.to_ical()
        event.save()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def delete_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> None:
        """Delete an event."""
        calendar = self._get_caldav_calendar(calendar_id)
        event = calendar.event_by_uid(event_id)
        event.delete()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def list_events(
        self,
        criteria: EventSearchCriteria
    ) -> list[CalendarEvent]:
        """List events based on criteria."""
        calendar = self._get_caldav_calendar(criteria.calendar_id)

        # Date range search
        events = calendar.date_search(
            start=criteria.time_min,
            end=criteria.time_max,
            expand=criteria.single_events
        )

        result = []
        for event in events:
            cal_event = AppleCalendarMapper.to_event_entity(event.data)

            # Filter by query if provided
            if criteria.query:
                if criteria.query.lower() in cal_event.summary.lower():
                    result.append(cal_event)
            else:
                result.append(cal_event)

            if len(result) >= criteria.max_results:
                break

        return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def list_calendars(self) -> list[Calendar]:
        """List all calendars for this account."""
        client = self._get_client()
        calendars = self._principal.calendars()

        return [
            AppleCalendarMapper.to_calendar_entity(cal)
            for cal in calendars
        ]

    def _get_caldav_calendar(self, calendar_id: str):
        """Get CalDAV calendar by ID."""
        if calendar_id == "primary":
            # Get default calendar
            calendars = self._principal.calendars()
            return calendars[0] if calendars else None
        else:
            # Find calendar by ID
            for cal in self._principal.calendars():
                if cal.id == calendar_id:
                    return cal
        raise ValueError(f"Calendar not found: {calendar_id}")
```

#### 4.3. Apple Calendar Schemas (app/infrastructure/connectors/apple_calendar/schemas.py)
```python
"""
Mappers between CalDAV/iCalendar and domain entities.
"""
from datetime import datetime
from icalendar import Calendar as iCalendar, Event as iEvent
import recurring_ical_events

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
        """Convert CalDAV calendar to domain entity."""
        return Calendar(
            id=caldav_calendar.id,
            summary=caldav_calendar.name,
            timezone=str(caldav_calendar.get_property(cdav.CalendarTimezone(), '')),
            provider=CalendarProvider.APPLE,
            is_primary=False  # CalDAV doesn't have primary concept
        )

    @staticmethod
    def to_event_entity(ical_data: str) -> CalendarEvent:
        """Convert iCalendar event to domain entity."""
        ical = iCalendar.from_ical(ical_data)

        for component in ical.walk():
            if component.name == "VEVENT":
                return AppleCalendarMapper._parse_vevent(component)

        raise ValueError("No VEVENT found in iCalendar data")

    @staticmethod
    def from_event_draft(draft: CalendarEventDraft) -> iCalendar:
        """Convert domain event draft to iCalendar format."""
        cal = iCalendar()
        cal.add('prodid', '-//Sumeria Personal Assistant//EN')
        cal.add('version', '2.0')

        event = iEvent()
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

        if draft.description:
            event.add('description', draft.description)
        if draft.location:
            event.add('location', draft.location)

        # Add attendees
        for attendee in draft.attendees:
            event.add('attendee', f'mailto:{attendee.email}', parameters={
                'cn': attendee.display_name or attendee.email,
                'role': 'OPT-PARTICIPANT' if attendee.optional else 'REQ-PARTICIPANT',
                'rsvp': 'TRUE'
            })

        # Add reminders (alarms)
        for reminder in draft.reminders:
            alarm = iCalendar()
            alarm.add('action', 'DISPLAY')
            alarm.add('trigger', f'-PT{reminder.minutes}M')
            event.add_component(alarm)

        # Add recurrence
        if draft.recurrence:
            event.add('rrule', draft.recurrence.rrule)

        event.add('uid', str(datetime.now().timestamp()))
        event.add('dtstamp', datetime.now())

        cal.add_component(event)
        return cal

    @staticmethod
    def _parse_vevent(vevent) -> CalendarEvent:
        """Parse VEVENT component to CalendarEvent."""
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
                email = str(att).replace('mailto:', '')
                attendees.append(CalendarAttendee(email=email))

        # Parse recurrence
        recurrence = None
        if 'rrule' in vevent:
            recurrence = EventRecurrence(rrule=str(vevent['rrule']))

        return CalendarEvent(
            id=str(vevent.get('uid', '')),
            summary=summary,
            start=start,
            end=end,
            description=description,
            location=location,
            attendees=attendees,
            recurrence=recurrence,
            provider=CalendarProvider.APPLE
        )

    @staticmethod
    def _parse_ical_datetime(dt_prop) -> EventDateTime:
        """Parse iCalendar datetime property."""
        if dt_prop is None:
            return EventDateTime()

        dt = dt_prop.dt

        if isinstance(dt, datetime):
            return EventDateTime(datetime=dt)
        else:  # date object
            return EventDateTime(date=dt.isoformat())
```

### Fase 5: Application Layer (Use Cases)

#### 5.1. Google Calendar Use Cases
Implementar los siguientes use cases siguiendo el patrón de Gmail:

- `CreateEventUseCase` - Crear evento
- `GetEventUseCase` - Obtener evento por ID
- `UpdateEventUseCase` - Actualizar evento
- `DeleteEventUseCase` - Eliminar evento
- `ListEventsUseCase` - Listar eventos con criterios
- `SearchEventsUseCase` - Buscar eventos
- `ListCalendarsUseCase` - Listar calendarios

Ejemplo de `CreateEventUseCase`:
```python
@dataclass
class CreateEventRequest:
    """Request to create a calendar event."""
    summary: str
    start_datetime: Optional[datetime] = None
    start_date: Optional[str] = None
    end_datetime: Optional[datetime] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: list[str] = field(default_factory=list)
    reminders_minutes: list[int] = field(default_factory=list)
    calendar_id: str = "primary"
    account_id: Optional[str] = None
    provider: str = "google"  # google or apple


@dataclass
class CreateEventResponse:
    """Response after creating an event."""
    success: bool
    event_id: Optional[str] = None
    html_link: Optional[str] = None
    error: Optional[str] = None


class CreateEventUseCase:
    """Use case for creating calendar events."""

    async def execute(self, request: CreateEventRequest) -> CreateEventResponse:
        """Create a calendar event."""
        try:
            # Build event draft
            draft = CalendarEventDraft(
                summary=request.summary,
                start=EventDateTime(
                    datetime=request.start_datetime,
                    date=request.start_date
                ),
                end=EventDateTime(
                    datetime=request.end_datetime,
                    date=request.end_date
                ),
                description=request.description,
                location=request.location,
                attendees=[CalendarAttendee(email=e) for e in request.attendees],
                reminders=[EventReminder(minutes=m) for m in request.reminders_minutes]
            )

            # Choose provider
            if request.provider == "google":
                from app.infrastructure.connectors.google_calendar.account_manager import (
                    google_calendar_account_manager
                )
                client = google_calendar_account_manager.get_client(request.account_id)
            else:  # apple
                from app.infrastructure.connectors.apple_calendar.client import (
                    AppleCalendarClient
                )
                client = AppleCalendarClient(account_id=request.account_id or "default")

            # Create event
            event_id = await client.create_event(request.calendar_id, draft)

            # Get event details for link
            event = await client.get_event(request.calendar_id, event_id)

            return CreateEventResponse(
                success=True,
                event_id=event_id,
                html_link=event.html_link
            )

        except Exception as e:
            return CreateEventResponse(
                success=False,
                error=str(e)
            )
```

#### 5.2. Apple Calendar Use Cases
Similar a Google Calendar, pero usando `AppleCalendarClient`.

### Fase 6: MCP Tools Layer

#### 6.1. Unified Calendar Tools (app/mcp/tools/calendar_tools.py)
```python
"""
MCP Tools for Calendar operations (Google Calendar & Apple Calendar).
Unified interface for both providers.
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

from app.application.use_cases.google_calendar.create_event import (
    CreateEventUseCase,
    CreateEventRequest
)
from app.application.use_cases.google_calendar.list_events import (
    ListEventsUseCase,
    ListEventsRequest
)
from app.application.use_cases.google_calendar.list_calendars import (
    ListCalendarsUseCase,
    ListCalendarsRequest
)
# ... more imports


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
        # ... more use cases

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
        # Parse datetimes
        start_dt = datetime.fromisoformat(start_datetime) if start_datetime else None
        end_dt = datetime.fromisoformat(end_datetime) if end_datetime else None

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
        time_min_dt = datetime.fromisoformat(time_min) if time_min else None
        time_max_dt = datetime.fromisoformat(time_max) if time_max else None

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
        events = [
            EventSummary(
                id=event.id,
                summary=event.summary,
                start=event.start.datetime.isoformat() if event.start.datetime else event.start.date,
                end=event.end.datetime.isoformat() if event.end.datetime else event.end.date,
                location=event.location,
                attendees_count=len(event.attendees),
                is_recurring=event.recurrence is not None,
                html_link=event.html_link
            )
            for event in response.events
        ]

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
            success=True,
            calendars=calendars
        )


# Global instance
calendar_tools = CalendarTools()
```

#### 6.2. Registrar Tools en main.py
```python
from app.mcp.tools.calendar_tools import calendar_tools

# Calendar Tools
@mcp.tool()
async def calendar_create_event(
    summary: str,
    start_datetime: str = None,
    start_date: str = None,
    end_datetime: str = None,
    end_date: str = None,
    description: str = None,
    location: str = None,
    attendees: list[str] = None,
    reminders_minutes: list[int] = None,
    calendar_id: str = "primary",
    provider: str = "google",
    account_id: str = None
):
    """
    Create a new calendar event.

    Supports both Google Calendar and Apple Calendar.
    Use start_datetime/end_datetime for timed events, or start_date/end_date for all-day events.
    """
    return await calendar_tools.create_event(
        summary=summary,
        start_datetime=start_datetime,
        start_date=start_date,
        end_datetime=end_datetime,
        end_date=end_date,
        description=description,
        location=location,
        attendees=attendees,
        reminders_minutes=reminders_minutes,
        calendar_id=calendar_id,
        provider=provider,
        account_id=account_id
    )

@mcp.tool()
async def calendar_list_events(
    calendar_id: str = "primary",
    time_min: str = None,
    time_max: str = None,
    query: str = None,
    max_results: int = 10,
    provider: str = "google",
    account_id: str = None
):
    """
    List calendar events.

    Filter by time range, search query, or both.
    """
    return await calendar_tools.list_events(
        calendar_id=calendar_id,
        time_min=time_min,
        time_max=time_max,
        query=query,
        max_results=max_results,
        provider=provider,
        account_id=account_id
    )

@mcp.tool()
async def calendar_list_calendars(
    provider: str = "google",
    account_id: str = None
):
    """
    List all available calendars.

    Shows calendars from Google or Apple depending on provider.
    """
    return await calendar_tools.list_calendars(
        provider=provider,
        account_id=account_id
    )

@mcp.tool()
async def calendar_update_event(
    event_id: str,
    calendar_id: str = "primary",
    summary: str = None,
    start_datetime: str = None,
    end_datetime: str = None,
    description: str = None,
    location: str = None,
    provider: str = "google",
    account_id: str = None
):
    """Update an existing calendar event."""
    return await calendar_tools.update_event(...)

@mcp.tool()
async def calendar_delete_event(
    event_id: str,
    calendar_id: str = "primary",
    provider: str = "google",
    account_id: str = None
):
    """Delete a calendar event."""
    return await calendar_tools.delete_event(...)

@mcp.prompt(title="Calendar Assistant")
def calendar_assistant():
    """Helpful calendar management assistant prompt."""
    return [
        base.UserMessage(
            "You are a helpful calendar management assistant supporting both Google Calendar and Apple Calendar. "
            "I can help you with:\n"
            "- Creating events with attendees and reminders\n"
            "- Listing and searching events\n"
            "- Managing multiple calendars\n"
            "- Updating and deleting events\n"
            "- Working with recurring events\n\n"
            "What would you like to do with your calendar?"
        )
    ]
```

### Fase 7: Tests

#### 7.1. Unit Tests Structure
```
tests/unit/
├── infrastructure/connectors/
│   ├── google_calendar/
│   │   ├── test_client.py
│   │   ├── test_oauth.py
│   │   └── test_schemas.py
│   └── apple_calendar/
│       ├── test_client.py
│       ├── test_auth.py
│       └── test_schemas.py
├── application/use_cases/
│   ├── google_calendar/
│   │   ├── test_create_event.py
│   │   └── test_list_events.py
│   └── apple_calendar/
│       ├── test_create_event.py
│       └── test_list_events.py
└── mcp/tools/
    └── test_calendar_tools.py
```

### Fase 8: Documentación

#### 8.1. Google Calendar Setup (docs/google-calendar-setup.md)
```markdown
# Google Calendar Setup

## 1. Create Google Cloud Project
- Go to Google Cloud Console
- Create new project
- Enable Google Calendar API

## 2. Create OAuth Credentials
- Navigate to APIs & Services > Credentials
- Create OAuth 2.0 Client ID
- Download credentials JSON

## 3. Configure Sumeria
```bash
# .env
GOOGLE_CALENDAR_CREDENTIALS_FILE=/path/to/credentials.json
```

## 4. First-time Authentication
```bash
# Run any calendar command - will open browser for auth
```

## 5. Multi-Account Support
Each account stores separate tokens in:
`~/.sumeria/tokens/google_calendar/token_{account_id}.json`
```

#### 8.2. Apple Calendar Setup (docs/apple-calendar-setup.md)
```markdown
# Apple Calendar (iCloud) Setup

## 1. Generate App-Specific Password
- Go to appleid.apple.com
- Sign in
- Generate app-specific password

## 2. Configure Sumeria
```bash
# .env
APPLE_CALENDAR_URL=https://caldav.icloud.com
APPLE_CALENDAR_USERNAME=your.apple.id@icloud.com
APPLE_CALENDAR_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App-specific password
```

## 3. Test Connection
The first calendar operation will validate credentials.

## Notes
- Use app-specific password, not your main Apple ID password
- CalDAV URL for iCloud: `https://caldav.icloud.com`
```

## MCP Tools Expuestos

| Tool | Descripción | Soporta Google | Soporta Apple |
|------|-------------|----------------|---------------|
| `calendar_create_event` | Crear evento | ✅ | ✅ |
| `calendar_list_events` | Listar eventos | ✅ | ✅ |
| `calendar_update_event` | Actualizar evento | ✅ | ✅ |
| `calendar_delete_event` | Eliminar evento | ✅ | ✅ |
| `calendar_list_calendars` | Listar calendarios | ✅ | ✅ |
| `calendar_search_events` | Buscar eventos | ✅ | ✅ |
| `calendar_get_free_busy` | Obtener disponibilidad | ✅ | ⚠️ Limitado |

## Consideraciones Técnicas

### Autenticación

#### Google Calendar
- OAuth2 con refresh tokens
- Multi-account support (similar a Gmail)
- Tokens almacenados localmente
- Auto-refresh cuando expiran

#### Apple Calendar
- Basic Auth con app-specific password
- No OAuth (CalDAV usa credenciales directas)
- Almacenamiento seguro de credenciales
- Soporte para iCloud y otros servidores CalDAV

### Rate Limiting
- **Google Calendar**: 1,000,000 requests/day, ~10 req/second per user
- **Apple iCloud**: ~240 requests/hour (más restrictivo)
- Implementar retry con exponential backoff (tenacity)
- Usar @retry decorator en todos los métodos

### Manejo de Errores
- Validación de event_id y calendar_id
- Manejo de permisos insuficientes
- Errores de red y timeouts
- Conflictos de eventos (overlapping)

### Zonas Horarias
- Soporte completo para timezones
- Conversión automática según calendar timezone
- All-day events vs timed events
- UTC como fallback

### Recurrencia
- RRULE format (RFC 5545)
- Expansión de eventos recurrentes
- Excepciones (EXDATE)
- Modificación de instancias específicas

## Orden de Implementación

1. **Fase 1**: Configuración y dependencias (30 min)
   - Actualizar pyproject.toml
   - Actualizar settings.py

2. **Fase 2**: Domain entities (1.5 horas)
   - calendar.py
   - calendar_event.py
   - calendar_attendee.py

3. **Fase 3**: Google Calendar Infrastructure (3 horas)
   - oauth.py (adaptar de Gmail)
   - client.py
   - account_manager.py
   - schemas.py

4. **Fase 4**: Apple Calendar Infrastructure (3 horas)
   - auth.py
   - client.py
   - schemas.py (iCalendar mappers)

5. **Fase 5**: Use cases Google Calendar (2 horas)
   - CreateEventUseCase
   - ListEventsUseCase
   - UpdateEventUseCase
   - DeleteEventUseCase
   - ListCalendarsUseCase

6. **Fase 6**: Use cases Apple Calendar (2 horas)
   - Same as Google Calendar

7. **Fase 7**: MCP Tools (2 horas)
   - calendar_tools.py (unified)
   - Registrar en main.py
   - Crear prompt

8. **Fase 8**: Tests (3 horas)
   - Unit tests para clients
   - Unit tests para schemas
   - Unit tests para use cases
   - Unit tests para tools

9. **Fase 9**: Documentación (1 hora)
   - google-calendar-setup.md
   - apple-calendar-setup.md
   - Actualizar README

## Tiempo Estimado Total
**~18 horas** de implementación

## Variables de Entorno Requeridas

```bash
# .env

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_FILE=/home/user/.sumeria/google_calendar_credentials.json
GOOGLE_CALENDAR_TOKENS_DIR=/home/user/.sumeria/tokens/google_calendar

# Apple Calendar (iCloud)
APPLE_CALENDAR_URL=https://caldav.icloud.com
APPLE_CALENDAR_USERNAME=your.apple.id@icloud.com
APPLE_CALENDAR_PASSWORD=xxxx-xxxx-xxxx-xxxx
APPLE_CALENDAR_TOKENS_DIR=/home/user/.sumeria/tokens/apple_calendar
```

## Casos de Uso Principales

### 1. Crear reunión con recordatorios
```python
calendar_create_event(
    summary="Team Standup",
    start_datetime="2026-01-10T09:00:00-08:00",
    end_datetime="2026-01-10T09:30:00-08:00",
    description="Daily team sync",
    location="Conference Room A",
    attendees=["alice@example.com", "bob@example.com"],
    reminders_minutes=[15, 30],
    provider="google"
)
```

### 2. Evento de día completo
```python
calendar_create_event(
    summary="Company Holiday",
    start_date="2026-01-15",
    end_date="2026-01-16",
    provider="apple"
)
```

### 3. Listar eventos de la semana
```python
calendar_list_events(
    time_min="2026-01-06T00:00:00Z",
    time_max="2026-01-13T23:59:59Z",
    max_results=50,
    provider="google"
)
```

### 4. Buscar eventos por keyword
```python
calendar_list_events(
    query="standup",
    provider="google"
)
```

### 5. Listar calendarios
```python
calendar_list_calendars(
    provider="apple"
)
```

## Dependencias entre Componentes

```
Settings
   ├─→ Google Calendar
   │      ├─→ OAuth Handler ─→ Client ─→ Use Cases ─→ Tools
   │      └─→ Account Manager
   │
   └─→ Apple Calendar
          ├─→ Auth Handler ─→ Client ─→ Use Cases ─→ Tools
          └─→ Schemas (iCalendar)
                                              │
                                              ↓
                                          MCP Server
```

## Criterios de Aceptación

- ✅ Todas las entidades de dominio definidas
- ✅ Google Calendar OAuth funcionando con multi-account
- ✅ Apple Calendar CalDAV funcionando
- ✅ Clients con operaciones CRUD completas
- ✅ Mappers bidireccionales para ambos providers
- ✅ Use cases con manejo de errores robusto
- ✅ MCP tools unificados registrados
- ✅ Soporte para eventos recurrentes
- ✅ Manejo de attendees y reminders
- ✅ Tests unitarios >80% coverage
- ✅ Documentación completa de setup
- ✅ Compatible con arquitectura existente

## Próximos Pasos (Post-Implementación)

1. **Sincronización bidireccional**
   - Webhooks de Google Calendar para cambios en tiempo real
   - Polling para Apple Calendar (CalDAV no soporta webhooks nativos)

2. **Características avanzadas**
   - Búsqueda de disponibilidad (free/busy)
   - Sugerencias de horarios automáticas
   - Detección de conflictos

3. **Integraciones**
   - Crear eventos desde emails (Gmail → Calendar)
   - Agregar tareas de Notion como eventos
   - Recordatorios vía WhatsApp

4. **Optimizaciones**
   - Caché con Redis para reducir llamadas API
   - Batch operations para múltiples eventos
   - Rate limiting inteligente

5. **UX Improvements**
   - Natural language parsing ("tomorrow at 3pm")
   - Recurring event templates
   - Smart scheduling assistant

6. **Outlook/Exchange Support**
   - Añadir soporte para Microsoft Calendar
   - Usar Microsoft Graph API
   - Unified provider interface

---

**Nota**: Este plan sigue estrictamente la arquitectura DDD establecida en el proyecto y mantiene consistencia con las integraciones existentes (Gmail, Notion, Holded, WhatsApp). La implementación es provider-agnostic a nivel de MCP tools, permitiendo usar Google Calendar y Apple Calendar de forma intercambiable.

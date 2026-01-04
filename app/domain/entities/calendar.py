"""
Calendar domain entity.
Represents a calendar from any provider (Google, Apple, etc.).
"""
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

"""
Notion Database domain entity.
Represents databases and database entries in Notion.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class NotionDatabase:
    """
    Notion database entity.
    Maps to Notion databases API.
    """
    id: Optional[str] = None
    title: str = ""

    # Properties schema
    properties: dict = field(default_factory=dict)

    # Parent information
    parent_type: str = "page_id"
    parent_id: Optional[str] = None

    # Visual elements
    icon: Optional[dict] = None
    cover: Optional[dict] = None

    # Metadata
    url: Optional[str] = None
    archived: bool = False
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None

    def get_property_names(self) -> list[str]:
        """Get list of property names in this database."""
        return list(self.properties.keys())


@dataclass
class NotionDatabaseEntry:
    """
    Entry (page) in a Notion database.
    Represents a row in a database.
    """
    id: Optional[str] = None
    database_id: Optional[str] = None

    # Properties with values
    properties: dict = field(default_factory=dict)

    # Visual elements
    icon: Optional[dict] = None
    cover: Optional[dict] = None

    # Metadata
    url: Optional[str] = None
    archived: bool = False
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    created_by: Optional[str] = None
    last_edited_by: Optional[str] = None

    def get_property_value(self, property_name: str) -> Optional[any]:
        """Get value of a specific property."""
        return self.properties.get(property_name)


@dataclass
class NotionDatabaseEntryDraft:
    """Draft for creating a new database entry."""
    database_id: str
    properties: dict
    icon: Optional[dict] = None
    cover: Optional[dict] = None
    children: Optional[list] = None  # Initial content blocks


@dataclass
class NotionDatabaseQuery:
    """
    Query criteria for database.
    Maps to Notion database query API.
    """
    database_id: str
    filter: Optional[dict] = None
    sorts: Optional[list] = None
    start_cursor: Optional[str] = None
    page_size: int = 100

    def has_filter(self) -> bool:
        """Check if query has filters."""
        return self.filter is not None

    def has_sorts(self) -> bool:
        """Check if query has sorting."""
        return self.sorts is not None and len(self.sorts) > 0

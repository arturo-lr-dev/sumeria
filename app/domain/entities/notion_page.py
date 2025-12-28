"""
Notion Page domain entity.
Represents pages in Notion workspace.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class NotionPage:
    """
    Notion page entity representing a page in workspace.
    Maps to Notion pages API.
    """
    id: Optional[str] = None
    title: str = ""

    # Parent information
    parent_type: str = "page_id"  # page_id, database_id, workspace
    parent_id: Optional[str] = None

    # Visual elements
    icon: Optional[dict] = None
    cover: Optional[dict] = None

    # Properties (for database pages)
    properties: dict = field(default_factory=dict)

    # Metadata
    url: Optional[str] = None
    archived: bool = False
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    created_by: Optional[str] = None
    last_edited_by: Optional[str] = None

    def is_database_page(self) -> bool:
        """Check if this page is a database entry."""
        return self.parent_type == "database_id"

    def is_workspace_page(self) -> bool:
        """Check if this page is a top-level workspace page."""
        return self.parent_type == "workspace"


@dataclass
class NotionPageDraft:
    """Draft for creating a new page."""
    title: str
    parent_id: str
    parent_type: str = "page_id"  # page_id, database_id, workspace
    properties: Optional[dict] = None
    children: Optional[list] = None  # Initial content blocks
    icon: Optional[dict] = None
    cover: Optional[dict] = None


@dataclass
class NotionPageSearchCriteria:
    """Criteria for searching pages."""
    query: Optional[str] = None
    filter_type: Optional[str] = None  # "page" or "database"
    sort_direction: str = "descending"  # ascending or descending
    sort_timestamp: str = "last_edited_time"  # last_edited_time or created_time
    max_results: int = 100

"""
Notion Block domain entity.
Represents content blocks in Notion pages.
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime


@dataclass
class NotionBlock:
    """
    Notion block (content element).
    Blocks are the building blocks of content in Notion.

    Supported block types:
    - Text: paragraph, heading_1/2/3, bulleted_list_item, numbered_list_item, to_do, toggle, quote, callout, code
    - Media: image, video, file, pdf, bookmark
    - Embeds: embed, link_preview
    - Database: child_database, child_page, table, table_row
    - Layout: divider, table_of_contents, breadcrumb, column_list, column, synced_block
    - Advanced: template, link_to_page, equation
    """
    id: Optional[str] = None
    type: str = "paragraph"

    # Raw content from API (varies by type)
    content: dict = field(default_factory=dict)

    # Extracted plain text (computed from content based on block type)
    text: Optional[str] = None

    # Table-specific extracted data
    table_width: Optional[int] = None
    has_column_header: Optional[bool] = None
    has_row_header: Optional[bool] = None
    cells: Optional[list[list[str]]] = None  # For table_row: text extracted from cells

    # Code block specific
    language: Optional[str] = None

    # Image/File/Media specific
    url: Optional[str] = None
    caption: Optional[str] = None

    # Children blocks
    has_children: bool = False
    children: list = field(default_factory=list)

    # Metadata
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    created_by: Optional[str] = None
    last_edited_by: Optional[str] = None
    archived: bool = False

    def is_text_block(self) -> bool:
        """Check if this is a text-based block."""
        text_types = [
            "paragraph", "heading_1", "heading_2", "heading_3",
            "bulleted_list_item", "numbered_list_item", "to_do",
            "toggle", "quote", "callout", "code"
        ]
        return self.type in text_types

    def is_table_block(self) -> bool:
        """Check if this is a table block."""
        return self.type == "table"

    def is_table_row(self) -> bool:
        """Check if this is a table row block."""
        return self.type == "table_row"

    def is_media_block(self) -> bool:
        """Check if this is a media block."""
        media_types = ["image", "video", "file", "pdf", "bookmark"]
        return self.type in media_types

    def is_container_block(self) -> bool:
        """Check if this block can contain children."""
        return self.has_children

    def get_text(self) -> str:
        """
        Extract plain text from block content.

        Returns:
            Plain text string, or empty string if no text available
        """
        # If text was already extracted, return it
        if self.text is not None:
            return self.text

        if not self.content:
            return ""

        # Get rich_text array from content
        rich_text = self.content.get("rich_text", [])

        if not rich_text:
            return ""

        # Concatenate all plain_text from rich text items
        return "".join(
            item.get("plain_text", "")
            for item in rich_text
        )

    def to_dict(self, include_content: bool = False, include_metadata: bool = False) -> dict:
        """
        Convert block to dictionary with relevant fields.

        Args:
            include_content: Include raw content from API
            include_metadata: Include created_time, created_by, etc.

        Returns:
            Dictionary representation of the block
        """
        result = {
            "id": self.id,
            "type": self.type,
            "has_children": self.has_children,
        }

        # Add type-specific fields
        if self.text:
            result["text"] = self.text

        if self.cells:
            result["cells"] = self.cells

        if self.table_width is not None:
            result["table_width"] = self.table_width
            result["has_column_header"] = self.has_column_header
            result["has_row_header"] = self.has_row_header

        if self.language:
            result["language"] = self.language

        if self.url:
            result["url"] = self.url

        if self.caption:
            result["caption"] = self.caption

        if self.children:
            result["children"] = [
                child.to_dict(include_content=include_content, include_metadata=include_metadata)
                for child in self.children
            ]

        if include_content:
            result["content"] = self.content

        if include_metadata:
            result["created_time"] = self.created_time.isoformat() if self.created_time else None
            result["last_edited_time"] = self.last_edited_time.isoformat() if self.last_edited_time else None
            result["created_by"] = self.created_by
            result["last_edited_by"] = self.last_edited_by
            result["archived"] = self.archived

        return result


@dataclass
class NotionBlockDraft:
    """
    Draft for creating a new block.
    Used when appending content to pages.
    """
    type: str
    content: dict
    children: Optional[list] = None


# Common block type helpers
@dataclass
class ParagraphBlock:
    """Helper for creating paragraph blocks."""
    text: str
    color: str = "default"

    def to_draft(self) -> NotionBlockDraft:
        """Convert to block draft."""
        return NotionBlockDraft(
            type="paragraph",
            content={
                "rich_text": [{"type": "text", "text": {"content": self.text}}],
                "color": self.color
            }
        )


@dataclass
class HeadingBlock:
    """Helper for creating heading blocks."""
    text: str
    level: int = 1  # 1, 2, or 3
    color: str = "default"

    def to_draft(self) -> NotionBlockDraft:
        """Convert to block draft."""
        return NotionBlockDraft(
            type=f"heading_{self.level}",
            content={
                "rich_text": [{"type": "text", "text": {"content": self.text}}],
                "color": self.color
            }
        )


@dataclass
class BulletedListItemBlock:
    """Helper for creating bulleted list item blocks."""
    text: str
    color: str = "default"

    def to_draft(self) -> NotionBlockDraft:
        """Convert to block draft."""
        return NotionBlockDraft(
            type="bulleted_list_item",
            content={
                "rich_text": [{"type": "text", "text": {"content": self.text}}],
                "color": self.color
            }
        )


@dataclass
class ToDoBlock:
    """Helper for creating to-do blocks."""
    text: str
    checked: bool = False
    color: str = "default"

    def to_draft(self) -> NotionBlockDraft:
        """Convert to block draft."""
        return NotionBlockDraft(
            type="to_do",
            content={
                "rich_text": [{"type": "text", "text": {"content": self.text}}],
                "checked": self.checked,
                "color": self.color
            }
        )

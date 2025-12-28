"""
Notion Block domain entity.
Represents content blocks in Notion pages.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class NotionBlock:
    """
    Notion block (content element).
    Blocks are the building blocks of content in Notion.
    """
    id: Optional[str] = None
    type: str = "paragraph"  # paragraph, heading_1, heading_2, heading_3, bulleted_list_item, etc.

    # Content (varies by type)
    content: dict = field(default_factory=dict)

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
            "toggle", "quote", "callout"
        ]
        return self.type in text_types

    def is_container_block(self) -> bool:
        """Check if this block can contain children."""
        return self.has_children


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

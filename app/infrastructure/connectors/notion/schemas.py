"""
Notion API schemas and mappers.
Converts between Notion API responses and domain entities.
"""
from typing import Optional, Any
from datetime import datetime

from app.domain.entities.notion_page import NotionPage, NotionPageDraft
from app.domain.entities.notion_database import (
    NotionDatabase,
    NotionDatabaseEntry,
    NotionDatabaseEntryDraft
)
from app.domain.entities.notion_block import NotionBlock, NotionBlockDraft


class NotionMapper:
    """
    Maps between Notion API responses and domain entities.
    """

    # ============ Page Mapping ============

    @staticmethod
    def to_page_entity(api_data: dict) -> NotionPage:
        """
        Convert Notion API page response to NotionPage entity.

        Args:
            api_data: Raw API response data

        Returns:
            NotionPage entity
        """
        # Extract title
        title = ""
        properties = api_data.get("properties", {})

        # Try to get title from different property types
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_array = prop_data.get("title", [])
                if title_array:
                    title = title_array[0].get("plain_text", "")
                break

        # Extract parent info
        parent = api_data.get("parent", {})
        parent_type = parent.get("type", "workspace")
        parent_id = None

        if parent_type == "page_id":
            parent_id = parent.get("page_id")
        elif parent_type == "database_id":
            parent_id = parent.get("database_id")
        elif parent_type == "workspace":
            parent_id = None

        # Parse timestamps
        created_time = None
        if api_data.get("created_time"):
            created_time = datetime.fromisoformat(
                api_data["created_time"].replace("Z", "+00:00")
            )

        last_edited_time = None
        if api_data.get("last_edited_time"):
            last_edited_time = datetime.fromisoformat(
                api_data["last_edited_time"].replace("Z", "+00:00")
            )

        return NotionPage(
            id=api_data.get("id"),
            title=title,
            parent_type=parent_type,
            parent_id=parent_id,
            icon=api_data.get("icon"),
            cover=api_data.get("cover"),
            properties=properties,
            url=api_data.get("url"),
            archived=api_data.get("archived", False),
            created_time=created_time,
            last_edited_time=last_edited_time,
            created_by=api_data.get("created_by", {}).get("id"),
            last_edited_by=api_data.get("last_edited_by", {}).get("id")
        )

    @staticmethod
    def from_page_draft(draft: NotionPageDraft) -> dict:
        """
        Convert NotionPageDraft to Notion API request format.

        Args:
            draft: Page draft

        Returns:
            API request data
        """
        # Build parent object
        parent = {}
        if draft.parent_type == "page_id":
            parent = {"page_id": draft.parent_id}
        elif draft.parent_type == "database_id":
            parent = {"database_id": draft.parent_id}
        elif draft.parent_type == "workspace":
            parent = {"workspace": True}

        # Build properties
        properties = draft.properties or {}

        # If no properties provided, create default title property
        if not properties:
            properties = {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": draft.title
                            }
                        }
                    ]
                }
            }

        data = {
            "parent": parent,
            "properties": properties
        }

        # Add optional fields
        if draft.icon:
            data["icon"] = draft.icon

        if draft.cover:
            data["cover"] = draft.cover

        if draft.children:
            data["children"] = draft.children

        return data

    # ============ Database Mapping ============

    @staticmethod
    def to_database_entity(api_data: dict) -> NotionDatabase:
        """
        Convert Notion API database response to NotionDatabase entity.

        Args:
            api_data: Raw API response data

        Returns:
            NotionDatabase entity
        """
        # Extract title
        title = ""
        title_array = api_data.get("title", [])
        if title_array:
            title = title_array[0].get("plain_text", "")

        # Extract parent info
        parent = api_data.get("parent", {})
        parent_type = parent.get("type", "workspace")
        parent_id = None

        if parent_type == "page_id":
            parent_id = parent.get("page_id")
        elif parent_type == "workspace":
            parent_id = None

        # Parse timestamps
        created_time = None
        if api_data.get("created_time"):
            created_time = datetime.fromisoformat(
                api_data["created_time"].replace("Z", "+00:00")
            )

        last_edited_time = None
        if api_data.get("last_edited_time"):
            last_edited_time = datetime.fromisoformat(
                api_data["last_edited_time"].replace("Z", "+00:00")
            )

        return NotionDatabase(
            id=api_data.get("id"),
            title=title,
            properties=api_data.get("properties", {}),
            parent_type=parent_type,
            parent_id=parent_id,
            icon=api_data.get("icon"),
            cover=api_data.get("cover"),
            url=api_data.get("url"),
            archived=api_data.get("archived", False),
            created_time=created_time,
            last_edited_time=last_edited_time
        )

    @staticmethod
    def to_database_entry_entity(api_data: dict) -> NotionDatabaseEntry:
        """
        Convert Notion API page response (database entry) to NotionDatabaseEntry entity.

        Args:
            api_data: Raw API response data

        Returns:
            NotionDatabaseEntry entity
        """
        # Extract database_id from parent
        database_id = None
        parent = api_data.get("parent", {})
        if parent.get("type") == "database_id":
            database_id = parent.get("database_id")

        # Parse timestamps
        created_time = None
        if api_data.get("created_time"):
            created_time = datetime.fromisoformat(
                api_data["created_time"].replace("Z", "+00:00")
            )

        last_edited_time = None
        if api_data.get("last_edited_time"):
            last_edited_time = datetime.fromisoformat(
                api_data["last_edited_time"].replace("Z", "+00:00")
            )

        return NotionDatabaseEntry(
            id=api_data.get("id"),
            database_id=database_id,
            properties=api_data.get("properties", {}),
            icon=api_data.get("icon"),
            cover=api_data.get("cover"),
            url=api_data.get("url"),
            archived=api_data.get("archived", False),
            created_time=created_time,
            last_edited_time=last_edited_time,
            created_by=api_data.get("created_by", {}).get("id"),
            last_edited_by=api_data.get("last_edited_by", {}).get("id")
        )

    @staticmethod
    def from_database_entry_draft(draft: NotionDatabaseEntryDraft) -> dict:
        """
        Convert NotionDatabaseEntryDraft to Notion API request format.

        Args:
            draft: Database entry draft

        Returns:
            API request data
        """
        data = {
            "parent": {"database_id": draft.database_id},
            "properties": draft.properties
        }

        # Add optional fields
        if draft.icon:
            data["icon"] = draft.icon

        if draft.cover:
            data["cover"] = draft.cover

        if draft.children:
            data["children"] = draft.children

        return data

    # ============ Block Mapping ============

    @staticmethod
    def to_block_entity(api_data: dict) -> NotionBlock:
        """
        Convert Notion API block response to NotionBlock entity.

        Args:
            api_data: Raw API response data

        Returns:
            NotionBlock entity
        """
        block_type = api_data.get("type", "paragraph")

        # Extract content based on block type
        content = api_data.get(block_type, {})

        # Parse timestamps
        created_time = None
        if api_data.get("created_time"):
            created_time = datetime.fromisoformat(
                api_data["created_time"].replace("Z", "+00:00")
            )

        last_edited_time = None
        if api_data.get("last_edited_time"):
            last_edited_time = datetime.fromisoformat(
                api_data["last_edited_time"].replace("Z", "+00:00")
            )

        # Extract type-specific data
        text = None
        table_width = None
        has_column_header = None
        has_row_header = None
        cells = None
        language = None
        url = None
        caption = None

        # Text blocks: extract plain text from rich_text
        if block_type in [
            "paragraph", "heading_1", "heading_2", "heading_3",
            "bulleted_list_item", "numbered_list_item", "to_do",
            "toggle", "quote", "callout", "code"
        ]:
            rich_text = content.get("rich_text", [])
            text = NotionMapper.extract_plain_text_from_rich_text(rich_text)

        # Code blocks: extract language
        if block_type == "code":
            language = content.get("language")

        # Table blocks: extract table properties
        if block_type == "table":
            table_width = content.get("table_width")
            has_column_header = content.get("has_column_header")
            has_row_header = content.get("has_row_header")

        # Table row blocks: extract cells content
        if block_type == "table_row":
            cells_data = content.get("cells", [])
            cells = [
                NotionMapper.extract_plain_text_from_rich_text(cell)
                for cell in cells_data
            ]

        # Media blocks: extract URL and caption
        if block_type in ["image", "video", "file", "pdf"]:
            # Get URL from external or file object
            file_obj = content.get("external") or content.get("file")
            if file_obj:
                url = file_obj.get("url")

            # Extract caption
            caption_array = content.get("caption", [])
            if caption_array:
                caption = NotionMapper.extract_plain_text_from_rich_text(caption_array)

        # Bookmark blocks: extract URL
        if block_type == "bookmark":
            url = content.get("url")
            caption_array = content.get("caption", [])
            if caption_array:
                caption = NotionMapper.extract_plain_text_from_rich_text(caption_array)

        return NotionBlock(
            id=api_data.get("id"),
            type=block_type,
            content=content,
            text=text,
            table_width=table_width,
            has_column_header=has_column_header,
            has_row_header=has_row_header,
            cells=cells,
            language=language,
            url=url,
            caption=caption,
            has_children=api_data.get("has_children", False),
            created_time=created_time,
            last_edited_time=last_edited_time,
            created_by=api_data.get("created_by", {}).get("id"),
            last_edited_by=api_data.get("last_edited_by", {}).get("id"),
            archived=api_data.get("archived", False)
        )

    @staticmethod
    def from_block_draft(draft: NotionBlockDraft) -> dict:
        """
        Convert NotionBlockDraft to Notion API request format.

        Args:
            draft: Block draft

        Returns:
            API request data
        """
        data = {
            "type": draft.type,
            draft.type: draft.content
        }

        if draft.children:
            data["children"] = draft.children

        return data

    # ============ Helper Methods ============

    @staticmethod
    def extract_plain_text_from_rich_text(rich_text_array: list) -> str:
        """
        Extract plain text from Notion rich text array.

        Args:
            rich_text_array: Array of rich text objects

        Returns:
            Concatenated plain text
        """
        if not rich_text_array:
            return ""

        return "".join(
            item.get("plain_text", "")
            for item in rich_text_array
        )

    @staticmethod
    def create_rich_text(text: str) -> list[dict]:
        """
        Create Notion rich text array from plain text.

        Args:
            text: Plain text string

        Returns:
            Rich text array
        """
        return [
            {
                "type": "text",
                "text": {
                    "content": text
                }
            }
        ]

    @staticmethod
    def extract_property_value(property_data: dict) -> Any:
        """
        Extract value from a Notion property object.

        Args:
            property_data: Property data from API

        Returns:
            Extracted value (type varies)
        """
        prop_type = property_data.get("type")

        if prop_type == "title":
            return NotionMapper.extract_plain_text_from_rich_text(
                property_data.get("title", [])
            )
        elif prop_type == "rich_text":
            return NotionMapper.extract_plain_text_from_rich_text(
                property_data.get("rich_text", [])
            )
        elif prop_type == "number":
            return property_data.get("number")
        elif prop_type == "select":
            select_data = property_data.get("select")
            return select_data.get("name") if select_data else None
        elif prop_type == "multi_select":
            return [
                item.get("name")
                for item in property_data.get("multi_select", [])
            ]
        elif prop_type == "date":
            date_data = property_data.get("date")
            return date_data.get("start") if date_data else None
        elif prop_type == "checkbox":
            return property_data.get("checkbox", False)
        elif prop_type == "url":
            return property_data.get("url")
        elif prop_type == "email":
            return property_data.get("email")
        elif prop_type == "phone_number":
            return property_data.get("phone_number")

        return None

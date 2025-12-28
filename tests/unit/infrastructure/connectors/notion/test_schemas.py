"""
Unit tests for Notion schemas and mappers.
"""
import pytest
from datetime import datetime

from app.infrastructure.connectors.notion.schemas import NotionMapper
from app.domain.entities.notion_page import NotionPageDraft
from app.domain.entities.notion_database import NotionDatabaseEntryDraft
from app.domain.entities.notion_block import NotionBlockDraft


class TestNotionMapper:
    """Test NotionMapper class."""

    def test_to_page_entity(self):
        """Test converting API response to NotionPage entity."""
        api_data = {
            "id": "page_123",
            "properties": {
                "title": {
                    "type": "title",
                    "title": [{"plain_text": "Test Page"}]
                }
            },
            "parent": {"type": "page_id", "page_id": "parent_123"},
            "url": "https://notion.so/page_123",
            "archived": False,
            "created_time": "2025-01-01T00:00:00.000Z",
            "last_edited_time": "2025-01-01T12:00:00.000Z",
            "created_by": {"id": "user_123"},
            "last_edited_by": {"id": "user_456"}
        }

        page = NotionMapper.to_page_entity(api_data)

        assert page.id == "page_123"
        assert page.title == "Test Page"
        assert page.parent_type == "page_id"
        assert page.parent_id == "parent_123"
        assert page.url == "https://notion.so/page_123"
        assert page.archived is False
        assert page.created_by == "user_123"
        assert page.last_edited_by == "user_456"
        assert isinstance(page.created_time, datetime)
        assert isinstance(page.last_edited_time, datetime)

    def test_to_page_entity_database_parent(self):
        """Test converting page with database parent."""
        api_data = {
            "id": "page_123",
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "Database Entry"}]
                }
            },
            "parent": {"type": "database_id", "database_id": "db_123"},
            "created_time": "2025-01-01T00:00:00.000Z",
            "last_edited_time": "2025-01-01T00:00:00.000Z"
        }

        page = NotionMapper.to_page_entity(api_data)

        assert page.parent_type == "database_id"
        assert page.parent_id == "db_123"
        assert page.title == "Database Entry"

    def test_from_page_draft(self):
        """Test converting NotionPageDraft to API format."""
        draft = NotionPageDraft(
            title="New Page",
            parent_id="parent_123",
            parent_type="page_id",
            icon={"type": "emoji", "emoji": "📄"},
            cover={"type": "external", "external": {"url": "https://example.com/cover.jpg"}}
        )

        api_data = NotionMapper.from_page_draft(draft)

        assert api_data["parent"] == {"page_id": "parent_123"}
        assert "properties" in api_data
        assert api_data["properties"]["title"]["title"][0]["text"]["content"] == "New Page"
        assert api_data["icon"] == {"type": "emoji", "emoji": "📄"}
        assert api_data["cover"]["type"] == "external"

    def test_from_page_draft_with_properties(self):
        """Test converting page draft with custom properties."""
        properties = {
            "Name": {
                "title": [{"text": {"content": "Custom Title"}}]
            },
            "Status": {
                "select": {"name": "Active"}
            }
        }

        draft = NotionPageDraft(
            title="Page",
            parent_id="db_123",
            parent_type="database_id",
            properties=properties
        )

        api_data = NotionMapper.from_page_draft(draft)

        assert api_data["parent"] == {"database_id": "db_123"}
        assert api_data["properties"] == properties

    def test_to_database_entity(self):
        """Test converting API response to NotionDatabase entity."""
        api_data = {
            "id": "db_123",
            "title": [{"plain_text": "Tasks Database"}],
            "properties": {
                "Name": {"type": "title"},
                "Status": {"type": "select"}
            },
            "parent": {"type": "page_id", "page_id": "page_123"},
            "url": "https://notion.so/db_123",
            "archived": False,
            "created_time": "2025-01-01T00:00:00.000Z",
            "last_edited_time": "2025-01-01T00:00:00.000Z"
        }

        database = NotionMapper.to_database_entity(api_data)

        assert database.id == "db_123"
        assert database.title == "Tasks Database"
        assert "Name" in database.properties
        assert "Status" in database.properties
        assert database.parent_type == "page_id"
        assert database.parent_id == "page_123"

    def test_to_database_entry_entity(self):
        """Test converting API response to NotionDatabaseEntry entity."""
        api_data = {
            "id": "entry_123",
            "parent": {"type": "database_id", "database_id": "db_123"},
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "Task 1"}]
                },
                "Status": {
                    "type": "select",
                    "select": {"name": "In Progress"}
                }
            },
            "url": "https://notion.so/entry_123",
            "created_time": "2025-01-01T00:00:00.000Z",
            "last_edited_time": "2025-01-01T00:00:00.000Z"
        }

        entry = NotionMapper.to_database_entry_entity(api_data)

        assert entry.id == "entry_123"
        assert entry.database_id == "db_123"
        assert "Name" in entry.properties
        assert "Status" in entry.properties

    def test_from_database_entry_draft(self):
        """Test converting NotionDatabaseEntryDraft to API format."""
        properties = {
            "Name": {
                "title": [{"text": {"content": "New Task"}}]
            },
            "Status": {
                "select": {"name": "To Do"}
            }
        }

        draft = NotionDatabaseEntryDraft(
            database_id="db_123",
            properties=properties
        )

        api_data = NotionMapper.from_database_entry_draft(draft)

        assert api_data["parent"] == {"database_id": "db_123"}
        assert api_data["properties"] == properties

    def test_to_block_entity(self):
        """Test converting API response to NotionBlock entity."""
        api_data = {
            "id": "block_123",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"plain_text": "Test content"}],
                "color": "default"
            },
            "has_children": False,
            "created_time": "2025-01-01T00:00:00.000Z",
            "last_edited_time": "2025-01-01T00:00:00.000Z",
            "archived": False
        }

        block = NotionMapper.to_block_entity(api_data)

        assert block.id == "block_123"
        assert block.type == "paragraph"
        assert "rich_text" in block.content
        assert block.has_children is False
        assert isinstance(block.created_time, datetime)

    def test_from_block_draft(self):
        """Test converting NotionBlockDraft to API format."""
        draft = NotionBlockDraft(
            type="heading_1",
            content={
                "rich_text": [{"type": "text", "text": {"content": "Title"}}],
                "color": "blue"
            }
        )

        api_data = NotionMapper.from_block_draft(draft)

        assert api_data["type"] == "heading_1"
        assert "heading_1" in api_data
        assert api_data["heading_1"]["color"] == "blue"

    def test_extract_plain_text_from_rich_text(self):
        """Test extracting plain text from rich text array."""
        rich_text = [
            {"plain_text": "Hello "},
            {"plain_text": "World"},
            {"plain_text": "!"}
        ]

        result = NotionMapper.extract_plain_text_from_rich_text(rich_text)

        assert result == "Hello World!"

    def test_extract_plain_text_empty_array(self):
        """Test extracting plain text from empty array."""
        result = NotionMapper.extract_plain_text_from_rich_text([])
        assert result == ""

    def test_create_rich_text(self):
        """Test creating rich text array from plain text."""
        result = NotionMapper.create_rich_text("Hello World")

        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert result[0]["text"]["content"] == "Hello World"

    def test_extract_property_value_title(self):
        """Test extracting title property value."""
        property_data = {
            "type": "title",
            "title": [{"plain_text": "Page Title"}]
        }

        result = NotionMapper.extract_property_value(property_data)
        assert result == "Page Title"

    def test_extract_property_value_select(self):
        """Test extracting select property value."""
        property_data = {
            "type": "select",
            "select": {"name": "Active"}
        }

        result = NotionMapper.extract_property_value(property_data)
        assert result == "Active"

    def test_extract_property_value_multi_select(self):
        """Test extracting multi-select property value."""
        property_data = {
            "type": "multi_select",
            "multi_select": [
                {"name": "Tag1"},
                {"name": "Tag2"}
            ]
        }

        result = NotionMapper.extract_property_value(property_data)
        assert result == ["Tag1", "Tag2"]

    def test_extract_property_value_number(self):
        """Test extracting number property value."""
        property_data = {
            "type": "number",
            "number": 42
        }

        result = NotionMapper.extract_property_value(property_data)
        assert result == 42

    def test_extract_property_value_checkbox(self):
        """Test extracting checkbox property value."""
        property_data = {
            "type": "checkbox",
            "checkbox": True
        }

        result = NotionMapper.extract_property_value(property_data)
        assert result is True

    def test_extract_property_value_date(self):
        """Test extracting date property value."""
        property_data = {
            "type": "date",
            "date": {"start": "2025-01-15"}
        }

        result = NotionMapper.extract_property_value(property_data)
        assert result == "2025-01-15"

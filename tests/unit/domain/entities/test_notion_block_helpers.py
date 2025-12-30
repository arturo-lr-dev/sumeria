"""
Unit tests for Notion block helpers.
"""
import pytest
from app.domain.entities.notion_block_helpers import (
    heading,
    paragraph,
    paragraph_with_formatting,
    bulleted_list_item,
    numbered_list_item,
    todo,
    toggle,
    divider,
    callout,
    quote,
    code,
    table_of_contents,
    bookmark,
    image
)


class TestBlockHelpers:
    """Test block helper functions."""

    def test_heading_level_1(self):
        """Test creating heading_1."""
        block = heading("Test Heading", level=1)

        assert block["type"] == "heading_1"
        assert "heading_1" in block
        assert len(block["heading_1"]["rich_text"]) == 1
        assert block["heading_1"]["rich_text"][0]["text"]["content"] == "Test Heading"

    def test_heading_level_2(self):
        """Test creating heading_2."""
        block = heading("Test Heading", level=2)

        assert block["type"] == "heading_2"
        assert "heading_2" in block

    def test_heading_level_3(self):
        """Test creating heading_3."""
        block = heading("Test Heading", level=3)

        assert block["type"] == "heading_3"
        assert "heading_3" in block

    def test_heading_with_bold(self):
        """Test creating heading with bold."""
        block = heading("Bold Heading", level=1, bold=True)

        rich_text = block["heading_1"]["rich_text"][0]
        assert rich_text["annotations"]["bold"] is True

    def test_heading_invalid_level(self):
        """Test heading with invalid level."""
        with pytest.raises(ValueError):
            heading("Test", level=4)

    def test_paragraph(self):
        """Test creating paragraph."""
        block = paragraph("Test paragraph")

        assert block["type"] == "paragraph"
        assert "paragraph" in block
        assert len(block["paragraph"]["rich_text"]) == 1
        assert block["paragraph"]["rich_text"][0]["text"]["content"] == "Test paragraph"
        assert block["paragraph"]["color"] == "default"

    def test_paragraph_with_formatting(self):
        """Test paragraph with bold and italic."""
        block = paragraph("Test", bold=True, italic=True, color="blue")

        rich_text = block["paragraph"]["rich_text"][0]
        assert rich_text["annotations"]["bold"] is True
        assert rich_text["annotations"]["italic"] is True
        assert block["paragraph"]["color"] == "blue"

    def test_paragraph_with_multiple_parts(self):
        """Test paragraph with multiple formatted parts."""
        block = paragraph_with_formatting([
            {"text": "Normal "},
            {"text": "bold", "bold": True},
            {"text": " and "},
            {"text": "italic", "italic": True}
        ])

        assert block["type"] == "paragraph"
        assert len(block["paragraph"]["rich_text"]) == 4

        # Check first part (normal)
        assert block["paragraph"]["rich_text"][0]["text"]["content"] == "Normal "
        assert "annotations" not in block["paragraph"]["rich_text"][0]

        # Check second part (bold)
        assert block["paragraph"]["rich_text"][1]["text"]["content"] == "bold"
        assert block["paragraph"]["rich_text"][1]["annotations"]["bold"] is True

        # Check fourth part (italic)
        assert block["paragraph"]["rich_text"][3]["text"]["content"] == "italic"
        assert block["paragraph"]["rich_text"][3]["annotations"]["italic"] is True

    def test_bulleted_list_item(self):
        """Test creating bulleted list item."""
        block = bulleted_list_item("List item")

        assert block["type"] == "bulleted_list_item"
        assert "bulleted_list_item" in block
        assert block["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "List item"

    def test_numbered_list_item(self):
        """Test creating numbered list item."""
        block = numbered_list_item("Numbered item")

        assert block["type"] == "numbered_list_item"
        assert "numbered_list_item" in block
        assert block["numbered_list_item"]["rich_text"][0]["text"]["content"] == "Numbered item"

    def test_todo_unchecked(self):
        """Test creating unchecked to-do."""
        block = todo("Task", checked=False)

        assert block["type"] == "to_do"
        assert "to_do" in block
        assert block["to_do"]["rich_text"][0]["text"]["content"] == "Task"
        assert block["to_do"]["checked"] is False

    def test_todo_checked(self):
        """Test creating checked to-do."""
        block = todo("Completed task", checked=True)

        assert block["to_do"]["checked"] is True

    def test_toggle_without_children(self):
        """Test creating toggle without children."""
        block = toggle("Toggle text")

        assert block["type"] == "toggle"
        assert "toggle" in block
        assert "children" not in block

    def test_toggle_with_children(self):
        """Test creating toggle with children."""
        children = [paragraph("Child paragraph")]
        block = toggle("Toggle text", children=children)

        assert "children" in block
        assert len(block["children"]) == 1

    def test_divider(self):
        """Test creating divider."""
        block = divider()

        assert block["type"] == "divider"
        assert "divider" in block
        assert block["divider"] == {}

    def test_callout(self):
        """Test creating callout."""
        block = callout("Important note", icon="⚠️", color="yellow_background")

        assert block["type"] == "callout"
        assert "callout" in block
        assert block["callout"]["rich_text"][0]["text"]["content"] == "Important note"
        assert block["callout"]["icon"]["emoji"] == "⚠️"
        assert block["callout"]["color"] == "yellow_background"

    def test_quote(self):
        """Test creating quote."""
        block = quote("Famous quote")

        assert block["type"] == "quote"
        assert "quote" in block
        assert block["quote"]["rich_text"][0]["text"]["content"] == "Famous quote"

    def test_code(self):
        """Test creating code block."""
        code_content = "print('Hello, World!')"
        block = code(code_content, language="python")

        assert block["type"] == "code"
        assert "code" in block
        assert block["code"]["rich_text"][0]["text"]["content"] == code_content
        assert block["code"]["language"] == "python"

    def test_table_of_contents(self):
        """Test creating table of contents."""
        block = table_of_contents()

        assert block["type"] == "table_of_contents"
        assert "table_of_contents" in block
        assert block["table_of_contents"]["color"] == "default"

    def test_bookmark_without_caption(self):
        """Test creating bookmark without caption."""
        block = bookmark("https://example.com")

        assert block["type"] == "bookmark"
        assert "bookmark" in block
        assert block["bookmark"]["url"] == "https://example.com"
        assert "caption" not in block["bookmark"]

    def test_bookmark_with_caption(self):
        """Test creating bookmark with caption."""
        block = bookmark("https://example.com", caption="Example site")

        assert "caption" in block["bookmark"]
        assert block["bookmark"]["caption"][0]["text"]["content"] == "Example site"

    def test_image_without_caption(self):
        """Test creating image without caption."""
        block = image("https://example.com/image.png")

        assert block["type"] == "image"
        assert "image" in block
        assert block["image"]["external"]["url"] == "https://example.com/image.png"
        assert "caption" not in block["image"]

    def test_image_with_caption(self):
        """Test creating image with caption."""
        block = image("https://example.com/image.png", caption="Beautiful image")

        assert "caption" in block["image"]
        assert block["image"]["caption"][0]["text"]["content"] == "Beautiful image"

    def test_block_structure_consistency(self):
        """Test that all blocks follow the same structure pattern."""
        # All blocks should have "type" and a key matching the type
        blocks_to_test = [
            (heading("Test", 1), "heading_1"),
            (paragraph("Test"), "paragraph"),
            (bulleted_list_item("Test"), "bulleted_list_item"),
            (numbered_list_item("Test"), "numbered_list_item"),
            (todo("Test"), "to_do"),
            (divider(), "divider"),
            (callout("Test"), "callout"),
            (quote("Test"), "quote"),
            (code("Test"), "code"),
        ]

        for block, expected_type in blocks_to_test:
            assert "type" in block, f"Block {expected_type} missing 'type' key"
            assert block["type"] == expected_type, f"Block type mismatch for {expected_type}"
            assert expected_type in block, f"Block {expected_type} missing content key"

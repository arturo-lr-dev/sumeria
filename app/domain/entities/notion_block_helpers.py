"""
Helper functions for building Notion blocks easily.
Provides simple functions to create common block types.
"""
from typing import Optional


def heading(text: str, level: int = 1, bold: bool = False) -> dict:
    """
    Create a heading block.

    Args:
        text: Heading text
        level: Heading level (1, 2, or 3)
        bold: Whether to make the text bold

    Returns:
        Notion API block format
    """
    if level not in [1, 2, 3]:
        raise ValueError("Heading level must be 1, 2, or 3")

    heading_type = f"heading_{level}"
    rich_text = {
        "type": "text",
        "text": {"content": text}
    }

    if bold:
        rich_text["annotations"] = {"bold": True}

    return {
        "type": heading_type,
        heading_type: {
            "rich_text": [rich_text]
        }
    }


def paragraph(text: str, bold: bool = False, italic: bool = False, color: str = "default") -> dict:
    """
    Create a paragraph block.

    Args:
        text: Paragraph text
        bold: Whether to make the text bold
        italic: Whether to make the text italic
        color: Text color (default, gray, brown, orange, yellow, green, blue, purple, pink, red)

    Returns:
        Notion API block format
    """
    rich_text = {
        "type": "text",
        "text": {"content": text}
    }

    annotations = {}
    if bold:
        annotations["bold"] = True
    if italic:
        annotations["italic"] = True

    if annotations:
        rich_text["annotations"] = annotations

    return {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [rich_text],
            "color": color
        }
    }


def paragraph_with_formatting(parts: list[dict]) -> dict:
    """
    Create a paragraph with multiple formatted parts.

    Args:
        parts: List of text parts with formatting. Each part is a dict with:
            - text (required): The text content
            - bold (optional): Whether to make bold
            - italic (optional): Whether to make italic
            - code (optional): Whether to make code
            - color (optional): Text color

    Example:
        paragraph_with_formatting([
            {"text": "Normal text "},
            {"text": "bold text", "bold": True},
            {"text": " and ", "italic": True},
            {"text": "code", "code": True}
        ])

    Returns:
        Notion API block format
    """
    rich_text = []

    for part in parts:
        text = part.get("text", "")
        annotations = {}

        if part.get("bold"):
            annotations["bold"] = True
        if part.get("italic"):
            annotations["italic"] = True
        if part.get("code"):
            annotations["code"] = True

        rt_item = {
            "type": "text",
            "text": {"content": text}
        }

        if annotations:
            rt_item["annotations"] = annotations

        rich_text.append(rt_item)

    color = parts[0].get("color", "default") if parts else "default"

    return {
        "type": "paragraph",
        "paragraph": {
            "rich_text": rich_text,
            "color": color
        }
    }


def bulleted_list_item(text: str) -> dict:
    """
    Create a bulleted list item.

    Args:
        text: List item text

    Returns:
        Notion API block format
    """
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }


def numbered_list_item(text: str) -> dict:
    """
    Create a numbered list item.

    Args:
        text: List item text

    Returns:
        Notion API block format
    """
    return {
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }


def todo(text: str, checked: bool = False) -> dict:
    """
    Create a to-do block.

    Args:
        text: To-do text
        checked: Whether the to-do is checked

    Returns:
        Notion API block format
    """
    return {
        "type": "to_do",
        "to_do": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ],
            "checked": checked
        }
    }


def toggle(text: str, children: Optional[list] = None) -> dict:
    """
    Create a toggle block (collapsible section).

    Args:
        text: Toggle text
        children: Optional nested blocks

    Returns:
        Notion API block format
    """
    block = {
        "type": "toggle",
        "toggle": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }

    if children:
        block["children"] = children

    return block


def divider() -> dict:
    """
    Create a divider block.

    Returns:
        Notion API block format
    """
    return {
        "type": "divider",
        "divider": {}
    }


def callout(text: str, icon: str = "💡", color: str = "gray_background") -> dict:
    """
    Create a callout block.

    Args:
        text: Callout text
        icon: Emoji icon
        color: Background color

    Returns:
        Notion API block format
    """
    return {
        "type": "callout",
        "callout": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ],
            "icon": {
                "type": "emoji",
                "emoji": icon
            },
            "color": color
        }
    }


def quote(text: str) -> dict:
    """
    Create a quote block.

    Args:
        text: Quote text

    Returns:
        Notion API block format
    """
    return {
        "type": "quote",
        "quote": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
    }


def code(code: str, language: str = "python") -> dict:
    """
    Create a code block.

    Args:
        code: Code content
        language: Programming language

    Returns:
        Notion API block format
    """
    return {
        "type": "code",
        "code": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": code}
                }
            ],
            "language": language
        }
    }


def table_of_contents() -> dict:
    """
    Create a table of contents block.

    Returns:
        Notion API block format
    """
    return {
        "type": "table_of_contents",
        "table_of_contents": {
            "color": "default"
        }
    }


def bookmark(url: str, caption: Optional[str] = None) -> dict:
    """
    Create a bookmark block.

    Args:
        url: URL to bookmark
        caption: Optional caption

    Returns:
        Notion API block format
    """
    block = {
        "type": "bookmark",
        "bookmark": {
            "url": url
        }
    }

    if caption:
        block["bookmark"]["caption"] = [
            {
                "type": "text",
                "text": {"content": caption}
            }
        ]

    return block


def image(url: str, caption: Optional[str] = None) -> dict:
    """
    Create an image block.

    Args:
        url: Image URL
        caption: Optional caption

    Returns:
        Notion API block format
    """
    block = {
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": url
            }
        }
    }

    if caption:
        block["image"]["caption"] = [
            {
                "type": "text",
                "text": {"content": caption}
            }
        ]

    return block

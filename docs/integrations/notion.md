# Notion Integration

Complete integration with Notion API for managing pages, databases, and content through the Sumeria MCP Server.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Authentication](#authentication)
- [MCP Tools](#mcp-tools)
- [Usage Examples](#usage-examples)
- [Property Types](#property-types)
- [Block Types](#block-types)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Notion integration provides comprehensive access to your Notion workspace, allowing you to:

- ✅ Create and manage pages
- ✅ Search across your workspace
- ✅ Create and query database entries
- ✅ Add and read content blocks
- ✅ Update page properties
- ✅ Archive and organize pages

### Architecture

The integration follows the DDD (Domain-Driven Design) architecture:

```
Domain Layer       → NotionPage, NotionDatabase, NotionBlock entities
Infrastructure     → NotionClient (API communication) + NotionMapper (schemas)
Application        → Use Cases (CreatePage, QueryDatabase, Search, etc.)
MCP Tools         → 8 tools exposed via MCP protocol
```

## Setup

### 1. Install Dependencies

The Notion integration is already included in the project dependencies:

```bash
pip install -r requirements.txt
```

Key dependency:
- `notion-client==2.2.1` - Official Notion Python SDK

### 2. Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "Sumeria Assistant")
4. Select the workspace
5. Set capabilities:
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
6. Click "Submit"
7. Copy the "Internal Integration Token" (starts with `secret_`)

### 3. Share Pages with Integration

For each page/database you want to access:

1. Open the page in Notion
2. Click "..." (more menu) in top right
3. Scroll to "Connections"
4. Search for your integration name
5. Click to connect

**Important**: The integration can only access pages/databases that have been explicitly shared with it.

### 4. Configure Environment Variables

Add your Notion API key to `.env`:

```bash
# Notion API
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_API_VERSION=2022-06-28
```

## Authentication

Notion uses **Integration Tokens** for authentication (not OAuth).

- API keys are scoped to your workspace
- Each integration has specific permissions
- Keys must be shared with specific pages/databases

## MCP Tools

### 1. `notion_create_page`

Create a new page in Notion.

**Parameters:**
- `title` (str, required): Page title
- `parent_id` (str, required): Parent page or database ID
- `parent_type` (str): Type of parent - `page_id`, `database_id`, or `workspace` (default: `page_id`)
- `properties` (dict): Page properties (required for database pages)
- `children` (list): Initial content blocks
- `icon` (dict): Page icon configuration
- `cover` (dict): Page cover configuration

**Returns:**
- `success` (bool): Operation status
- `page_id` (str): Created page ID
- `error` (str): Error message if failed

### 2. `notion_get_page`

Get detailed information about a page.

**Parameters:**
- `page_id` (str, required): Page ID

**Returns:**
- `success` (bool): Operation status
- `page` (PageSummary): Page details
- `properties` (dict): Page properties
- `error` (str): Error message if failed

### 3. `notion_update_page`

Update a page's properties or metadata.

**Parameters:**
- `page_id` (str, required): Page ID
- `properties` (dict): Properties to update
- `archived` (bool): Archive status
- `icon` (dict): Page icon
- `cover` (dict): Page cover

**Returns:**
- `success` (bool): Operation status
- `page` (PageSummary): Updated page details
- `error` (str): Error message if failed

### 4. `notion_search`

Search for pages in your workspace.

**Parameters:**
- `query` (str): Search query text
- `filter_type` (str): Filter by type - `page` or `database`
- `sort_direction` (str): `ascending` or `descending` (default: `descending`)
- `sort_timestamp` (str): `last_edited_time` or `created_time` (default: `last_edited_time`)
- `max_results` (int): Maximum results (default: 100)

**Returns:**
- `success` (bool): Operation status
- `count` (int): Number of results
- `pages` (list[PageSummary]): Matching pages
- `error` (str): Error message if failed

### 5. `notion_create_database_entry`

Create a new entry in a database.

**Parameters:**
- `database_id` (str, required): Database ID
- `properties` (dict, required): Entry properties (must match database schema)
- `icon` (dict): Entry icon
- `cover` (dict): Entry cover
- `children` (list): Initial content blocks

**Returns:**
- `success` (bool): Operation status
- `entry_id` (str): Created entry ID
- `error` (str): Error message if failed

### 6. `notion_query_database`

Query a database with filters and sorting.

**Parameters:**
- `database_id` (str, required): Database ID
- `filter` (dict): Filter criteria (Notion filter format)
- `sorts` (list): Sort criteria
- `start_cursor` (str): Pagination cursor
- `page_size` (int): Results per page (default: 100)

**Returns:**
- `success` (bool): Operation status
- `count` (int): Number of results
- `entries` (list[DatabaseEntrySummary]): Matching entries
- `error` (str): Error message if failed

### 7. `notion_append_content`

Append content blocks to a page.

**Parameters:**
- `page_id` (str, required): Page ID
- `blocks` (list[dict], required): List of block objects

**Returns:**
- `success` (bool): Operation status
- `count` (int): Number of blocks created
- `block_ids` (list[str]): Created block IDs
- `error` (str): Error message if failed

### 8. `notion_get_page_content`

Get content blocks from a page.

**Parameters:**
- `page_id` (str, required): Page ID
- `page_size` (int): Number of blocks to retrieve (default: 100)

**Returns:**
- `success` (bool): Operation status
- `count` (int): Number of blocks
- `blocks` (list[BlockSummary]): Page blocks
- `error` (str): Error message if failed

## Usage Examples

### Creating a Simple Page

```python
result = await notion_create_page(
    title="Meeting Notes - Q1 Planning",
    parent_id="parent_page_id",
    parent_type="page_id"
)

if result["success"]:
    print(f"Page created: {result['page_id']}")
```

### Creating a Page with Content

```python
result = await notion_create_page(
    title="Project Plan",
    parent_id="parent_page_id",
    children=[
        {
            "type": "heading_1",
            "content": {
                "rich_text": [{"type": "text", "text": {"content": "Overview"}}]
            }
        },
        {
            "type": "paragraph",
            "content": {
                "rich_text": [{"type": "text", "text": {"content": "This is the project plan."}}]
            }
        },
        {
            "type": "to_do",
            "content": {
                "rich_text": [{"type": "text", "text": {"content": "Define requirements"}}],
                "checked": False
            }
        }
    ]
)
```

### Creating a Database Entry

```python
# For a Tasks database with Name, Status, Priority, Due Date
result = await notion_create_database_entry(
    database_id="db_id_here",
    properties={
        "Name": {
            "title": [{"text": {"content": "Complete Notion integration"}}]
        },
        "Status": {
            "select": {"name": "In Progress"}
        },
        "Priority": {
            "number": 5
        },
        "Due Date": {
            "date": {"start": "2025-01-15"}
        }
    }
)
```

### Querying a Database

```python
# Find all tasks that are "In Progress" and high priority
result = await notion_query_database(
    database_id="db_id_here",
    filter={
        "and": [
            {
                "property": "Status",
                "select": {"equals": "In Progress"}
            },
            {
                "property": "Priority",
                "number": {"greater_than_or_equal_to": 4}
            }
        ]
    },
    sorts=[
        {"property": "Due Date", "direction": "ascending"}
    ]
)

print(f"Found {result['count']} tasks")
for entry in result["entries"]:
    print(f"- {entry['id']}: {entry['properties']}")
```

### Searching Pages

```python
# Search for pages containing "integration"
result = await notion_search(
    query="integration",
    filter_type="page",
    sort_direction="descending",
    sort_timestamp="last_edited_time"
)

for page in result["pages"]:
    print(f"- {page['title']} (ID: {page['id']})")
```

### Adding Content to a Page

```python
result = await notion_append_content(
    page_id="page_id_here",
    blocks=[
        {
            "type": "heading_2",
            "content": {
                "rich_text": [{"type": "text", "text": {"content": "Updates"}}]
            }
        },
        {
            "type": "bulleted_list_item",
            "content": {
                "rich_text": [{"type": "text", "text": {"content": "Completed phase 1"}}]
            }
        },
        {
            "type": "bulleted_list_item",
            "content": {
                "rich_text": [{"type": "text", "text": {"content": "Started phase 2"}}]
            }
        }
    ]
)
```

## Property Types

Notion supports various property types for databases:

### Title
```python
"Name": {
    "title": [{"text": {"content": "Entry name"}}]
}
```

### Rich Text
```python
"Description": {
    "rich_text": [{"text": {"content": "Description text"}}]
}
```

### Number
```python
"Priority": {
    "number": 5
}
```

### Select (Single choice)
```python
"Status": {
    "select": {"name": "In Progress"}
}
```

### Multi-select (Multiple choices)
```python
"Tags": {
    "multi_select": [
        {"name": "Important"},
        {"name": "Urgent"}
    ]
}
```

### Date
```python
"Due Date": {
    "date": {"start": "2025-01-15"}
}

# Date range
"Event Date": {
    "date": {
        "start": "2025-01-15",
        "end": "2025-01-20"
    }
}
```

### Checkbox
```python
"Completed": {
    "checkbox": True
}
```

### URL
```python
"Website": {
    "url": "https://example.com"
}
```

### Email
```python
"Contact": {
    "email": "user@example.com"
}
```

### Phone Number
```python
"Phone": {
    "phone_number": "+1-555-0100"
}
```

## Block Types

### Paragraph
```python
{
    "type": "paragraph",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Text content"}}],
        "color": "default"
    }
}
```

### Headings
```python
# Heading 1
{
    "type": "heading_1",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Main Title"}}]
    }
}

# Heading 2
{
    "type": "heading_2",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Section"}}]
    }
}

# Heading 3
{
    "type": "heading_3",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Subsection"}}]
    }
}
```

### Lists
```python
# Bulleted list
{
    "type": "bulleted_list_item",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "List item"}}]
    }
}

# Numbered list
{
    "type": "numbered_list_item",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "List item"}}]
    }
}
```

### To-Do
```python
{
    "type": "to_do",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Task description"}}],
        "checked": False
    }
}
```

### Toggle
```python
{
    "type": "toggle",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Click to expand"}}]
    }
}
```

### Quote
```python
{
    "type": "quote",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Quoted text"}}]
    }
}
```

### Callout
```python
{
    "type": "callout",
    "content": {
        "rich_text": [{"type": "text", "text": {"content": "Important note"}}],
        "icon": {"emoji": "💡"}
    }
}
```

## Best Practices

### 1. Page IDs and Database IDs

- Get page/database IDs from the Notion URL
- Format: `https://notion.so/Page-Title-{page_id}`
- IDs are 32 characters with hyphens (format: `8-4-4-4-12`)

### 2. Property Naming

- Property names are case-sensitive
- Use the exact property names from your database
- Check property types match your database schema

### 3. Rate Limiting

- Notion has rate limits: ~3 requests/second
- The client uses automatic retry with exponential backoff
- For bulk operations, consider adding delays

### 4. Error Handling

- Always check the `success` field in responses
- Log `error` messages for debugging
- Validate page/database IDs before operations

### 5. Content Structure

- Keep content blocks focused and modular
- Use appropriate block types for content
- Nested blocks can be added using `children` property

### 6. Search Optimization

- Use specific queries for better results
- Filter by type (`page` or `database`) when possible
- Limit results to needed amount

## Troubleshooting

### "Notion API key is required"

**Problem**: Missing API key configuration.

**Solution**: Set `NOTION_API_KEY` in your `.env` file.

### "object not found"

**Problem**: Page/database doesn't exist or integration doesn't have access.

**Solution**:
1. Verify the page/database ID is correct
2. Share the page with your integration
3. Check the integration has required permissions

### "validation_error" on properties

**Problem**: Properties don't match database schema.

**Solution**:
1. Check property names (case-sensitive)
2. Verify property types match schema
3. Ensure required properties are included

### "rate_limited"

**Problem**: Too many requests.

**Solution**:
- Wait a few seconds between requests
- The client automatically retries with backoff
- Consider implementing request queuing for bulk operations

### Empty search results

**Problem**: Search returns no results.

**Solution**:
1. Verify pages are shared with integration
2. Check search query syntax
3. Try searching without filters first

## API Reference

For detailed Notion API documentation:
- [Notion API Reference](https://developers.notion.com/reference)
- [Property Values](https://developers.notion.com/reference/property-value-object)
- [Block Types](https://developers.notion.com/reference/block)
- [Filter and Sort](https://developers.notion.com/reference/post-database-query-filter)

## Support

For issues or questions:
1. Check this documentation
2. Review Notion API docs
3. Check application logs for errors
4. Open an issue on the project repository

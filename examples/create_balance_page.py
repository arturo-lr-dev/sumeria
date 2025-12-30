#!/usr/bin/env python3
"""
Example: Create a balance page in Notion with correct structure.

This example shows how to create a page like the one mentioned in the error,
but using the correct structure.

Usage:
    # From project root:
    PYTHONPATH=. python examples/create_balance_page.py

    # Or use the helper script:
    ./examples/run_example.sh create_balance_page.py
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from app.application.use_cases.notion.create_page import (
    CreatePageUseCase,
    CreatePageRequest
)
from app.domain.entities.notion_block_helpers import (
    heading,
    paragraph,
    paragraph_with_formatting,
    divider
)


async def create_balance_page(parent_id: str):
    """
    Create a balance page with proper formatting.

    Args:
        parent_id: The parent page ID where this page will be created
    """

    # Build the content using helpers
    children = [
        heading("Balance General", level=1),

        paragraph("Fecha: 29 de diciembre de 2025"),

        heading("Cuentas de Tesorería", level=2),

        paragraph("Cuenta Principal (ES5368880001686965441657)"),

        paragraph_with_formatting([
            {"text": "Balance: "},
            {"text": "50.964,18 €", "bold": True}
        ]),

        heading("Resumen", level=2),

        paragraph_with_formatting([
            {"text": "Balance Total: "},
            {"text": "50.964,18 €", "bold": True}
        ])
    ]

    # Create the page request
    request = CreatePageRequest(
        title="Balance a Día de Hoy",
        parent_id=parent_id,
        parent_type="page_id",
        children=children
    )

    # Execute the use case
    use_case = CreatePageUseCase()
    response = await use_case.execute(request)

    if response.success:
        print(f"✅ Página creada exitosamente!")
        print(f"   Page ID: {response.page_id}")
    else:
        print(f"❌ Error al crear la página:")
        print(f"   {response.error}")

    return response


async def main():
    """Main function."""
    # REPLACE THIS with your actual parent page ID
    parent_id = "2d865487be858019942cece64d4fd5a0"

    print("Creando página de balance en Notion...")
    print(f"Parent ID: {parent_id}")
    print()

    await create_balance_page(parent_id)


if __name__ == "__main__":
    asyncio.run(main())

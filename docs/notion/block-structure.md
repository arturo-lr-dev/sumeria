# Notion Block Structure Guide

## Problema Común: Estructura Incorrecta de Bloques

### ❌ Estructura INCORRECTA

```python
# NO HACER ESTO - Estructura incorrecta
children = [
    {
        "type": "heading_1",
        "content": {  # ❌ Incorrecto: usa "content"
            "rich_text": [
                {
                    "text": {"content": "Balance General"},
                    "type": "text"
                }
            ]
        }
    }
]
```

### ✅ Estructura CORRECTA

```python
# HACER ESTO - Estructura correcta para la API de Notion
children = [
    {
        "type": "heading_1",
        "heading_1": {  # ✅ Correcto: usa el nombre del tipo de bloque
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Balance General"}
                }
            ]
        }
    },
    {
        "type": "paragraph",
        "paragraph": {  # ✅ La clave debe coincidir con el tipo
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Fecha: 29 de diciembre de 2025"}
                }
            ]
        }
    }
]
```

## Regla Fundamental

**La clave del contenido DEBE ser el mismo valor que el tipo del bloque:**

```python
{
    "type": "TYPE_NAME",  # El tipo de bloque
    "TYPE_NAME": {        # La misma palabra como clave
        # ... contenido del bloque
    }
}
```

## Ejemplos por Tipo de Bloque

### Heading 1, 2, 3

```python
{
    "type": "heading_1",  # o heading_2, heading_3
    "heading_1": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Título Principal"}
            }
        ]
    }
}
```

### Paragraph

```python
{
    "type": "paragraph",
    "paragraph": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Este es un párrafo normal."}
            }
        ]
    }
}
```

### Paragraph con Texto en Negrita

```python
{
    "type": "paragraph",
    "paragraph": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Texto normal "}
            },
            {
                "type": "text",
                "text": {"content": "texto en negrita"},
                "annotations": {"bold": True}
            }
        ]
    }
}
```

### Bulleted List Item

```python
{
    "type": "bulleted_list_item",
    "bulleted_list_item": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Elemento de lista"}
            }
        ]
    }
}
```

### Numbered List Item

```python
{
    "type": "numbered_list_item",
    "numbered_list_item": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Elemento numerado"}
            }
        ]
    }
}
```

### To-Do

```python
{
    "type": "to_do",
    "to_do": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Tarea por hacer"}
            }
        ],
        "checked": False
    }
}
```

### Divider (separador)

```python
{
    "type": "divider",
    "divider": {}
}
```

## Usar NotionBlockDraft (Recomendado)

En lugar de construir manualmente los diccionarios, puedes usar las clases helper:

```python
from app.domain.entities.notion_block import (
    NotionBlockDraft,
    HeadingBlock,
    ParagraphBlock,
    BulletedListItemBlock
)

# Opción 1: Usar helpers
blocks = [
    HeadingBlock(text="Balance General", level=1).to_draft(),
    ParagraphBlock(text="Fecha: 29 de diciembre de 2025").to_draft(),
]

# Opción 2: Construir NotionBlockDraft directamente
blocks = [
    NotionBlockDraft(
        type="heading_1",
        content={
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Balance General"}
                }
            ]
        }
    ),
    NotionBlockDraft(
        type="paragraph",
        content={
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Fecha: 29 de diciembre de 2025"}
                }
            ]
        }
    )
]

# Convertir a formato de API
from app.infrastructure.connectors.notion.schemas import NotionMapper
children = [NotionMapper.from_block_draft(block) for block in blocks]
```

## Ejemplo Completo: Crear Página con Contenido

```python
from app.application.use_cases.notion.create_page import (
    CreatePageUseCase,
    CreatePageRequest
)
from app.domain.entities.notion_block import HeadingBlock, ParagraphBlock
from app.infrastructure.connectors.notion.schemas import NotionMapper

# Construir bloques usando helpers
blocks = [
    HeadingBlock(text="Balance General", level=1).to_draft(),
    ParagraphBlock(text="Fecha: 29 de diciembre de 2025").to_draft(),
    HeadingBlock(text="Cuentas de Tesorería", level=2).to_draft(),
]

# Convertir a formato de API
children = [NotionMapper.from_block_draft(block) for block in blocks]

# Crear request
request = CreatePageRequest(
    title="Balance a Día de Hoy",
    parent_id="2d865487be858019942cece64d4fd5a0",
    parent_type="page_id",
    children=children
)

# Ejecutar
use_case = CreatePageUseCase()
response = await use_case.execute(request)

if response.success:
    print(f"Página creada: {response.page_id}")
else:
    print(f"Error: {response.error}")
```

## Errores Comunes

### Error 1: RetryError

Si recibes un `RetryError`, generalmente significa que:
1. La estructura del bloque es incorrecta
2. El API key no es válido
3. No tienes permisos sobre el parent_id especificado
4. El parent_id no existe

### Error 2: "The body failed validation"

Significa que la estructura de los bloques no cumple con el schema de Notion. Verifica:
- Que uses `"type_name": {...}` en lugar de `"content": {...}`
- Que `rich_text` sea un array
- Que cada elemento de `rich_text` tenga `type` y `text`

### Error 3: "Could not find page with ID"

El `parent_id` no existe o no tienes acceso a él. Verifica:
- Que el ID sea correcto
- Que la integración tenga acceso a esa página
- Que uses el formato correcto (sin guiones si el ID viene de la URL)

## Debugging

Para ver exactamente qué se está enviando a la API:

```python
import json
from app.infrastructure.connectors.notion.schemas import NotionMapper
from app.domain.entities.notion_page import NotionPageDraft

draft = NotionPageDraft(
    title="Test",
    parent_id="abc123",
    parent_type="page_id",
    children=children  # tus bloques
)

# Ver qué se enviará a la API
api_data = NotionMapper.from_page_draft(draft)
print(json.dumps(api_data, indent=2))
```

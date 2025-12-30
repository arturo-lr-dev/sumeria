# Notion Integration - Guía Completa

## 🎯 Resumen

Esta integración permite crear páginas, gestionar bases de datos y manipular contenido en Notion usando Python.

## 📚 Documentación

- **[Block Structure Guide](block-structure.md)** - Estructura correcta de bloques (¡IMPORTANTE!)
- **[Examples](examples.md)** - Ejemplos de uso completos

## ⚠️ Problema Común: RetryError

Si estás viendo errores como:

```json
{
  "success": false,
  "page_id": null,
  "error": "RetryError[<Future at 0x12170c8e0 state=finished raised Exception>]"
}
```

**Causa más común:** Estructura incorrecta de los bloques.

### ❌ Estructura INCORRECTA

```python
# NO HACER ESTO
children = [
    {
        "type": "heading_1",
        "content": {  # ❌ Error: usa "content"
            "rich_text": [...]
        }
    }
]
```

### ✅ Estructura CORRECTA

```python
# HACER ESTO - Opción 1: Usar helpers (recomendado)
from app.domain.entities.notion_block_helpers import heading, paragraph

children = [
    heading("Mi Título", level=1),
    paragraph("Mi contenido")
]

# HACER ESTO - Opción 2: Estructura manual correcta
children = [
    {
        "type": "heading_1",
        "heading_1": {  # ✅ La clave debe ser el tipo de bloque
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Mi Título"}
                }
            ]
        }
    }
]
```

## 🚀 Quick Start

### Crear una Página Simple

```python
from app.application.use_cases.notion.create_page import (
    CreatePageUseCase,
    CreatePageRequest
)
from app.domain.entities.notion_block_helpers import (
    heading,
    paragraph,
    divider
)

# Construir contenido
children = [
    heading("Mi Primera Página", level=1),
    paragraph("Este es un párrafo."),
    divider(),
    paragraph("Más contenido aquí.")
]

# Crear página
request = CreatePageRequest(
    title="Mi Primera Página",
    parent_id="tu_parent_id",  # ID de la página padre
    parent_type="page_id",
    children=children
)

use_case = CreatePageUseCase()
response = await use_case.execute(request)

if response.success:
    print(f"✅ Página creada: {response.page_id}")
else:
    print(f"❌ Error: {response.error}")
```

### Ejecutar el Ejemplo de Balance

```bash
# Edita el parent_id en el archivo
python examples/create_balance_page.py
```

## 📦 Helpers Disponibles

La forma más fácil de crear bloques es usar los helpers:

```python
from app.domain.entities.notion_block_helpers import (
    heading,          # Encabezados (h1, h2, h3)
    paragraph,        # Párrafos
    paragraph_with_formatting,  # Párrafos con formato
    bulleted_list_item,  # Lista con viñetas
    numbered_list_item,  # Lista numerada
    todo,            # Checkbox
    toggle,          # Sección colapsable
    divider,         # Línea divisoria
    callout,         # Bloque destacado
    quote,           # Cita
    code,            # Bloque de código
    table_of_contents,  # Tabla de contenidos
    bookmark,        # Enlace marcado
    image,           # Imagen
)
```

## 🔧 Operaciones Disponibles

### Páginas

```python
# Crear página
from app.application.use_cases.notion.create_page import CreatePageUseCase

# Obtener página
from app.application.use_cases.notion.get_page import GetPageUseCase

# Actualizar página
from app.application.use_cases.notion.update_page import UpdatePageUseCase

# Buscar páginas
from app.application.use_cases.notion.search_pages import SearchPagesUseCase

# Obtener contenido de página
from app.application.use_cases.notion.get_page_content import GetPageContentUseCase

# Añadir bloques a página
from app.application.use_cases.notion.append_blocks import AppendBlocksUseCase
```

### Bases de Datos

```python
# Crear entrada en base de datos
from app.application.use_cases.notion.create_database_entry import (
    CreateDatabaseEntryUseCase
)

# Consultar base de datos
from app.application.use_cases.notion.query_database import QueryDatabaseUseCase
```

## 🐛 Debugging

### Ver qué se envía a la API

```python
from app.infrastructure.connectors.notion.schemas import NotionMapper
from app.domain.entities.notion_page import NotionPageDraft
import json

draft = NotionPageDraft(
    title="Test",
    parent_id="abc123",
    parent_type="page_id",
    children=children
)

# Ver estructura que se enviará
api_data = NotionMapper.from_page_draft(draft)
print(json.dumps(api_data, indent=2))
```

### Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `RetryError` | Estructura de bloques incorrecta | Ver [Block Structure Guide](block-structure.md) |
| `Could not find page` | Parent ID no existe o sin acceso | Verificar ID y permisos |
| `validation failed` | Schema incorrecto | Usar helpers o verificar estructura |
| `unauthorized` | API key inválida | Verificar `NOTION_API_KEY` en `.env` |

## 📖 Más Ejemplos

Ver [examples.md](examples.md) para ejemplos completos de:

- ✅ Crear páginas con formato
- ✅ Listas de tareas
- ✅ Documentos con código
- ✅ Páginas con imágenes
- ✅ Añadir contenido a páginas existentes
- ✅ Crear entradas en bases de datos
- ✅ Buscar y consultar contenido

## 🔑 Configuración

Asegúrate de tener configurada la API key en tu `.env`:

```bash
NOTION_API_KEY="secret_tu_api_key_aqui"
```

## 🎓 Mejores Prácticas

1. **Siempre usa los helpers** - Son más fáciles y evitan errores
2. **Valida IDs** - Normaliza los IDs removiendo guiones si es necesario
3. **Maneja errores** - Siempre verifica `response.success` antes de continuar
4. **Limita bloques** - La API de Notion limita a 100 bloques por request
5. **Debuggea primero** - Usa `NotionMapper.from_page_draft()` para ver qué se envía

## 📝 Regla de Oro

**La clave del contenido del bloque DEBE coincidir con el tipo de bloque:**

```python
{
    "type": "TYPE_NAME",
    "TYPE_NAME": {  # ← Mismo valor
        # contenido aquí
    }
}
```

## 🚨 Si Nada Funciona

1. Verifica tu API key
2. Verifica que la integración tenga acceso a la página/database
3. Lee los logs completos del error
4. Revisa [Block Structure Guide](block-structure.md)
5. Ejecuta el ejemplo `examples/create_balance_page.py`

## 🤝 Soporte

Para más ayuda:
- Ver ejemplos completos en `/examples`
- Leer tests en `/tests/unit/application/use_cases/notion`
- Consultar documentación oficial de Notion API

---

**Última actualización:** 2025-12-29

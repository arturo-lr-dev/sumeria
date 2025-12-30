# Notion Integration - Ejemplos de Uso

## Usando los Block Helpers (Más Fácil)

### Ejemplo 1: Crear una Página Simple

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

# Construir el contenido
children = [
    heading("Mi Primera Página", level=1),
    paragraph("Este es un párrafo de ejemplo."),
    divider(),
    heading("Sección 2", level=2),
    paragraph("Más contenido aquí.")
]

# Crear la página
request = CreatePageRequest(
    title="Mi Primera Página",
    parent_id="tu_parent_id_aquí",
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

### Ejemplo 2: Balance con Formato

```python
from app.domain.entities.notion_block_helpers import (
    heading,
    paragraph,
    paragraph_with_formatting,
    divider
)

children = [
    heading("Balance a Día de Hoy", level=1),
    paragraph("Fecha: 29 de diciembre de 2025"),
    divider(),

    heading("Cuentas de Tesorería", level=2),
    paragraph("Cuenta Principal (ES5368880001686965441657)"),
    paragraph_with_formatting([
        {"text": "Balance: "},
        {"text": "50.964,18 €", "bold": True}
    ]),
    divider(),

    heading("Resumen", level=2),
    paragraph_with_formatting([
        {"text": "Balance Total: "},
        {"text": "50.964,18 €", "bold": True}
    ])
]

request = CreatePageRequest(
    title="Balance a Día de Hoy",
    parent_id="2d865487be858019942cece64d4fd5a0",
    parent_type="page_id",
    children=children
)

use_case = CreatePageUseCase()
response = await use_case.execute(request)
```

### Ejemplo 3: Lista de Tareas

```python
from app.domain.entities.notion_block_helpers import (
    heading,
    todo,
    bulleted_list_item
)

children = [
    heading("Tareas del Día", level=1),

    todo("Revisar emails", checked=True),
    todo("Reunión con equipo", checked=True),
    todo("Completar reporte", checked=False),
    todo("Enviar factura", checked=False),

    heading("Notas", level=2),
    bulleted_list_item("Recordar llamar a cliente"),
    bulleted_list_item("Preparar presentación"),
]

request = CreatePageRequest(
    title="Tareas del Día",
    parent_id="parent_id",
    parent_type="page_id",
    children=children
)

use_case = CreatePageUseCase()
response = await use_case.execute(request)
```

### Ejemplo 4: Documento con Código

```python
from app.domain.entities.notion_block_helpers import (
    heading,
    paragraph,
    code,
    callout
)

children = [
    heading("Guía de Instalación", level=1),

    callout("Esta guía te ayudará a instalar el proyecto.", icon="📚"),

    heading("Paso 1: Clonar el repositorio", level=2),
    code("git clone https://github.com/usuario/proyecto.git", language="bash"),

    heading("Paso 2: Instalar dependencias", level=2),
    code("pip install -r requirements.txt", language="bash"),

    heading("Paso 3: Configurar variables", level=2),
    paragraph("Crea un archivo .env con las siguientes variables:"),
    code('NOTION_API_KEY="tu_api_key"\nDATABASE_URL="tu_db_url"', language="bash"),
]

request = CreatePageRequest(
    title="Guía de Instalación",
    parent_id="parent_id",
    parent_type="page_id",
    children=children
)

use_case = CreatePageUseCase()
response = await use_case.execute(request)
```

### Ejemplo 5: Página con Imágenes y Enlaces

```python
from app.domain.entities.notion_block_helpers import (
    heading,
    paragraph,
    image,
    bookmark
)

children = [
    heading("Recursos del Proyecto", level=1),

    heading("Documentación", level=2),
    bookmark("https://docs.proyecto.com", caption="Documentación oficial"),

    heading("Capturas de Pantalla", level=2),
    image(
        "https://ejemplo.com/imagen.png",
        caption="Pantalla principal de la aplicación"
    ),

    heading("Videos", level=2),
    paragraph("Tutorial en YouTube:"),
    bookmark("https://youtube.com/watch?v=ejemplo"),
]

request = CreatePageRequest(
    title="Recursos del Proyecto",
    parent_id="parent_id",
    parent_type="page_id",
    children=children
)

use_case = CreatePageUseCase()
response = await use_case.execute(request)
```

## Añadir Contenido a una Página Existente

```python
from app.application.use_cases.notion.append_blocks import (
    AppendBlocksUseCase,
    AppendBlocksRequest
)
from app.domain.entities.notion_block_helpers import (
    heading,
    paragraph,
    bulleted_list_item
)

# Construir nuevo contenido
new_blocks = [
    heading("Nueva Sección", level=2),
    paragraph("Este contenido se añadirá al final de la página."),
    bulleted_list_item("Punto 1"),
    bulleted_list_item("Punto 2"),
]

# Añadir a la página
request = AppendBlocksRequest(
    page_id="id_de_la_pagina_existente",
    blocks=new_blocks
)

use_case = AppendBlocksUseCase()
response = await use_case.execute(request)

if response.success:
    print(f"✅ {response.count} bloques añadidos")
    print(f"IDs: {response.block_ids}")
else:
    print(f"❌ Error: {response.error}")
```

## Crear Entrada en Base de Datos

```python
from app.application.use_cases.notion.create_database_entry import (
    CreateDatabaseEntryUseCase,
    CreateDatabaseEntryRequest
)
from app.domain.entities.notion_block_helpers import paragraph

# Definir propiedades según el schema de tu database
properties = {
    "Name": {  # Título (campo title)
        "title": [
            {
                "type": "text",
                "text": {"content": "Nueva Tarea"}
            }
        ]
    },
    "Status": {  # Select
        "select": {
            "name": "En Progreso"
        }
    },
    "Priority": {  # Select
        "select": {
            "name": "Alta"
        }
    },
    "Due Date": {  # Date
        "date": {
            "start": "2025-12-31"
        }
    },
    "Tags": {  # Multi-select
        "multi_select": [
            {"name": "importante"},
            {"name": "urgente"}
        ]
    }
}

# Contenido inicial (opcional)
children = [
    paragraph("Descripción detallada de la tarea."),
    paragraph("Pasos a seguir...")
]

request = CreateDatabaseEntryRequest(
    database_id="tu_database_id",
    properties=properties,
    children=children
)

use_case = CreateDatabaseEntryUseCase()
response = await use_case.execute(request)

if response.success:
    print(f"✅ Entrada creada: {response.entry_id}")
else:
    print(f"❌ Error: {response.error}")
```

## Buscar Páginas

```python
from app.application.use_cases.notion.search_pages import (
    SearchPagesUseCase,
    SearchPagesRequest
)

request = SearchPagesRequest(
    query="balance",  # Texto a buscar
    filter_type="page",  # "page" o "database"
    sort_direction="descending",
    sort_timestamp="last_edited_time",
    max_results=10
)

use_case = SearchPagesUseCase()
response = await use_case.execute(request)

if response.success:
    print(f"✅ Encontradas {response.count} páginas:")
    for page in response.pages:
        print(f"  - {page.title} ({page.id})")
        print(f"    URL: {page.url}")
else:
    print(f"❌ Error: {response.error}")
```

## Obtener Contenido de una Página

```python
from app.application.use_cases.notion.get_page_content import (
    GetPageContentUseCase,
    GetPageContentRequest
)

request = GetPageContentRequest(
    page_id="id_de_la_pagina",
    page_size=100,
    recursive=True  # Incluir bloques anidados (tablas, toggles, etc.)
)

use_case = GetPageContentUseCase()
response = await use_case.execute(request)

if response.success:
    print(f"✅ {response.count} bloques:")
    for block in response.blocks:
        print(f"  [{block.type}] {block.text or ''}")

        # Bloques de tabla
        if block.type == "table_row" and block.cells:
            print(f"    Celdas: {block.cells}")

        # Bloques con hijos
        if block.children:
            for child in block.children:
                print(f"    → [{child.type}] {child.text or ''}")
else:
    print(f"❌ Error: {response.error}")
```

## Consultar Base de Datos con Filtros

```python
from app.application.use_cases.notion.query_database import (
    QueryDatabaseUseCase,
    QueryDatabaseRequest
)

# Filtro: solo tareas con status "En Progreso"
filter_criteria = {
    "property": "Status",
    "select": {
        "equals": "En Progreso"
    }
}

# Ordenar por fecha de creación (descendente)
sorts = [
    {
        "timestamp": "created_time",
        "direction": "descending"
    }
]

request = QueryDatabaseRequest(
    database_id="tu_database_id",
    filter=filter_criteria,
    sorts=sorts,
    page_size=50
)

use_case = QueryDatabaseUseCase()
response = await use_case.execute(request)

if response.success:
    print(f"✅ {response.count} entradas encontradas:")
    for entry in response.entries:
        # Extraer el título
        name_prop = entry.properties.get("Name", {})
        title = ""
        if name_prop.get("type") == "title":
            title_array = name_prop.get("title", [])
            if title_array:
                title = title_array[0].get("plain_text", "")

        print(f"  - {title} ({entry.id})")
else:
    print(f"❌ Error: {response.error}")
```

## Manejo de Errores

```python
from app.application.use_cases.notion.create_page import (
    CreatePageUseCase,
    CreatePageRequest
)

try:
    use_case = CreatePageUseCase()
    response = await use_case.execute(request)

    if response.success:
        print(f"✅ Éxito: Página {response.page_id}")
    else:
        # El error ya está capturado en response.error
        print(f"❌ Error al crear página: {response.error}")

        # Errores comunes:
        if "Could not find page" in response.error:
            print("→ El parent_id no existe o no tienes acceso")
        elif "validation" in response.error.lower():
            print("→ La estructura de los bloques es incorrecta")
        elif "unauthorized" in response.error.lower():
            print("→ Verifica tu API key de Notion")

except Exception as e:
    print(f"❌ Error inesperado: {e}")
```

## Tips y Mejores Prácticas

### 1. Validar IDs
```python
# Los IDs de Notion pueden tener guiones o no
# Normalízalos antes de usar:
def normalize_notion_id(notion_id: str) -> str:
    """Remove hyphens from Notion ID."""
    return notion_id.replace("-", "")
```

### 2. Límites de la API
```python
# Notion limita a 100 bloques por request
# Si tienes más, divide en chunks:

from app.domain.entities.notion_block_helpers import paragraph

all_blocks = [paragraph(f"Párrafo {i}") for i in range(250)]

# Dividir en chunks de 100
chunk_size = 100
for i in range(0, len(all_blocks), chunk_size):
    chunk = all_blocks[i:i + chunk_size]

    request = AppendBlocksRequest(
        page_id="page_id",
        blocks=chunk
    )

    response = await use_case.execute(request)
    print(f"Chunk {i//chunk_size + 1}: {response.count} bloques añadidos")
```

### 3. Rich Text con Múltiples Formatos
```python
from app.domain.entities.notion_block_helpers import paragraph_with_formatting

# Texto con negrita, cursiva y código
formatted = paragraph_with_formatting([
    {"text": "Texto normal, "},
    {"text": "texto en negrita", "bold": True},
    {"text": ", "},
    {"text": "texto en cursiva", "italic": True},
    {"text": ", y "},
    {"text": "código", "code": True},
    {"text": "."}
])
```

### 4. Crear Páginas Anidadas
```python
# Primero crea la página padre
parent_request = CreatePageRequest(
    title="Página Padre",
    parent_id="workspace_id",
    parent_type="page_id"
)

parent_response = await use_case.execute(parent_request)

if parent_response.success:
    # Luego crea la página hija
    child_request = CreatePageRequest(
        title="Página Hija",
        parent_id=parent_response.page_id,  # Usar el ID de la página padre
        parent_type="page_id"
    )

    child_response = await use_case.execute(child_request)
```

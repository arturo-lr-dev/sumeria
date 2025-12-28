# Plan de Implementación: Integración con Notion

## Resumen
Implementar integración completa con Notion API siguiendo la arquitectura DDD establecida en el proyecto, permitiendo gestionar páginas, databases, bloques y contenido de Notion a través del MCP server.

## Objetivos
- Integrar Notion API usando el SDK oficial de Python
- Seguir la arquitectura DDD establecida (Domain, Application, Infrastructure)
- Implementar operaciones CRUD para páginas y databases
- Exponer funcionalidad a través de MCP tools
- Mantener consistencia con las integraciones existentes (Gmail, Holded)

## Análisis de Requisitos

### Funcionalidades Principales de Notion
1. **Pages (Páginas)**
   - Crear páginas
   - Leer contenido de páginas
   - Actualizar páginas
   - Eliminar/archivar páginas
   - Buscar páginas

2. **Databases**
   - Crear databases
   - Consultar databases
   - Crear entradas en databases
   - Actualizar entradas
   - Filtrar y ordenar resultados

3. **Blocks (Bloques de contenido)**
   - Leer bloques
   - Crear bloques (párrafos, headings, listas, etc.)
   - Actualizar bloques
   - Eliminar bloques

4. **Search**
   - Búsqueda global en workspace
   - Filtros por tipo de objeto

## Estructura de Archivos

```
app/
├── config/
│   └── settings.py                           # ✏️ Agregar configuración de Notion
├── domain/
│   └── entities/
│       ├── notion_page.py                    # ✨ NUEVO
│       ├── notion_database.py                # ✨ NUEVO
│       └── notion_block.py                   # ✨ NUEVO
├── infrastructure/
│   └── connectors/
│       └── notion/
│           ├── __init__.py                   # ✨ NUEVO
│           ├── client.py                     # ✨ NUEVO
│           └── schemas.py                    # ✨ NUEVO
├── application/
│   └── use_cases/
│       └── notion/
│           ├── __init__.py                   # ✨ NUEVO
│           ├── create_page.py                # ✨ NUEVO
│           ├── get_page.py                   # ✨ NUEVO
│           ├── update_page.py                # ✨ NUEVO
│           ├── search_pages.py               # ✨ NUEVO
│           ├── create_database_entry.py      # ✨ NUEVO
│           ├── query_database.py             # ✨ NUEVO
│           └── append_blocks.py              # ✨ NUEVO
├── mcp/
│   └── tools/
│       └── notion_tools.py                   # ✨ NUEVO
└── main.py                                   # ✏️ Registrar MCP tools

tests/
└── unit/
    ├── infrastructure/
    │   └── connectors/
    │       └── notion/
    │           ├── __init__.py               # ✨ NUEVO
    │           ├── test_client.py            # ✨ NUEVO
    │           └── test_schemas.py           # ✨ NUEVO
    └── mcp/
        └── tools/
            └── test_notion_tools.py          # ✨ NUEVO

docs/
└── integrations/
    └── notion.md                             # ✨ NUEVO
```

## Implementación Detallada

### Fase 1: Configuración y Dependencias

#### 1.1. Actualizar requirements.txt
```python
# Agregar:
notion-client==2.2.1
```

#### 1.2. Actualizar settings.py
```python
# Agregar campos:
notion_api_key: Optional[str] = Field(
    default=None,
    description="Notion API key for authentication"
)
notion_api_version: str = Field(
    default="2022-06-28",
    description="Notion API version"
)
```

### Fase 2: Domain Layer (Entidades)

#### 2.1. Domain Entity: NotionPage (app/domain/entities/notion_page.py)
```python
@dataclass
class NotionPage:
    """Notion page entity."""
    id: Optional[str] = None
    title: str = ""
    parent_type: str = "page_id"  # page_id, database_id, workspace
    parent_id: Optional[str] = None
    icon: Optional[dict] = None
    cover: Optional[dict] = None
    properties: dict = None
    url: Optional[str] = None
    archived: bool = False
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None

@dataclass
class NotionPageDraft:
    """Draft for creating a new page."""
    title: str
    parent_id: str
    parent_type: str = "page_id"
    properties: Optional[dict] = None
    children: Optional[list] = None  # Initial content blocks
```

#### 2.2. Domain Entity: NotionDatabase (app/domain/entities/notion_database.py)
```python
@dataclass
class NotionDatabaseEntry:
    """Entry in a Notion database."""
    id: Optional[str] = None
    properties: dict = None
    url: Optional[str] = None
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None

@dataclass
class NotionDatabaseQuery:
    """Query criteria for database."""
    database_id: str
    filter: Optional[dict] = None
    sorts: Optional[list] = None
    max_results: int = 100
```

#### 2.3. Domain Entity: NotionBlock (app/domain/entities/notion_block.py)
```python
@dataclass
class NotionBlock:
    """Notion block (content element)."""
    id: Optional[str] = None
    type: str = "paragraph"
    content: dict = None
    has_children: bool = False
    children: list = None
```

### Fase 3: Infrastructure Layer (Cliente y Schemas)

#### 3.1. Notion Client (app/infrastructure/connectors/notion/client.py)
```python
class NotionClient:
    """Notion API client."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Notion client."""
        from notion_client import Client
        self.api_key = api_key or settings.notion_api_key
        self.client = Client(auth=self.api_key)

    # Métodos principales:
    async def create_page(self, draft: NotionPageDraft) -> str
    async def get_page(self, page_id: str) -> NotionPage
    async def update_page(self, page_id: str, properties: dict) -> None
    async def search(self, query: str, filter_type: Optional[str]) -> list
    async def create_database_entry(self, database_id: str, properties: dict) -> str
    async def query_database(self, query: NotionDatabaseQuery) -> list[NotionDatabaseEntry]
    async def append_blocks(self, block_id: str, blocks: list[NotionBlock]) -> None
    async def get_block_children(self, block_id: str) -> list[NotionBlock]
```

#### 3.2. Notion Schemas (app/infrastructure/connectors/notion/schemas.py)
```python
class NotionMapper:
    """Maps between Notion API responses and domain entities."""

    @staticmethod
    def to_page_entity(api_data: dict) -> NotionPage

    @staticmethod
    def from_page_draft(draft: NotionPageDraft) -> dict

    @staticmethod
    def to_database_entry_entity(api_data: dict) -> NotionDatabaseEntry

    @staticmethod
    def to_block_entity(api_data: dict) -> NotionBlock

    @staticmethod
    def from_block(block: NotionBlock) -> dict
```

### Fase 4: Application Layer (Use Cases)

#### 4.1. Create Page Use Case
```python
class CreatePageUseCase:
    """Use case for creating Notion pages."""

    async def execute(self, request: CreatePageRequest) -> CreatePageResponse
```

#### 4.2. Query Database Use Case
```python
class QueryDatabaseUseCase:
    """Use case for querying Notion databases."""

    async def execute(self, request: QueryDatabaseRequest) -> QueryDatabaseResponse
```

#### 4.3. Search Pages Use Case
```python
class SearchPagesUseCase:
    """Use case for searching in Notion."""

    async def execute(self, request: SearchRequest) -> SearchResponse
```

#### 4.4. Append Blocks Use Case
```python
class AppendBlocksUseCase:
    """Use case for adding content to pages."""

    async def execute(self, request: AppendBlocksRequest) -> AppendBlocksResponse
```

### Fase 5: MCP Tools Layer

#### 5.1. Notion Tools (app/mcp/tools/notion_tools.py)
```python
class NotionTools:
    """Collection of Notion MCP tools."""

    # Pydantic models para respuestas estructuradas
    class PageSummary(BaseModel):
        id: str
        title: str
        url: str
        created_time: str
        last_edited_time: str

    class CreatePageResult(BaseModel):
        success: bool
        page_id: Optional[str] = None
        url: Optional[str] = None
        error: Optional[str] = None

    # Métodos principales
    async def create_page(...)
    async def get_page(...)
    async def update_page(...)
    async def search_pages(...)
    async def create_database_entry(...)
    async def query_database(...)
    async def append_content(...)
```

#### 5.2. Registrar Tools en main.py
```python
@mcp.tool()
async def notion_create_page(
    title: str,
    parent_id: str,
    parent_type: str = "page_id",
    content: list[dict] = None
):
    """Create a new page in Notion."""
    return await notion_tools.create_page(...)

@mcp.tool()
async def notion_search(
    query: str,
    filter_type: str = None
):
    """Search in Notion workspace."""
    return await notion_tools.search_pages(...)

@mcp.tool()
async def notion_query_database(
    database_id: str,
    filter: dict = None,
    sorts: list[dict] = None,
    max_results: int = 100
):
    """Query a Notion database with filters and sorting."""
    return await notion_tools.query_database(...)

@mcp.tool()
async def notion_create_database_entry(
    database_id: str,
    properties: dict
):
    """Create a new entry in a Notion database."""
    return await notion_tools.create_database_entry(...)

@mcp.tool()
async def notion_append_content(
    page_id: str,
    blocks: list[dict]
):
    """Append content blocks to a Notion page."""
    return await notion_tools.append_content(...)

@mcp.prompt()
def notion_assistant():
    """Helpful Notion management assistant prompt."""
    return [
        base.UserMessage(
            "You are a helpful Notion management assistant. "
            "I can help you with:\n"
            "- Creating and updating pages\n"
            "- Searching across your Notion workspace\n"
            "- Managing database entries\n"
            "- Querying databases with filters and sorts\n"
            "- Adding content to pages\n\n"
            "What would you like to do with your Notion workspace?"
        )
    ]
```

### Fase 6: Tests

#### 6.1. Unit Tests para Client
```python
# tests/unit/infrastructure/connectors/notion/test_client.py
- test_create_page
- test_get_page
- test_search
- test_query_database
- test_append_blocks
```

#### 6.2. Unit Tests para Schemas
```python
# tests/unit/infrastructure/connectors/notion/test_schemas.py
- test_to_page_entity
- test_from_page_draft
- test_to_database_entry_entity
```

#### 6.3. Unit Tests para MCP Tools
```python
# tests/unit/mcp/tools/test_notion_tools.py
- test_create_page
- test_search_pages
- test_query_database
```

### Fase 7: Documentación

#### 7.1. Crear docs/integrations/notion.md
Documentar:
- Cómo obtener API key de Notion
- Configuración inicial
- Ejemplos de uso
- Estructura de properties para databases
- Tipos de bloques soportados

## MCP Tools Expuestos

| Tool | Descripción | Parámetros Principales |
|------|-------------|------------------------|
| `notion_create_page` | Crear nueva página | title, parent_id, content |
| `notion_get_page` | Obtener página | page_id |
| `notion_update_page` | Actualizar propiedades | page_id, properties |
| `notion_search` | Buscar en workspace | query, filter_type |
| `notion_create_database_entry` | Crear entrada en DB | database_id, properties |
| `notion_query_database` | Consultar database | database_id, filter, sorts |
| `notion_append_content` | Agregar contenido | page_id, blocks |
| `notion_get_page_content` | Leer bloques | page_id |

## Consideraciones Técnicas

### Autenticación
- API key mediante variable de entorno `NOTION_API_KEY`
- Sin OAuth (Notion usa Integration tokens)
- Permisos configurados en Notion Integrations

### Rate Limiting
- Notion tiene rate limits: ~3 requests/second
- Implementar retry con exponential backoff (ya usando tenacity)
- Usar @retry decorator como en Gmail/Holded

### Manejo de Errores
- NotionClient debe manejar errores específicos de Notion API
- Validación de page_id y database_id
- Manejo de permisos insuficientes

### Rich Text y Properties
- Notion usa formato especial para rich text
- Properties tienen tipos específicos (title, rich_text, number, date, etc.)
- Crear helpers para construcción de properties comunes

## Orden de Implementación

1. ✅ **Fase 1**: Configuración y dependencias (30 min)
   - Actualizar requirements.txt
   - Actualizar settings.py

2. ✅ **Fase 2**: Domain entities (1 hora)
   - notion_page.py
   - notion_database.py
   - notion_block.py

3. ✅ **Fase 3**: Infrastructure (2 horas)
   - client.py con métodos principales
   - schemas.py con mappers

4. ✅ **Fase 4**: Use cases (1.5 horas)
   - CreatePageUseCase
   - QueryDatabaseUseCase
   - SearchPagesUseCase
   - AppendBlocksUseCase

5. ✅ **Fase 5**: MCP Tools (1.5 horas)
   - notion_tools.py
   - Registrar en main.py
   - Crear prompt

6. ✅ **Fase 6**: Tests (2 horas)
   - Unit tests para client
   - Unit tests para schemas
   - Unit tests para tools

7. ✅ **Fase 7**: Documentación (30 min)
   - docs/integrations/notion.md
   - Actualizar README

## Tiempo Estimado Total
**~9 horas** de implementación

## Variables de Entorno Requeridas

```bash
# .env
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_API_VERSION=2022-06-28
```

## Casos de Uso Principales

### 1. Crear página de notas
```python
notion_create_page(
    title="Meeting Notes",
    parent_id="workspace_id",
    content=[
        {"type": "heading_1", "text": "Agenda"},
        {"type": "paragraph", "text": "Discuss Q4 goals"}
    ]
)
```

### 2. Agregar tarea a database
```python
notion_create_database_entry(
    database_id="xxx",
    properties={
        "Name": {"title": [{"text": {"content": "Complete integration"}}]},
        "Status": {"select": {"name": "In Progress"}},
        "Due Date": {"date": {"start": "2025-01-15"}}
    }
)
```

### 3. Buscar páginas
```python
notion_search(
    query="integration plan",
    filter_type="page"
)
```

### 4. Consultar database de tareas
```python
notion_query_database(
    database_id="xxx",
    filter={
        "property": "Status",
        "select": {"equals": "In Progress"}
    },
    sorts=[
        {"property": "Due Date", "direction": "ascending"}
    ]
)
```

## Dependencias entre Componentes

```
Settings ─→ NotionClient ─→ Use Cases ─→ NotionTools ─→ MCP Server
              ↑                 ↑
         Schemas          Domain Entities
```

## Criterios de Aceptación

- ✅ Todas las entidades de dominio definidas
- ✅ Cliente de Notion funcionando con operaciones CRUD
- ✅ Mappers bidireccionales implementados
- ✅ Use cases con manejo de errores
- ✅ MCP tools registrados y documentados
- ✅ Tests unitarios >80% coverage
- ✅ Documentación completa
- ✅ Compatible con arquitectura existente

## Próximos Pasos (Post-Implementación)

1. Implementar soporte para más tipos de bloques (images, files, etc.)
2. Agregar caché con Redis para reducir llamadas API
3. Implementar webhooks para sincronización en tiempo real
4. Crear templates de páginas comunes
5. Agregar soporte para comments en páginas

---

**Nota**: Este plan sigue estrictamente la arquitectura DDD establecida en el proyecto y mantiene consistencia con las integraciones de Gmail y Holded existentes.

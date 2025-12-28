# Sumeria Personal Assistant

Un servidor MCP (Model Context Protocol) para gestionar Gmail con soporte para múltiples cuentas.

## Características

- ✉️ **Gestión completa de Gmail**: Enviar, buscar, leer y organizar emails
- 👥 **Múltiples cuentas**: Soporta múltiples cuentas de Gmail simultáneamente
- 🔐 **OAuth2 seguro**: Autenticación mediante Google OAuth2
- 🏗️ **Arquitectura limpia**: DDD (Domain-Driven Design) con separación de capas
- 🚀 **MCP Protocol**: Integración directa con Claude y otros clientes MCP
- 📦 **Type-safe**: Completamente tipado con Pydantic

## Herramientas Disponibles

### Operaciones de Email
- `send_email` - Enviar emails (texto plano o HTML)
- `search_emails` - Buscar emails con filtros avanzados
- `get_email` - Obtener detalles completos de un email
- `mark_email_as_read` - Marcar email como leído
- `mark_email_as_unread` - Marcar email como no leído
- `add_email_label` - Agregar etiquetas a emails

### Gestión de Cuentas
- `list_gmail_accounts` - Listar cuentas autenticadas
- `add_gmail_account` - Agregar nueva cuenta
- `set_default_gmail_account` - Establecer cuenta por defecto

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd sumeria
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Gmail OAuth2

Sigue la guía detallada en [docs/gmail-setup.md](docs/gmail-setup.md) para:
1. Crear proyecto en Google Cloud Console
2. Habilitar Gmail API
3. Configurar OAuth consent screen
4. Descargar credenciales

### 5. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y actualiza:
```env
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_DEFAULT_ACCOUNT=tu-email@gmail.com
```

## Uso

### Ejecutar el servidor MCP

```bash
python -m app.main
```

### Primer uso - Autenticación

La primera vez que uses una herramienta de Gmail:
1. Se abrirá tu navegador
2. Inicia sesión con tu cuenta de Google
3. Autoriza los permisos solicitados
4. El token se guardará automáticamente en `tokens/`

### Ejemplos de uso

#### Buscar emails no leídos

```python
search_emails(
    is_unread=True,
    max_results=10
)
```

#### Enviar email

```python
send_email(
    to=["destinatario@example.com"],
    subject="Hola desde Sumeria",
    body_text="Este es un email de prueba"
)
```

#### Buscar emails de una persona específica

```python
search_emails(
    from_address="alguien@example.com",
    subject="importante",
    max_results=5
)
```

#### Trabajar con múltiples cuentas

```python
# Agregar segunda cuenta
add_gmail_account(account_id="trabajo@gmail.com")

# Buscar en cuenta específica
search_emails(
    is_unread=True,
    account_id="trabajo@gmail.com"
)

# Enviar desde cuenta específica
send_email(
    to=["cliente@example.com"],
    subject="Asunto",
    body_text="Contenido",
    account_id="trabajo@gmail.com"
)
```

## Estructura del Proyecto

```
sumeria/
├── app/
│   ├── config/              # Configuración (Settings, MCP config)
│   ├── core/                # Dependencias, seguridad, excepciones
│   ├── domain/              # Entidades y lógica de negocio
│   │   ├── entities/        # Email, Task, etc.
│   │   ├── repositories/    # Interfaces de repositorios
│   │   └── services/        # Servicios de dominio
│   ├── infrastructure/      # Implementaciones técnicas
│   │   ├── connectors/      # Gmail, Notion, WhatsApp
│   │   │   └── gmail/       # Cliente Gmail, OAuth, Schemas
│   │   ├── queue/           # Celery/ARQ (futuro)
│   │   └── cache/           # Redis (futuro)
│   ├── application/         # Casos de uso
│   │   └── use_cases/       # SendEmail, SearchEmails, etc.
│   └── mcp/                 # Servidor MCP
│       ├── server.py        # Definición del servidor
│       └── tools/           # Herramientas MCP
├── docs/                    # Documentación
├── tests/                   # Tests (futuro)
├── requirements.txt         # Dependencias
├── .env.example            # Ejemplo de configuración
└── README.md
```

## Arquitectura

El proyecto sigue principios de **Domain-Driven Design (DDD)**:

- **Domain Layer**: Entidades de negocio independientes de frameworks
- **Application Layer**: Casos de uso que orquestan la lógica
- **Infrastructure Layer**: Implementaciones técnicas (Gmail API, OAuth)
- **MCP Layer**: Adaptadores para exponer funcionalidad vía MCP

## Desarrollo

### Ejecutar tests (futuro)

```bash
pytest
```

### Linting y formato

```bash
# Format code
black app/

# Lint
ruff check app/

# Type checking
mypy app/
```

## Próximas Características

- [ ] Integración con Notion
- [ ] Integración con Google Calendar
- [ ] Integración con WhatsApp
- [ ] Procesamiento de documentos
- [ ] Base de datos para persistencia
- [ ] Cache con Redis
- [ ] Task queue para operaciones asíncronas
- [ ] API REST (FastAPI)
- [ ] Tests unitarios e integración

## Seguridad

⚠️ **Importante**:
- Nunca commitees `credentials.json` o archivos en `tokens/`
- Mantén tu `.env` privado
- Los tokens tienen acceso completo a tu Gmail
- Revoca acceso en [Google Account Settings](https://myaccount.google.com/permissions) si es necesario

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

MIT License - ver archivo LICENSE para detalles

## Soporte

Para problemas o preguntas:
1. Revisa [docs/gmail-setup.md](docs/gmail-setup.md) para configuración de Gmail
2. Abre un issue en GitHub
3. Consulta la documentación de [MCP Protocol](https://modelcontextprotocol.io/)

---

Hecho con ❤️ usando [FastMCP](https://github.com/jlowin/fastmcp) y [Google Gmail API](https://developers.google.com/gmail/api)

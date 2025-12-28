# Sumeria Personal Assistant

Un servidor MCP (Model Context Protocol) para gestionar Gmail y Holded con soporte completo para operaciones de negocio.

## Características

- ✉️ **Gestión completa de Gmail**: Enviar, buscar, leer y organizar emails
- 👥 **Múltiples cuentas Gmail**: Soporta múltiples cuentas de Gmail simultáneamente
- 💼 **Integración con Holded**: Gestión de facturas, contactos y productos
- 🔐 **Autenticación segura**: OAuth2 para Gmail, API Key para Holded
- 🏗️ **Arquitectura limpia**: DDD (Domain-Driven Design) con separación de capas
- 🚀 **MCP Protocol**: Integración directa con Claude y otros clientes MCP
- 📦 **Type-safe**: Completamente tipado con Pydantic

## Herramientas Disponibles

### Gmail - Operaciones de Email
- `send_email` - Enviar emails (texto plano o HTML)
- `search_emails` - Buscar emails con filtros avanzados
- `get_email` - Obtener detalles completos de un email
- `mark_email_as_read` - Marcar email como leído
- `mark_email_as_unread` - Marcar email como no leído
- `add_email_label` - Agregar etiquetas a emails

### Gmail - Gestión de Cuentas
- `list_gmail_accounts` - Listar cuentas autenticadas
- `add_gmail_account` - Agregar nueva cuenta
- `set_default_gmail_account` - Establecer cuenta por defecto

### Holded - Gestión de Facturas
- `holded_create_invoice` - Crear facturas, presupuestos y proformas
- `holded_get_invoice` - Obtener detalles de una factura
- `holded_list_invoices` - Listar y filtrar facturas

### Holded - Gestión de Contactos
- `holded_create_contact` - Crear clientes o proveedores
- `holded_get_contact` - Obtener detalles de un contacto
- `holded_list_contacts` - Listar todos los contactos

### Holded - Catálogo de Productos
- `holded_list_products` - Listar productos con precios y stock

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

### 5. Configurar Holded API

1. Inicia sesión en tu cuenta de Holded
2. Ve a **Configuración** → **Desarrolladores**
3. Genera una API key
4. Copia la API key

### 6. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y actualiza:
```env
# Gmail
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_DEFAULT_ACCOUNT=tu-email@gmail.com

# Holded
HOLDED_API_KEY=tu-api-key-de-holded
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

#### Gmail - Buscar emails no leídos

```python
search_emails(
    is_unread=True,
    max_results=10
)
```

#### Gmail - Enviar email

```python
send_email(
    to=["destinatario@example.com"],
    subject="Hola desde Sumeria",
    body_text="Este es un email de prueba"
)
```

#### Gmail - Trabajar con múltiples cuentas

```python
# Agregar segunda cuenta
add_gmail_account(account_id="trabajo@gmail.com")

# Buscar en cuenta específica
search_emails(
    is_unread=True,
    account_id="trabajo@gmail.com"
)
```

#### Holded - Crear factura

```python
holded_create_invoice(
    contact_id="63f8a1234567890abcdef123",
    items=[
        {
            "name": "Servicio de Desarrollo Web",
            "quantity": 40,
            "price": 50.0,
            "tax_rate": 21.0
        }
    ],
    date="2025-01-15",
    due_date="2025-02-15"
)
```

#### Holded - Crear cliente

```python
holded_create_contact(
    name="Acme Corporation",
    email="contacto@acme.com",
    vat_number="ESB12345678",
    type="client",
    billing_address={
        "street": "Calle Mayor 1",
        "city": "Madrid",
        "postal_code": "28001",
        "country": "Spain"
    }
)
```

#### Holded - Listar facturas pendientes

```python
holded_list_invoices(
    paid=False,
    status="sent",
    max_results=20
)
```

Ver más ejemplos en [docs/holded-integration.md](docs/holded-integration.md)

## Estructura del Proyecto

```
sumeria/
├── app/
│   ├── config/              # Configuración (Settings, MCP config)
│   ├── core/                # Dependencias, seguridad, excepciones
│   ├── domain/              # Entidades y lógica de negocio
│   │   ├── entities/        # Email, Invoice, Contact, Product, etc.
│   │   ├── repositories/    # Interfaces de repositorios
│   │   └── services/        # Servicios de dominio
│   ├── infrastructure/      # Implementaciones técnicas
│   │   ├── connectors/      # Integraciones externas
│   │   │   ├── gmail/       # Cliente Gmail, OAuth, Schemas
│   │   │   └── holded/      # Cliente Holded, API, Schemas
│   │   ├── queue/           # Celery/ARQ (futuro)
│   │   └── cache/           # Redis (futuro)
│   ├── application/         # Casos de uso
│   │   └── use_cases/       # Gmail, Holded, etc.
│   └── mcp/                 # Servidor MCP
│       ├── server.py        # Definición del servidor
│       └── tools/           # Herramientas MCP (Gmail, Holded)
├── docs/                    # Documentación
│   ├── gmail-setup.md      # Guía de configuración Gmail
│   └── holded-integration.md # Guía de integración Holded
├── tests/                   # Tests unitarios e integración
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

## Documentación

- [Configuración de Gmail](docs/gmail-setup.md) - Guía paso a paso para configurar Gmail OAuth2
- [Integración con Holded](docs/holded-integration.md) - Documentación completa de la integración Holded
- [Arquitectura](. agent/architecture.instructions.md) - Detalles de la arquitectura del proyecto

## Próximas Características

- [ ] Integración con Notion
- [ ] Integración con Google Calendar
- [ ] Integración con WhatsApp
- [ ] Procesamiento de documentos
- [ ] Base de datos para persistencia
- [ ] Cache con Redis
- [ ] Task queue para operaciones asíncronas
- [ ] API REST (FastAPI)
- [x] Tests unitarios e integración

## Seguridad

⚠️ **Importante**:
- Nunca commitees `credentials.json`, archivos en `tokens/`, o tu `.env`
- Mantén tus API keys privadas
- Los tokens de Gmail tienen acceso completo a tu cuenta
- La API key de Holded tiene acceso a todos tus datos de negocio
- Revoca acceso en [Google Account Settings](https://myaccount.google.com/permissions) si es necesario
- Regenera tu API key de Holded si crees que ha sido comprometida

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
1. Revisa la documentación:
   - [Gmail Setup](docs/gmail-setup.md) para configuración de Gmail
   - [Holded Integration](docs/holded-integration.md) para configuración de Holded
2. Abre un issue en GitHub
3. Consulta la documentación de:
   - [MCP Protocol](https://modelcontextprotocol.io/)
   - [Holded API](https://developers.holded.com/)

---

Hecho con ❤️ usando [FastMCP](https://github.com/jlowin/fastmcp), [Google Gmail API](https://developers.google.com/gmail/api), y [Holded API](https://developers.holded.com/)

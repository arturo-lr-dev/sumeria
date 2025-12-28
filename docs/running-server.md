# Running the Sumeria MCP Server

Hay varias formas de ejecutar el servidor MCP según tus necesidades.

## Métodos de Ejecución

### 1. Usando run.sh (Recomendado para desarrollo con HTTP)

El script `run.sh` arranca el servidor en modo HTTP con Cloudflare tunnel:

```bash
./run.sh
```

Esto ejecuta:
- Transporte: HTTP
- Puerto: 8000
- URL local: http://localhost:8000
- URL pública: https://celebration-beings-powder-booking.trycloudflare.com (via Cloudflare tunnel)

### 2. Usando stdio (Para Claude Desktop)

Para integración directa con Claude Desktop, usa el transporte stdio:

```bash
python -m app.main
```

Configuración en `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sumeria": {
      "command": "python",
      "args": ["-m", "app.main"],
      "cwd": "/ruta/completa/a/sumeria",
      "env": {
        "GMAIL_CREDENTIALS_FILE": "credentials.json",
        "GMAIL_DEFAULT_ACCOUNT": "tu-email@gmail.com"
      }
    }
  }
}
```

### 3. Usando fastmcp dev (Para testing)

Para probar el servidor con el MCP Inspector:

```bash
fastmcp dev app/mcp/server.py:mcp
```

Esto abrirá una interfaz web para probar las herramientas interactivamente.

### 4. Modo HTTP manual

```bash
fastmcp run app/mcp/server.py:mcp --transport http --port 8000
```

## Variables de Entorno

Antes de ejecutar, asegúrate de configurar `.env`:

```env
# Requerido
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_DEFAULT_ACCOUNT=tu-email@gmail.com

# Opcional
MCP_TRANSPORT=stdio  # o "streamable-http"
DEBUG=false
LOG_LEVEL=INFO
```

## Verificar que el Servidor Funciona

Ejecuta el script de prueba:

```bash
python test_server.py
```

Deberías ver:
```
✓ Settings module loaded successfully
✓ MCP server module loaded successfully
✓ Registered 9 MCP tools:
  - send_email
  - search_emails
  - get_email
  - mark_email_as_read
  - mark_email_as_unread
  - add_email_label
  - list_gmail_accounts
  - add_gmail_account
  - set_default_gmail_account

✅ All imports successful! Server is ready to run.
```

## Herramientas Disponibles

Una vez que el servidor esté corriendo, tendrás acceso a estas herramientas:

### Gestión de Emails
- `send_email` - Enviar emails
- `search_emails` - Buscar emails con filtros
- `get_email` - Obtener detalles de un email
- `mark_email_as_read` - Marcar como leído
- `mark_email_as_unread` - Marcar como no leído
- `add_email_label` - Agregar etiqueta

### Gestión de Cuentas
- `list_gmail_accounts` - Listar cuentas autenticadas
- `add_gmail_account` - Agregar nueva cuenta
- `set_default_gmail_account` - Establecer cuenta por defecto

## Troubleshooting

### El servidor no arranca

1. Verifica que las dependencias estén instaladas:
   ```bash
   pip install -r requirements.txt
   ```

2. Verifica que `.env` existe y tiene la configuración correcta

3. Revisa los logs para ver errores específicos

### Error: "Credentials file not found"

Necesitas configurar OAuth2. Ver [docs/gmail-setup.md](gmail-setup.md)

### Error con Cloudflare tunnel

Si `run.sh` muestra errores de Host header:
- Esto es normal durante el desarrollo
- El servidor acepta conexiones de cualquier host
- Para producción, restringe `allowed_hosts` en `app/mcp/server.py`

### Primera autenticación

La primera vez que uses una herramienta de Gmail:
1. Se abrirá tu navegador
2. Inicia sesión con Google
3. Autoriza los permisos
4. El token se guardará en `tokens/`

## Logs

Los logs del servidor se muestran en la consola. Para más detalle:

```env
# En .env
LOG_LEVEL=DEBUG
```

## Seguridad en Producción

⚠️ Para producción, actualiza `app/mcp/server.py`:

```python
mcp = FastMCP(
    name=settings.mcp_server_name,
    allowed_origins=["https://tu-dominio.com"],  # ← Dominios específicos
    allowed_hosts=["tu-dominio.com"],  # ← Hosts específicos
)
```

Y configura HTTPS con certificados válidos.

# Quickstart - Sumeria MCP Server

Guía rápida para poner en marcha el servidor en 5 minutos.

## 1. Instalar Dependencias

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## 2. Configurar Gmail OAuth2

### Opción A: Ya tienes credentials.json

Si ya descargaste `credentials.json` de Google Cloud Console:

```bash
# Copiar el archivo a la raíz del proyecto
cp /ruta/a/tu/credentials.json .

# Crear archivo .env
cp .env.example .env

# Editar .env y configurar tu email
nano .env  # o usar tu editor favorito
```

En `.env`:
```env
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_DEFAULT_ACCOUNT=tu-email@gmail.com
```

### Opción B: Aún no tienes credentials.json

Sigue la guía completa: [docs/gmail-setup.md](docs/gmail-setup.md)

Resumen:
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear proyecto
3. Habilitar Gmail API
4. Crear OAuth2 credentials (Desktop app)
5. Descargar como `credentials.json`

## 3. Verificar Configuración

```bash
python test_server.py
```

Deberías ver:
```
✓ Settings module loaded successfully
✓ MCP server module loaded successfully
✓ Registered 9 MCP tools
✅ All imports successful!
```

## 4. Ejecutar el Servidor

### Para desarrollo con HTTP:

```bash
./run.sh
```

El servidor estará disponible en:
- Local: http://localhost:8000
- Cloudflare tunnel: https://celebration-beings-powder-booking.trycloudflare.com

### Para Claude Desktop (stdio):

```bash
python -m app.main
```

## 5. Primera Autenticación

La primera vez que uses una herramienta de Gmail:

1. El navegador se abrirá automáticamente
2. Selecciona tu cuenta de Google
3. Autoriza los permisos solicitados
4. Si aparece "App no verificada":
   - Click en "Advanced"
   - Click en "Go to Sumeria (unsafe)"
   - Esto es normal para desarrollo
5. El token se guardará automáticamente

## 6. Probar las Herramientas

### Con MCP Inspector:

```bash
fastmcp dev app/mcp/server.py:mcp
```

Esto abre una interfaz web para probar las herramientas.

### Ejemplos de uso:

```python
# Buscar emails no leídos
search_emails(is_unread=True, max_results=5)

# Enviar email
send_email(
    to=["destinatario@example.com"],
    subject="Test desde Sumeria",
    body_text="Hola desde el MCP server!"
)

# Ver cuentas autenticadas
list_gmail_accounts()
```

## 7. Múltiples Cuentas

Para agregar más cuentas de Gmail:

```python
# Agregar segunda cuenta (abrirá navegador para autenticar)
add_gmail_account(account_id="trabajo@gmail.com")

# Listar todas las cuentas
list_gmail_accounts()

# Usar cuenta específica
search_emails(
    is_unread=True,
    account_id="trabajo@gmail.com"
)
```

## Siguientes Pasos

- Lee [README.md](README.md) para más detalles
- Ver [docs/gmail-setup.md](docs/gmail-setup.md) para configuración avanzada
- Ver [docs/running-server.md](docs/running-server.md) para diferentes modos de ejecución

## Troubleshooting Común

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Credentials file not found"
Asegúrate de que `credentials.json` está en la raíz del proyecto.

### OAuth no funciona
Verifica que agregaste tu email como "test user" en Google Cloud Console.

### El servidor no arranca
```bash
# Ver errores detallados
DEBUG=true python -m app.main
```

## ¿Necesitas Ayuda?

1. Revisa la documentación completa en `docs/`
2. Abre un issue en GitHub
3. Verifica los logs del servidor

---

¡Listo! Ya tienes el servidor funcionando 🚀

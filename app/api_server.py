"""
FastAPI server for handling webhooks.

This server runs separately from the MCP server to handle incoming webhooks
from WhatsApp and other services that require HTTP endpoints.

To run this server:
    uvicorn app.api_server:app --host 0.0.0.0 --port 8000

For development with auto-reload:
    uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.api.v1.router import api_router


# Create FastAPI application
app = FastAPI(
    title=f"{settings.app_name} - API Server",
    version=settings.app_version,
    description="API server for handling webhooks and external integrations",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Important: Expose Mcp-Session-Id header for MCP protocol (if using HTTP transport)
    expose_headers=["Mcp-Session-Id"],
)

# Mount API v1 router
app.include_router(
    api_router,
    prefix=settings.api_v1_prefix
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "whatsapp_webhook": f"{settings.api_v1_prefix}/whatsapp/webhook",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "api-server"
    }


if __name__ == "__main__":
    import uvicorn

    print(f"Starting {settings.app_name} - API Server")
    print(f"Version: {settings.app_version}")
    print(f"Webhook endpoint: http://localhost:8000{settings.api_v1_prefix}/whatsapp/webhook")
    print("-" * 50)

    uvicorn.run(
        "app.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

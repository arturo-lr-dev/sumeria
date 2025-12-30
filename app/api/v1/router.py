"""
API v1 router.
Aggregates all API endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import whatsapp_webhook


# Create main API router
api_router = APIRouter()

# Include WhatsApp webhook endpoints
api_router.include_router(
    whatsapp_webhook.router,
    prefix="/whatsapp",
    tags=["whatsapp"]
)

# Future: Add other API endpoints here
# api_router.include_router(
#     other_endpoints.router,
#     prefix="/other",
#     tags=["other"]
# )

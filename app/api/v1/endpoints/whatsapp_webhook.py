"""
WhatsApp webhook endpoints.
Handles webhook verification and incoming messages from WhatsApp Business Cloud API.
"""
import hmac
import hashlib
from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException, Header, Query

from app.config.settings import settings
from app.application.use_cases.whatsapp.process_webhook_message import (
    ProcessWebhookMessageUseCase,
    ProcessWebhookMessageRequest
)


router = APIRouter()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    """
    Webhook verification endpoint for Meta.

    Meta sends a GET request to verify webhook ownership during setup.
    Must return hub.challenge if verify token matches.

    This is called once when setting up the webhook in Meta Business Manager.

    Args:
        hub_mode: Should be "subscribe"
        hub_challenge: Challenge string from Meta
        hub_verify_token: Verification token (must match our configured token)

    Returns:
        The challenge string if verification succeeds

    Raises:
        HTTPException: 403 if verification token doesn't match
    """
    # Verify the token matches
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_webhook_verify_token:
        # Respond with the challenge to verify the webhook
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        raise HTTPException(
            status_code=403,
            detail="Verification token mismatch or invalid mode"
        )


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Receive incoming WhatsApp messages and status updates.

    Meta sends POST requests with message data and status updates.
    Should verify signature for security and return 200 quickly.

    Args:
        request: FastAPI request with webhook payload
        x_hub_signature_256: HMAC SHA256 signature from Meta (in header)

    Returns:
        Success response (must be returned within 20 seconds)

    Raises:
        HTTPException: 403 if signature is invalid
    """
    # Get raw body for signature verification
    body = await request.body()

    # Verify webhook signature (security measure)
    if not verify_webhook_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=403,
            detail="Invalid webhook signature"
        )

    # Parse JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON payload: {e}"
        )

    # Process webhook asynchronously (to avoid timeout)
    # Note: This is a simple implementation. For production, consider:
    # - Using a task queue (Celery, ARQ, etc.)
    # - Using background tasks (FastAPI BackgroundTasks)
    # - Storing in database for later processing
    await process_webhook_async(payload)

    # Must return 200 immediately (within 20 seconds or Meta will retry)
    return {"status": "received"}


async def process_webhook_async(payload: dict):
    """
    Process webhook in background.

    This function processes the webhook payload and extracts messages.
    In a production environment, you might want to:
    - Store messages in a database
    - Trigger notification handlers
    - Process auto-reply rules
    - Forward to other systems

    Args:
        payload: Complete webhook payload from WhatsApp
    """
    try:
        use_case = ProcessWebhookMessageUseCase()
        request = ProcessWebhookMessageRequest(webhook_payload=payload)
        response = await use_case.execute(request)

        if response.success:
            # Log successful processing
            print(f"Processed {response.message_count} WhatsApp messages")

            # TODO: Add your custom logic here
            # - Store messages in database
            # - Send notifications
            # - Trigger auto-replies
            # - Forward to other systems

            # Example: Print received messages
            for message in response.messages:
                print(f"Received message from {message.from_number}: {message.text_content}")

        else:
            print(f"Error processing webhook: {response.error}")

    except Exception as e:
        # Log error but don't raise (webhook already responded with 200)
        print(f"Error in webhook processing: {e}")


def verify_webhook_signature(body: bytes, signature: Optional[str]) -> bool:
    """
    Verify webhook signature from Meta using HMAC SHA256.

    Meta signs all webhook requests with your app secret.
    This verifies the request actually came from Meta.

    Args:
        body: Raw request body (bytes)
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    # If no signature provided, reject
    if not signature:
        return False

    # Get app secret from settings
    app_secret = settings.whatsapp_app_secret

    if not app_secret:
        # If app secret not configured, skip verification (development mode)
        # WARNING: This is insecure! Always configure app secret in production!
        print("WARNING: WhatsApp app secret not configured - skipping signature verification")
        return True

    try:
        # Compute expected signature
        expected_signature = hmac.new(
            app_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        # Format: "sha256=<hash>"
        expected_signature_formatted = f"sha256={expected_signature}"

        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(signature, expected_signature_formatted)

    except Exception as e:
        print(f"Error verifying webhook signature: {e}")
        return False

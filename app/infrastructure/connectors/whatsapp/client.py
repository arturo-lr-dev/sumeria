"""
WhatsApp Business Cloud API client implementation.
Handles all interactions with WhatsApp Business Cloud API (Meta).
"""
from typing import Optional, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.domain.entities.whatsapp_message import WhatsAppMedia, WhatsAppMessageDraft
from app.domain.entities.whatsapp_template import WhatsAppTemplate


class WhatsAppClient:
    """
    WhatsApp Business Cloud API client.

    Handles authentication and API communication with Meta's WhatsApp API.
    Supports sending messages, managing media, and retrieving templates.

    API Documentation: https://developers.facebook.com/docs/whatsapp/cloud-api
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        phone_number_id: Optional[str] = None
    ):
        """
        Initialize WhatsApp client.

        Args:
            access_token: Meta access token (will use settings if not provided)
            phone_number_id: WhatsApp Business phone number ID

        Raises:
            ValueError: If required credentials are missing
        """
        self.access_token = access_token or settings.whatsapp_access_token
        self.phone_number_id = phone_number_id or settings.whatsapp_phone_number_id

        if not self.access_token:
            raise ValueError("WhatsApp access token is required")
        if not self.phone_number_id:
            raise ValueError("WhatsApp phone number ID is required")

        self.base_url = f"{settings.whatsapp_api_base_url}/{settings.whatsapp_api_version}"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        files: Optional[dict] = None
    ) -> Any:
        """
        Make HTTP request to WhatsApp API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data (JSON)
            params: Query parameters
            files: Files for multipart upload (for media)

        Returns:
            Response data

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        # For file uploads, use different headers
        headers = self.headers.copy()
        if files:
            # Remove Content-Type for multipart/form-data (httpx sets it automatically)
            headers.pop("Content-Type", None)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=data if not files else None,
                params=params,
                files=files
            )

            response.raise_for_status()

            if response.status_code == 204:
                return None

            return response.json()

    # ============ Message Sending Operations ============

    async def send_text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> str:
        """
        Send a text message.

        Args:
            to: Recipient phone number (E.164 format: +1234567890)
            text: Message text (max 4096 characters)
            preview_url: Enable URL preview for links in message

        Returns:
            Message ID (wamid)

        Raises:
            ValueError: If phone number format is invalid
            httpx.HTTPError: If API request fails
        """
        try:
            if not to.startswith('+'):
                raise ValueError(f"Phone number must be in E.164 format: {to}")

            if len(text) > 4096:
                raise ValueError("Text message cannot exceed 4096 characters")

            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to.lstrip('+'),  # WhatsApp API expects number without +
                "type": "text",
                "text": {
                    "preview_url": preview_url,
                    "body": text
                }
            }

            result = await self._request(
                method="POST",
                endpoint=f"/{self.phone_number_id}/messages",
                data=data
            )

            return result.get("messages", [{}])[0].get("id", "")

        except Exception as error:
            raise Exception(f"Failed to send text message: {error}")

    async def send_media_message(
        self,
        to: str,
        media: WhatsAppMedia
    ) -> str:
        """
        Send a media message (image, video, document, audio).

        Args:
            to: Recipient phone number (E.164 format)
            media: WhatsAppMedia object with media details

        Returns:
            Message ID (wamid)

        Raises:
            ValueError: If media is invalid
            httpx.HTTPError: If API request fails
        """
        try:
            if not to.startswith('+'):
                raise ValueError(f"Phone number must be in E.164 format: {to}")

            if not media.media_id and not media.media_url:
                raise ValueError("Either media_id or media_url must be provided")

            # Build media object
            media_object = {}
            if media.media_id:
                media_object["id"] = media.media_id
            elif media.media_url:
                media_object["link"] = media.media_url

            if media.caption:
                media_object["caption"] = media.caption

            if media.filename and media.media_type == 'document':
                media_object["filename"] = media.filename

            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to.lstrip('+'),
                "type": media.media_type,
                media.media_type: media_object
            }

            result = await self._request(
                method="POST",
                endpoint=f"/{self.phone_number_id}/messages",
                data=data
            )

            return result.get("messages", [{}])[0].get("id", "")

        except Exception as error:
            raise Exception(f"Failed to send media message: {error}")

    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language: str,
        parameters: list[str]
    ) -> str:
        """
        Send a pre-approved template message.

        Args:
            to: Recipient phone number (E.164 format)
            template_name: Name of the approved template
            language: Language code (e.g., "en_US", "es_ES")
            parameters: Template parameter values (e.g., ["John", "123"])

        Returns:
            Message ID (wamid)

        Raises:
            ValueError: If template parameters are invalid
            httpx.HTTPError: If API request fails
        """
        try:
            if not to.startswith('+'):
                raise ValueError(f"Phone number must be in E.164 format: {to}")

            # Build template components with parameters
            components = []
            if parameters:
                components.append({
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": param}
                        for param in parameters
                    ]
                })

            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to.lstrip('+'),
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language
                    },
                    "components": components
                }
            }

            result = await self._request(
                method="POST",
                endpoint=f"/{self.phone_number_id}/messages",
                data=data
            )

            return result.get("messages", [{}])[0].get("id", "")

        except Exception as error:
            raise Exception(f"Failed to send template message: {error}")

    # ============ Media Operations ============

    async def upload_media(
        self,
        file_data: bytes,
        mime_type: str,
        filename: str
    ) -> str:
        """
        Upload media to WhatsApp servers.

        Args:
            file_data: Binary file data
            mime_type: MIME type of the file
            filename: Original filename

        Returns:
            Media ID (for use in send_media_message)

        Raises:
            httpx.HTTPError: If upload fails
        """
        try:
            files = {
                'file': (filename, file_data, mime_type)
            }

            data_form = {
                'messaging_product': 'whatsapp'
            }

            # Note: This uses multipart/form-data, not JSON
            # We need to send form data separately
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}

                response = await client.post(
                    f"{self.base_url}/{self.phone_number_id}/media",
                    headers=headers,
                    files=files,
                    data=data_form
                )

                response.raise_for_status()
                result = response.json()

            return result.get("id", "")

        except Exception as error:
            raise Exception(f"Failed to upload media: {error}")

    async def get_media_url(self, media_id: str) -> str:
        """
        Get download URL for a media file.

        Args:
            media_id: WhatsApp media ID

        Returns:
            Download URL (temporary, expires)

        Raises:
            httpx.HTTPError: If request fails
        """
        try:
            result = await self._request(
                method="GET",
                endpoint=f"/{media_id}"
            )

            return result.get("url", "")

        except Exception as error:
            raise Exception(f"Failed to get media URL: {error}")

    async def download_media(self, media_id: str) -> tuple[bytes, str]:
        """
        Download media file.

        Args:
            media_id: WhatsApp media ID

        Returns:
            Tuple of (file_data, mime_type)

        Raises:
            httpx.HTTPError: If download fails
        """
        try:
            # First, get the download URL
            media_url = await self.get_media_url(media_id)

            if not media_url:
                raise Exception("Failed to retrieve media URL")

            # Download the media
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = await client.get(media_url, headers=headers)
                response.raise_for_status()

                mime_type = response.headers.get("Content-Type", "application/octet-stream")
                return response.content, mime_type

        except Exception as error:
            raise Exception(f"Failed to download media: {error}")

    # ============ Message Operations ============

    async def mark_message_as_read(self, message_id: str) -> None:
        """
        Mark an incoming message as read.

        Args:
            message_id: WhatsApp message ID (wamid)

        Raises:
            httpx.HTTPError: If request fails
        """
        try:
            data = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }

            await self._request(
                method="POST",
                endpoint=f"/{self.phone_number_id}/messages",
                data=data
            )

        except Exception as error:
            raise Exception(f"Failed to mark message as read: {error}")

    # ============ Template Operations ============

    async def list_templates(self) -> list[dict]:
        """
        List all message templates for the business account.

        Returns:
            List of template data (raw API format)

        Raises:
            httpx.HTTPError: If request fails

        Note:
            This returns raw template data. Use WhatsAppMapper.to_template_entity()
            to convert to domain entities.
        """
        try:
            # Templates are associated with the WhatsApp Business Account (WABA)
            business_account_id = settings.whatsapp_business_account_id

            if not business_account_id:
                raise ValueError("WhatsApp Business Account ID is required to list templates")

            result = await self._request(
                method="GET",
                endpoint=f"/{business_account_id}/message_templates"
            )

            return result.get("data", [])

        except Exception as error:
            raise Exception(f"Failed to list templates: {error}")

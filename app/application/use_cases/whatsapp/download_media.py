"""
Download WhatsApp media use case.
Handles downloading media files from WhatsApp messages.
"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from app.infrastructure.connectors.whatsapp.client import WhatsAppClient


@dataclass
class DownloadMediaRequest:
    """
    Request to download media from WhatsApp.

    Attributes:
        media_id: WhatsApp media ID (from incoming message)
        save_path: Optional local path to save the file
    """
    media_id: str
    save_path: Optional[str] = None


@dataclass
class DownloadMediaResponse:
    """
    Response after downloading media.

    Attributes:
        success: Whether the download was successful
        media_data: Binary media data (if not saved to file)
        mime_type: MIME type of the media
        size_bytes: Size of the media file in bytes
        saved_path: Path where file was saved (if save_path provided)
        error: Error message if failed
    """
    success: bool
    media_data: Optional[bytes] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    saved_path: Optional[str] = None
    error: Optional[str] = None


class DownloadMediaUseCase:
    """
    Use case for downloading media from WhatsApp messages.

    Downloads media and optionally saves to local file.
    """

    def __init__(self, client: Optional[WhatsAppClient] = None):
        """
        Initialize use case.

        Args:
            client: WhatsAppClient instance (creates new if not provided)
        """
        self.client = client or WhatsAppClient()

    async def execute(
        self,
        request: DownloadMediaRequest
    ) -> DownloadMediaResponse:
        """
        Execute the use case to download media.

        Args:
            request: Download media request

        Returns:
            Response with media data or saved path
        """
        try:
            # Validate media ID
            if not request.media_id:
                return DownloadMediaResponse(
                    success=False,
                    error="media_id is required"
                )

            # Download media
            media_data, mime_type = await self.client.download_media(
                media_id=request.media_id
            )

            size_bytes = len(media_data)

            # Save to file if path provided
            saved_path = None
            if request.save_path:
                try:
                    save_file = Path(request.save_path)

                    # Create parent directories if needed
                    save_file.parent.mkdir(parents=True, exist_ok=True)

                    # Write file
                    save_file.write_bytes(media_data)
                    saved_path = str(save_file)

                    # Clear media_data if saved to file (to save memory)
                    media_data = None

                except Exception as e:
                    return DownloadMediaResponse(
                        success=False,
                        error=f"Failed to save file: {e}"
                    )

            return DownloadMediaResponse(
                success=True,
                media_data=media_data,
                mime_type=mime_type,
                size_bytes=size_bytes,
                saved_path=saved_path
            )

        except Exception as e:
            return DownloadMediaResponse(
                success=False,
                error=str(e)
            )

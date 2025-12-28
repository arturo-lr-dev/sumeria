"""
Gmail API client implementation.
Handles all interactions with Gmail API.
"""
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.infrastructure.connectors.gmail.oauth import GmailOAuthHandler
from app.infrastructure.connectors.gmail.schemas import GmailMessageMapper
from app.domain.entities.email import Email, EmailDraft, EmailSearchCriteria


class GmailClient:
    """
    Gmail API client for email operations.
    Handles authentication and API communication for a specific account.
    """

    def __init__(
        self,
        account_id: str,
        oauth_handler: Optional[GmailOAuthHandler] = None
    ):
        """
        Initialize Gmail client for a specific account.

        Args:
            account_id: Gmail account identifier (email or alias)
            oauth_handler: OAuth handler for authentication (will be created if not provided)
        """
        self.account_id = account_id
        self.oauth_handler = oauth_handler or GmailOAuthHandler(account_id=account_id)
        self._service = None
        self._user_email: Optional[str] = None

    def _get_service(self):
        """Get or create Gmail API service."""
        if self._service is None:
            creds = self.oauth_handler.get_credentials()
            self._service = build('gmail', 'v1', credentials=creds)
        return self._service

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def send_email(self, draft: EmailDraft) -> str:
        """
        Send an email.

        Args:
            draft: Email draft to send

        Returns:
            Message ID of sent email

        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            service = self._get_service()

            # Convert draft to Gmail message format
            raw_message = GmailMessageMapper.from_email_draft(draft)

            message = {'raw': raw_message}

            # Send message
            result = service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            return result['id']

        except HttpError as error:
            raise Exception(f"Failed to send email: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_email(self, message_id: str) -> Email:
        """
        Get a specific email by ID.

        Args:
            message_id: Gmail message ID

        Returns:
            Email entity

        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            service = self._get_service()

            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            return GmailMessageMapper.to_email_entity(message)

        except HttpError as error:
            raise Exception(f"Failed to get email: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def search_emails(
        self,
        criteria: EmailSearchCriteria
    ) -> list[Email]:
        """
        Search emails based on criteria.

        Args:
            criteria: Search criteria

        Returns:
            List of matching emails

        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            service = self._get_service()

            # Convert criteria to Gmail query
            query = criteria.to_gmail_query()

            # Search messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=criteria.max_results
            ).execute()

            messages = results.get('messages', [])

            # Fetch full message details
            emails = []
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                emails.append(GmailMessageMapper.to_email_entity(message))

            return emails

        except HttpError as error:
            raise Exception(f"Failed to search emails: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def mark_as_read(self, message_id: str) -> None:
        """
        Mark an email as read.

        Args:
            message_id: Gmail message ID

        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            service = self._get_service()

            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        except HttpError as error:
            raise Exception(f"Failed to mark email as read: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def mark_as_unread(self, message_id: str) -> None:
        """
        Mark an email as unread.

        Args:
            message_id: Gmail message ID

        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            service = self._get_service()

            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()

        except HttpError as error:
            raise Exception(f"Failed to mark email as unread: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def add_label(self, message_id: str, label: str) -> None:
        """
        Add a label to an email.

        Args:
            message_id: Gmail message ID
            label: Label to add

        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            service = self._get_service()

            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label]}
            ).execute()

        except HttpError as error:
            raise Exception(f"Failed to add label: {error}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_attachment(
        self,
        message_id: str,
        attachment_id: str
    ) -> bytes:
        """
        Get attachment data.

        Args:
            message_id: Gmail message ID
            attachment_id: Attachment ID

        Returns:
            Attachment data as bytes

        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            service = self._get_service()

            attachment = service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            import base64
            data = attachment['data']
            return base64.urlsafe_b64decode(data)

        except HttpError as error:
            raise Exception(f"Failed to get attachment: {error}")

"""Divera 24/7 message API endpoints."""

from typing import TYPE_CHECKING

from divera247.client import Divera247Client
from divera247.models.alarm import SuccessResponse
from divera247.models.message import (
    MessageInput,
    MessageSingleResponse,
    MessagesResponse,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class MessageEndpoint:
    """Divera 24/7 message API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_messages(self) -> MessagesResponse:
        """Get all non-archived messages (GET /api/v2/messages)."""
        response = await self.client.get('v2/messages')
        return MessagesResponse.model_validate(response.json())

    async def create_message(self, payload: MessageInput) -> MessageSingleResponse:
        """Create a new message (POST /api/v2/messages)."""
        response = await self.client.post(
            'v2/messages',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return MessageSingleResponse.model_validate(response.json())

    async def get_message(self, message_id: int) -> MessageSingleResponse:
        """Get a single message by ID (GET /api/v2/messages/{id})."""
        response = await self.client.get(f'v2/messages/{message_id}')
        return MessageSingleResponse.model_validate(response.json())

    async def update_message(
        self,
        message_id: int,
        payload: MessageInput,
    ) -> MessageSingleResponse:
        """Update a message (PUT /api/v2/messages/{id})."""
        response = await self.client.put(
            f'v2/messages/{message_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return MessageSingleResponse.model_validate(response.json())

    async def delete_message(self, message_id: int) -> SuccessResponse:
        """Delete a message (DELETE /api/v2/messages/{id})."""
        response = await self.client.delete(f'v2/messages/{message_id}')
        return SuccessResponse.model_validate(response.json())

    async def archive_message(self, message_id: int) -> SuccessResponse:
        """Archive a message (POST /api/v2/messages/archive/{id})."""
        response = await self.client.post(f'v2/messages/archive/{message_id}')
        return SuccessResponse.model_validate(response.json())

    async def add_attachment(
        self,
        message_id: int,
        *,
        upload: bytes,
        title: str,
        description: str,
        filename: str = 'attachment',
    ) -> SuccessResponse:
        """Add an attachment to a message (POST /api/v2/messages/attachment/{id})."""
        files: Mapping[str, object] = {
            'Attachment[upload]': (filename, upload, 'application/octet-stream'),
        }
        data: Mapping[str, str] = {
            'Attachment[title]': title,
            'Attachment[description]': description,
        }
        response = await self.client.post_multipart(
            f'v2/messages/attachment/{message_id}',
            files=files,
            data=data,
        )
        return SuccessResponse.model_validate(response.json())

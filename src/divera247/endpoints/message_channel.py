"""Divera 24/7 message-channel API endpoints."""

from divera247.client import Divera247Client
from divera247.models.alarm import SuccessResponse
from divera247.models.message_channel import (
    MessageChannelActivityPayload,
    MessageChannelInput,
    MessageChannelNotificationPayload,
    MessageChannelSingleResponse,
    MessageChannelsResponse,
    MessageSortingResponse,
    MessagesResponse,
)


class MessageChannelEndpoint:
    """Divera 24/7 message-channel API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_message_channels(self) -> MessageChannelsResponse:
        """Get all non-archived channels (GET /api/v2/message-channels)."""
        response = await self.client.get('v2/message-channels')
        return MessageChannelsResponse.model_validate(response.json())

    async def create_message_channel(
        self,
        payload: MessageChannelInput,
    ) -> MessageChannelSingleResponse:
        """Create a new channel (POST /api/v2/message-channels)."""
        response = await self.client.post(
            'v2/message-channels',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return MessageChannelSingleResponse.model_validate(response.json())

    async def get_message_channel(
        self,
        channel_id: int,
    ) -> MessageChannelSingleResponse:
        """Get a single channel by ID (GET /api/v2/message-channels/{id})."""
        response = await self.client.get(f'v2/message-channels/{channel_id}')
        return MessageChannelSingleResponse.model_validate(response.json())

    async def update_message_channel(
        self,
        channel_id: int,
        payload: MessageChannelInput,
    ) -> MessageChannelSingleResponse:
        """Update a channel (PUT /api/v2/message-channels/{id})."""
        response = await self.client.put(
            f'v2/message-channels/{channel_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return MessageChannelSingleResponse.model_validate(response.json())

    async def delete_message_channel(
        self,
        channel_id: int,
    ) -> SuccessResponse:
        """Delete a channel (DELETE /api/v2/message-channels/{id})."""
        response = await self.client.delete(f'v2/message-channels/{channel_id}')
        return SuccessResponse.model_validate(response.json())

    async def get_messages(
        self,
        channel_id: int,
        *,
        first_message_id: int,
        parent_message_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> MessagesResponse:
        """Load messages for a channel (GET /api/v2/message-channels/messages/{id})."""
        params: dict[str, int] = {'first_message_id': first_message_id}
        if parent_message_id is not None:
            params['parent_message_id'] = parent_message_id
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        response = await self.client.get(
            f'v2/message-channels/messages/{channel_id}',
            params=params,
        )
        return MessagesResponse.model_validate(response.json())

    async def get_message_sorting(
        self,
        channel_id: int,
        *,
        parent_message_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> MessageSortingResponse:
        """Get message IDs and timestamps (GET /api/v2/message-channels/message-sorting/{id})."""
        params: dict[str, int] = {}
        if parent_message_id is not None:
            params['parent_message_id'] = parent_message_id
        if limit is not None:
            params['limit'] = limit
        if offset is not None:
            params['offset'] = offset
        response = await self.client.get(
            f'v2/message-channels/message-sorting/{channel_id}',
            params=params or None,
        )
        return MessageSortingResponse.model_validate(response.json())

    async def update_activity(
        self,
        channel_id: int,
        payload: MessageChannelActivityPayload,
    ) -> SuccessResponse:
        """Update last read message (POST /api/v2/message-channels/activity/{id})."""
        response = await self.client.post(
            f'v2/message-channels/activity/{channel_id}',
            data=payload.model_dump(by_alias=False),
        )
        return SuccessResponse.model_validate(response.json())

    async def update_notification_settings(
        self,
        channel_id: int,
        payload: MessageChannelNotificationPayload,
    ) -> SuccessResponse:
        """Update notification settings (POST /api/v2/message-channels/notification-settings/{id})."""
        response = await self.client.post(
            f'v2/message-channels/notification-settings/{channel_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return SuccessResponse.model_validate(response.json())

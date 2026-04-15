"""Message-channel API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.v2.endpoints import MessageChannelEndpoint
from divera247.v2.models.alarm import SuccessResponse
from divera247.v2.models.message_channel import (
    MessageChannelActivityPayload,
    MessageChannelInput,
    MessageChannelNotificationPayload,
    MessageChannelSingleResponse,
    MessageChannelsResponse,
    MessageSortingResponse,
    MessagesResponse,
)
from tests.v2._helpers import load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def message_channel_endpoint(api_client: Divera247Client) -> MessageChannelEndpoint:
    """Provide ``MessageChannelEndpoint`` using the shared mock client."""
    return MessageChannelEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_message-channels_request.json', MessageChannelInput),
        ('post_message-channels_response.json', MessageChannelSingleResponse),
        ('get_message-channels_response.json', MessageChannelsResponse),
        ('get_message-channels_id_response.json', MessageChannelSingleResponse),
        ('put_message-channels_id_request.json', MessageChannelInput),
        ('put_message-channels_id_response.json', MessageChannelSingleResponse),
        ('delete_message-channels_id_response.json', SuccessResponse),
        ('get_message-channels_messages_id_response.json', MessagesResponse),
        ('get_message-channels_message-sorting_id_response.json', MessageSortingResponse),
        ('post_message-channels_activity_id_request.json', MessageChannelActivityPayload),
        ('post_message-channels_activity_id_response.json', SuccessResponse),
        (
            'post_message-channels_notification-settings_id_request.json',
            MessageChannelNotificationPayload,
        ),
        ('post_message-channels_notification-settings_id_response.json', SuccessResponse),
    ],
)
def test_message_channel_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('message-channel', filename))


async def test_get_message_channels(
    message_channel_endpoint: MessageChannelEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET message channels returns success."""
    httpx_mock.add_response(json=load_v2_json('message-channel', 'get_message-channels_response.json'))
    response = await message_channel_endpoint.get_message_channels()
    assert response.success is True

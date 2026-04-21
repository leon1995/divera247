"""Message API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.endpoints import MessageEndpoint
from divera247.models.alarm import SuccessResponse
from divera247.models.message import MessageInput, MessageSingleResponse, MessagesResponse
from tests._helpers import load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def message_endpoint(api_client: Divera247Client) -> MessageEndpoint:
    """Provide ``MessageEndpoint`` using the shared mock client."""
    return MessageEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_messages_request.json', MessageInput),
        ('post_messages_response.json', MessageSingleResponse),
        ('get_messages_response.json', MessagesResponse),
        ('get_messages_id_response.json', MessageSingleResponse),
        ('put_messages_id_request.json', MessageInput),
        ('put_messages_id_response.json', MessageSingleResponse),
        ('delete_messages_id_response.json', SuccessResponse),
        ('post_messages_archive_id_response.json', SuccessResponse),
        ('post_messages_attachment_id_response.json', SuccessResponse),
    ],
)
def test_message_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('message', filename))


async def test_get_messages(
    message_endpoint: MessageEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET messages returns success."""
    httpx_mock.add_response(json=load_v2_json('message', 'get_messages_response.json'))
    response = await message_endpoint.get_messages()
    assert response.success is True

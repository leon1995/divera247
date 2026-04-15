"""Event API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from pydantic import BaseModel
from tests.v2._helpers import EXAMPLE_ID, load_v2_json

from divera247.client import Divera247Client
from divera247.v2.endpoints import EventEndpoint
from divera247.v2.models.alarm import SuccessResponse
from divera247.v2.models.event import (
    EventConfirmPayload,
    EventInput,
    EventSingleResponse,
    EventsResponse,
    ReachResponse,
)


@pytest.fixture
def event_endpoint(api_client: Divera247Client) -> EventEndpoint:
    return EventEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_events_request.json', EventInput),
        ('post_events_response.json', EventSingleResponse),
        ('get_events_response.json', EventsResponse),
        ('get_events_id_response.json', EventSingleResponse),
        ('put_events_id_request.json', EventInput),
        ('put_events_id_response.json', EventSingleResponse),
        ('delete_events_id_response.json', SuccessResponse),
        ('post_events_confirm_id_request.json', EventConfirmPayload),
        ('post_events_confirm_id_response.json', SuccessResponse),
        ('post_events_read_id_response.json', SuccessResponse),
        ('post_events_archive_id_response.json', SuccessResponse),
        ('post_events_attachment_id_response.json', SuccessResponse),
        ('get_events_reach_id_response.json', ReachResponse),
        ('get_events_download_id_response.json', SuccessResponse),
        ('delete_events_reset-responses_id_response.json', SuccessResponse),
    ],
)
def test_event_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    model.model_validate(load_v2_json('event', filename))


async def test_get_events(event_endpoint: EventEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    httpx_mock.add_response(json=load_v2_json('event', 'get_events_response.json'))
    response = await event_endpoint.get_events()
    assert response.success is True
    assert response.data is not None


async def test_download_event(event_endpoint: EventEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    payload = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'
    httpx_mock.add_response(content=payload)
    content = await event_endpoint.download_event(EXAMPLE_ID)
    assert content == payload

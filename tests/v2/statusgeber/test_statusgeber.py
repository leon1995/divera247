"""Statusgeber API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from pydantic import BaseModel
from tests.v2._helpers import load_v2_json

from divera247.client import Divera247Client
from divera247.v2.endpoints import StatusgeberEndpoint
from divera247.v2.models.statusgeber import StatusgeberPayload


@pytest.fixture
def statusgeber_endpoint(api_client: Divera247Client) -> StatusgeberEndpoint:
    return StatusgeberEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_statusgeber_set-status_request.json', StatusgeberPayload),
    ],
)
def test_statusgeber_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    model.model_validate(load_v2_json('statusgeber', filename))


async def test_set_status(
    statusgeber_endpoint: StatusgeberEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    payload = StatusgeberPayload.model_validate(
        load_v2_json('statusgeber', 'post_statusgeber_set-status_request.json'),
    )
    httpx_mock.add_response(json=load_v2_json('statusgeber', 'post_statusgeber_set-status_response.json'))
    response = await statusgeber_endpoint.set_status(payload)
    assert response is None

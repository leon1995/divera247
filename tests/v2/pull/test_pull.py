"""Pull API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from pydantic import BaseModel
from tests.v2._helpers import load_v2_json

from divera247.client import Divera247Client
from divera247.v2.endpoints.pull import PullEndpoint
from divera247.v2.models.pull import PullAllResponse, VehicleStatusResponse


@pytest.fixture
def pull_endpoint(api_client: Divera247Client) -> PullEndpoint:
    return PullEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('get_pull_all_response.json', PullAllResponse),
        ('get_pull_vehicle-status_response.json', VehicleStatusResponse),
    ],
)
def test_pull_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    model.model_validate(load_v2_json('pull', filename))


async def test_get_all(pull_endpoint: PullEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    httpx_mock.add_response(json=load_v2_json('pull', 'get_pull_all_response.json'))
    response = await pull_endpoint.get_all()
    assert response.success is True

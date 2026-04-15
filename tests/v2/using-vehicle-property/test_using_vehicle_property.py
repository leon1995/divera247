"""Using-vehicle-property API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from pydantic import BaseModel
from tests.v2._helpers import EXAMPLE_ID, load_v2_json

from divera247.client import Divera247Client
from divera247.v2.endpoints.using_vehicle_property import UsingVehiclePropertyEndpoint
from divera247.v2.models.using_vehicle_property import UsingVehiclePropertyPayload


@pytest.fixture
def using_vehicle_property_endpoint(api_client: Divera247Client) -> UsingVehiclePropertyEndpoint:
    return UsingVehiclePropertyEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_using-vehicle-property_set_id_request.json', UsingVehiclePropertyPayload),
    ],
)
def test_using_vehicle_property_fixture_parses(
    filename: str,
    model: type[BaseModel],
) -> None:
    model.model_validate(load_v2_json('using-vehicle-property', filename))


async def test_get_properties(
    using_vehicle_property_endpoint: UsingVehiclePropertyEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    httpx_mock.add_response(
        json=load_v2_json('using-vehicle-property', 'get_using-vehicle-property_get_id_response.json')
    )
    response = await using_vehicle_property_endpoint.get_properties(EXAMPLE_ID)
    assert isinstance(response, dict)

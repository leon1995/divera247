"""Using-vehicle-property API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.endpoints import UsingVehiclePropertyEndpoint
from divera247.models.using_vehicle_property import UsingVehiclePropertyPayload
from tests._helpers import EXAMPLE_ID, load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def using_vehicle_property_endpoint(api_client: Divera247Client) -> UsingVehiclePropertyEndpoint:
    """Provide ``UsingVehiclePropertyEndpoint`` using the shared mock client."""
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
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('using-vehicle-property', filename))


async def test_get_properties(
    using_vehicle_property_endpoint: UsingVehiclePropertyEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET vehicle properties returns a mapping."""
    httpx_mock.add_response(
        json=load_v2_json('using-vehicle-property', 'get_using-vehicle-property_get_id_response.json')
    )
    response = await using_vehicle_property_endpoint.get_properties(EXAMPLE_ID)
    assert isinstance(response, dict)

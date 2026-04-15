"""Using-vehicle API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.v2.endpoints import UsingVehicleEndpoint
from divera247.v2.models.using_vehicle import (
    UsingVehicleBulkPayload,
    UsingVehicleBulkResponse,
    UsingVehicleSetStatusPayload,
)
from tests.v2._helpers import EXAMPLE_ID, load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def using_vehicle_endpoint(api_client: Divera247Client) -> UsingVehicleEndpoint:
    """Provide ``UsingVehicleEndpoint`` using the shared mock client."""
    return UsingVehicleEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_using-vehicles_set-status_id_request.json', UsingVehicleSetStatusPayload),
        ('post_using-vehicles_set-status-bulk_request.json', UsingVehicleBulkPayload),
        ('post_using-vehicles_set-status-bulk_response.json', UsingVehicleBulkResponse),
    ],
)
def test_using_vehicle_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('using-vehicle', filename))


async def test_get_status(
    using_vehicle_endpoint: UsingVehicleEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET using-vehicle status returns a mapping."""
    httpx_mock.add_response(json=load_v2_json('using-vehicle', 'get_using-vehicles_get-status_id_response.json'))
    response = await using_vehicle_endpoint.get_status(EXAMPLE_ID)
    assert isinstance(response, dict)

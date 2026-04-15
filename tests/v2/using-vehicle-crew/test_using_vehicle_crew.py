"""Using-vehicle-crew API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from pydantic import BaseModel
from tests.v2._helpers import EXAMPLE_ID, load_v2_json

from divera247.client import Divera247Client
from divera247.v2.endpoints.using_vehicle_crew import UsingVehicleCrewEndpoint
from divera247.v2.models.using_vehicle_crew import UsingVehicleCrewPayload


@pytest.fixture
def using_vehicle_crew_endpoint(api_client: Divera247Client) -> UsingVehicleCrewEndpoint:
    return UsingVehicleCrewEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_using-vehicle-crew_add_id_request.json', UsingVehicleCrewPayload),
        ('post_using-vehicle-crew_remove_id_request.json', UsingVehicleCrewPayload),
    ],
)
def test_using_vehicle_crew_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    model.model_validate(load_v2_json('using-vehicle-crew', filename))


async def test_add_crew(
    using_vehicle_crew_endpoint: UsingVehicleCrewEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    payload = UsingVehicleCrewPayload.model_validate(
        load_v2_json('using-vehicle-crew', 'post_using-vehicle-crew_add_id_request.json'),
    )
    httpx_mock.add_response(json=load_v2_json('using-vehicle-crew', 'post_using-vehicle-crew_add_id_response.json'))
    response = await using_vehicle_crew_endpoint.add_crew(EXAMPLE_ID, payload)
    assert response is None

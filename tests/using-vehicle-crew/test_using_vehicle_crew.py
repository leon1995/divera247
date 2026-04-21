"""Using-vehicle-crew API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.endpoints import UsingVehicleCrewEndpoint
from divera247.models.using_vehicle_crew import UsingVehicleCrewPayload
from tests._helpers import EXAMPLE_ID, load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def using_vehicle_crew_endpoint(api_client: Divera247Client) -> UsingVehicleCrewEndpoint:
    """Provide ``UsingVehicleCrewEndpoint`` using the shared mock client."""
    return UsingVehicleCrewEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_using-vehicle-crew_add_id_request.json', UsingVehicleCrewPayload),
        ('post_using-vehicle-crew_remove_id_request.json', UsingVehicleCrewPayload),
    ],
)
def test_using_vehicle_crew_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('using-vehicle-crew', filename))


async def test_add_crew(
    using_vehicle_crew_endpoint: UsingVehicleCrewEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST add crew returns empty body (None)."""
    payload = UsingVehicleCrewPayload.model_validate(
        load_v2_json('using-vehicle-crew', 'post_using-vehicle-crew_add_id_request.json'),
    )
    httpx_mock.add_response(json=load_v2_json('using-vehicle-crew', 'post_using-vehicle-crew_add_id_response.json'))
    response = await using_vehicle_crew_endpoint.add_crew(EXAMPLE_ID, payload)
    assert response is None

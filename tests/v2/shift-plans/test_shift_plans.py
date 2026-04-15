"""Shift plans API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.v2.endpoints import ShiftPlansEndpoint
from divera247.v2.models.shift_plans import ShiftPlanItem
from tests.v2._helpers import load_v2_json

if TYPE_CHECKING:
    import pytest_httpx

    from divera247.client import Divera247Client


@pytest.fixture
def shift_plans_endpoint(api_client: Divera247Client) -> ShiftPlansEndpoint:
    """Provide ``ShiftPlansEndpoint`` using the shared mock client."""
    return ShiftPlansEndpoint(api_client)


def test_shift_plans_fixture_parses() -> None:
    """List response JSON must parse each element as ``ShiftPlanItem``."""
    data = load_v2_json('shift-plans', 'get_shift-plans_response.json')
    assert isinstance(data, list)
    for item in data:
        ShiftPlanItem.model_validate(item)


async def test_get_shift_plans(
    shift_plans_endpoint: ShiftPlansEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET shift plans returns a non-empty list."""
    httpx_mock.add_response(json=load_v2_json('shift-plans', 'get_shift-plans_response.json'))
    response = await shift_plans_endpoint.get_shift_plans()
    assert len(response) >= 1

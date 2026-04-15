"""Dashboard API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.v2.endpoints import DashboardEndpoint
from divera247.v2.models.alarm import SuccessResponse
from divera247.v2.models.dashboard import (
    DashboardInput,
    DashboardSingleResponse,
    DashboardsResponse,
)
from tests.v2._helpers import load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def dashboard_endpoint(api_client: Divera247Client) -> DashboardEndpoint:
    """Provide ``DashboardEndpoint`` using the shared mock client."""
    return DashboardEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_dashboards_request.json', DashboardInput),
        ('post_dashboards_response.json', DashboardSingleResponse),
        ('get_dashboards_response.json', DashboardsResponse),
        ('get_dashboards_id_response.json', DashboardSingleResponse),
        ('put_dashboards_id_request.json', DashboardInput),
        ('put_dashboards_id_response.json', DashboardSingleResponse),
        ('delete_dashboards_id_response.json', SuccessResponse),
    ],
)
def test_dashboard_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('dashboard', filename))


async def test_get_dashboards(
    dashboard_endpoint: DashboardEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET dashboards returns success."""
    httpx_mock.add_response(json=load_v2_json('dashboard', 'get_dashboards_response.json'))
    response = await dashboard_endpoint.get_dashboards()
    assert response.success is True

"""Divera 24/7 dashboard API endpoints."""

from divera247.client import Divera247Client
from divera247.models.alarm import SuccessResponse
from divera247.models.dashboard import (
    DashboardInput,
    DashboardSingleResponse,
    DashboardsResponse,
)


class DashboardEndpoint:
    """Divera 24/7 dashboard API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_dashboards(self) -> DashboardsResponse:
        """Get all dashboards (GET /api/v2/dashboards)."""
        response = await self.client.get('v2/dashboards')
        return DashboardsResponse.model_validate(response.json())

    async def create_dashboard(
        self,
        payload: DashboardInput,
    ) -> DashboardSingleResponse:
        """Create a new dashboard (POST /api/v2/dashboards)."""
        response = await self.client.post(
            'v2/dashboards',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return DashboardSingleResponse.model_validate(response.json())

    async def get_dashboard(self, dashboard_id: int) -> DashboardSingleResponse:
        """Get a single dashboard by ID (GET /api/v2/dashboards/{id})."""
        response = await self.client.get(f'v2/dashboards/{dashboard_id}')
        return DashboardSingleResponse.model_validate(response.json())

    async def update_dashboard(
        self,
        dashboard_id: int,
        payload: DashboardInput,
    ) -> DashboardSingleResponse:
        """Update a dashboard (PUT /api/v2/dashboards/{id})."""
        response = await self.client.put(
            f'v2/dashboards/{dashboard_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return DashboardSingleResponse.model_validate(response.json())

    async def delete_dashboard(self, dashboard_id: int) -> SuccessResponse:
        """Delete a dashboard (DELETE /api/v2/dashboards/{id})."""
        response = await self.client.delete(f'v2/dashboards/{dashboard_id}')
        return SuccessResponse.model_validate(response.json())

"""Divera 24/7 using-vehicle-crew API endpoints."""

from divera247.client import Divera247Client
from divera247.v2.models.using_vehicle_crew import UsingVehicleCrewPayload


class UsingVehicleCrewEndpoint:
    """Divera 24/7 using-vehicle-crew API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def add_crew(
        self,
        vehicle_id: int,
        payload: UsingVehicleCrewPayload,
    ) -> None:
        """Add users to vehicle (POST /api/v2/using-vehicle-crew/add/{id})."""
        await self.client.post(
            f'v2/using-vehicle-crew/add/{vehicle_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )

    async def remove_crew(
        self,
        vehicle_id: int,
        payload: UsingVehicleCrewPayload,
    ) -> None:
        """Remove users from vehicle (POST /api/v2/using-vehicle-crew/remove/{id})."""
        await self.client.post(
            f'v2/using-vehicle-crew/remove/{vehicle_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )

    async def reset_crew(self, vehicle_id: int) -> None:
        """Reset vehicle crew (DELETE /api/v2/using-vehicle-crew/reset/{id})."""
        await self.client.delete(f'v2/using-vehicle-crew/reset/{vehicle_id}')

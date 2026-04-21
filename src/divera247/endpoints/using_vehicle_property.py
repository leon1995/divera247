"""Divera 24/7 using-vehicle-property API endpoints."""

from divera247.client import Divera247Client
from divera247.models.using_vehicle_property import UsingVehiclePropertyPayload


class UsingVehiclePropertyEndpoint:
    """Divera 24/7 using-vehicle-property API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_properties(self, vehicle_id: int) -> object:
        """Get vehicle properties (GET /api/v2/using-vehicle-property/get/{id})."""
        response = await self.client.get(
            f'v2/using-vehicle-property/get/{vehicle_id}',
        )
        return response.json()

    async def set_properties(
        self,
        vehicle_id: int,
        payload: UsingVehiclePropertyPayload,
    ) -> None:
        """Set vehicle properties (POST /api/v2/using-vehicle-property/set/{id})."""
        await self.client.post(
            f'v2/using-vehicle-property/set/{vehicle_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )

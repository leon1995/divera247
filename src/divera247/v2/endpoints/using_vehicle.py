"""Divera 24/7 using-vehicle API endpoints."""

from divera247.client import Divera247Client
from divera247.v2.models.using_vehicle import (
    UsingVehicleBulkPayload,
    UsingVehicleBulkResponse,
    UsingVehicleSetStatusPayload,
)


class UsingVehicleEndpoint:
    """Divera 24/7 using-vehicle API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_status(self, vehicle_id: int) -> object:
        """Get vehicle status (GET /api/v2/using-vehicles/get-status/{id})."""
        response = await self.client.get(
            f'v2/using-vehicles/get-status/{vehicle_id}',
        )
        return response.json()

    async def set_status(
        self,
        vehicle_id: int,
        payload: UsingVehicleSetStatusPayload,
    ) -> None:
        """Set vehicle status (POST /api/v2/using-vehicles/set-status/{id})."""
        await self.client.post(
            f'v2/using-vehicles/set-status/{vehicle_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )

    async def set_status_bulk(
        self,
        payload: UsingVehicleBulkPayload,
    ) -> UsingVehicleBulkResponse:
        """Set status for multiple vehicles (POST /api/v2/using-vehicles/set-status-bulk)."""
        response = await self.client.post(
            'v2/using-vehicles/set-status-bulk',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return UsingVehicleBulkResponse.model_validate(response.json())

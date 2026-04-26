"""Divera 24/7 statusgeber API endpoints."""

from divera247.client import Divera247Client
from divera247.models.statusgeber import StatusgeberPayload


class StatusgeberEndpoint:
    """Divera 24/7 statusgeber API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def set_status(self, payload: StatusgeberPayload) -> None:
        """Set status (POST /api/v2/statusgeber/set-status)."""
        await self.client.post(
            'v2/statusgeber/set-status',
            data=payload.model_dump(mode='json', by_alias=False, exclude_none=True),
        )

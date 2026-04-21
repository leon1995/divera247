"""Divera 24/7 pull API endpoints."""

from divera247.client import Divera247Client
from divera247.models.pull import PullAllResponse, VehicleStatusResponse


class PullEndpoint:
    """Divera 24/7 pull API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_all(  # noqa: C901, PLR0913
        self,
        *,
        ucr: int | None = None,
        ts_user: int | None = None,
        ts_alarm: int | None = None,
        ts_news: int | None = None,
        ts_event: int | None = None,
        ts_status: int | None = None,
        ts_statusplan: int | None = None,
        ts_cluster: int | None = None,
        ts_localmonitor: int | None = None,
        ts_monitor: int | None = None,
    ) -> PullAllResponse:
        """Get all data (GET /api/v2/pull/all)."""
        params: dict[str, int] = {}
        if ucr is not None:
            params['ucr'] = ucr
        if ts_user is not None:
            params['ts_user'] = ts_user
        if ts_alarm is not None:
            params['ts_alarm'] = ts_alarm
        if ts_news is not None:
            params['ts_news'] = ts_news
        if ts_event is not None:
            params['ts_event'] = ts_event
        if ts_status is not None:
            params['ts_status'] = ts_status
        if ts_statusplan is not None:
            params['ts_statusplan'] = ts_statusplan
        if ts_cluster is not None:
            params['ts_cluster'] = ts_cluster
        if ts_localmonitor is not None:
            params['ts_localmonitor'] = ts_localmonitor
        if ts_monitor is not None:
            params['ts_monitor'] = ts_monitor
        response = await self.client.get(
            'v2/pull/all',
            params=params or None,
        )
        return PullAllResponse.model_validate(response.json())

    async def get_vehicle_status(self) -> VehicleStatusResponse:
        """Get vehicle status (GET /api/v2/pull/vehicle-status)."""
        response = await self.client.get('v2/pull/vehicle-status')
        return VehicleStatusResponse.model_validate(response.json())

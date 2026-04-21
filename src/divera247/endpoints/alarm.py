"""Divera 24/7 alarm API endpoints."""

from typing import TYPE_CHECKING, Any

from divera247.client import Divera247Client
from divera247.models.alarm import (
    AlarmInput,
    AlarmSingleResponse,
    AlarmsListResponse,
    AlarmsResponse,
    CloseAlarmPayload,
    ConfirmPayload,
    ReachResponse,
    SuccessResponse,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class AlarmEndpoint:
    """Divera 24/7 alarm API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_alarms(self) -> AlarmsResponse:
        """Get all non-archived alarms (GET /api/v2/alarms)."""
        response = await self.client.get('v2/alarms')
        return AlarmsResponse.model_validate(response.json())

    async def create_alarm(self, payload: AlarmInput) -> AlarmSingleResponse:
        """Create a new alarm (POST /api/v2/alarms)."""
        response = await self.client.post(
            'v2/alarms',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return AlarmSingleResponse.model_validate(response.json())

    async def get_alarms_list(
        self,
        closed: int | None = None,
    ) -> AlarmsListResponse:
        """Get all alarms, optionally filtered (GET /api/v2/alarms/list).

        :param closed: If 0, only non-closed alarms are returned.
        """
        params: dict[str, Any] = {}
        if closed is not None:
            params['closed'] = closed
        response = await self.client.get(
            'v2/alarms/list',
            params=params or None,
        )
        return AlarmsListResponse.model_validate(response.json())

    async def get_alarm(self, alarm_id: int) -> AlarmSingleResponse:
        """Get a single alarm by ID (GET /api/v2/alarms/{id})."""
        response = await self.client.get(f'v2/alarms/{alarm_id}')
        return AlarmSingleResponse.model_validate(response.json())

    async def update_alarm(
        self,
        alarm_id: int,
        payload: AlarmInput,
    ) -> AlarmSingleResponse:
        """Update an alarm (PUT /api/v2/alarms/{id})."""
        response = await self.client.put(
            f'v2/alarms/{alarm_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return AlarmSingleResponse.model_validate(response.json())

    async def delete_alarm(self, alarm_id: int) -> SuccessResponse:
        """Delete an alarm (DELETE /api/v2/alarms/{id})."""
        response = await self.client.delete(f'v2/alarms/{alarm_id}')
        return SuccessResponse.model_validate(response.json())

    async def add_attachment(
        self,
        alarm_id: int,
        *,
        upload: bytes,
        title: str,
        description: str,
        filename: str = 'attachment',
    ) -> SuccessResponse:
        """Add an attachment to an alarm (POST /api/v2/alarms/attachment/{id}).

        :param alarm_id: Alarm ID.
        :param upload: File content as bytes.
        :param title: Attachment title.
        :param description: Attachment description.
        :param filename: Filename for the upload (default: attachment).
        """
        files: Mapping[str, Any] = {
            'Attachment[upload]': (filename, upload, 'application/octet-stream'),
        }
        data: Mapping[str, str] = {
            'Attachment[title]': title,
            'Attachment[description]': description,
        }
        response = await self.client.post_multipart(
            f'v2/alarms/attachment/{alarm_id}',
            files=files,
            data=data,
        )
        return SuccessResponse.model_validate(response.json())

    async def archive_alarm(self, alarm_id: int) -> SuccessResponse:
        """Archive an alarm (POST /api/v2/alarms/archive/{id})."""
        response = await self.client.post(f'v2/alarms/archive/{alarm_id}')
        return SuccessResponse.model_validate(response.json())

    async def confirm_alarm(
        self,
        alarm_id: int,
        payload: ConfirmPayload,
    ) -> SuccessResponse:
        """Create a response to an alarm (POST /api/v2/alarms/confirm/{id})."""
        response = await self.client.post(
            f'v2/alarms/confirm/{alarm_id}',
            data=payload.model_dump(by_alias=False),
        )
        return SuccessResponse.model_validate(response.json())

    async def read_alarm(self, alarm_id: int) -> SuccessResponse:
        """Mark an alarm as read (POST /api/v2/alarms/read/{id})."""
        response = await self.client.post(f'v2/alarms/read/{alarm_id}')
        return SuccessResponse.model_validate(response.json())

    async def close_alarm(
        self,
        alarm_id: int,
        payload: CloseAlarmPayload | None = None,
    ) -> SuccessResponse:
        """Close an alarm (POST /api/v2/alarms/close/{id})."""
        data = payload.model_dump(by_alias=False, exclude_none=True) if payload else None
        response = await self.client.post(
            f'v2/alarms/close/{alarm_id}',
            data=data,
        )
        return SuccessResponse.model_validate(response.json())

    async def get_alarm_reach(self, alarm_id: int) -> ReachResponse:
        """Get alarm reach stats (GET /api/v2/alarms/reach/{id})."""
        response = await self.client.get(f'v2/alarms/reach/{alarm_id}')
        return ReachResponse.model_validate(response.json())

    async def download_alarm(self, alarm_id: int) -> bytes:
        """Download alarm as PDF (GET /api/v2/alarms/download/{id}).

        Returns the raw PDF bytes.
        """
        response = await self.client.get(f'v2/alarms/download/{alarm_id}')
        return response.content

    async def reset_responses(self, alarm_id: int) -> SuccessResponse:
        """Reset responses for an alarm (DELETE /api/v2/alarms/reset-responses/{id})."""
        response = await self.client.delete(
            f'v2/alarms/reset-responses/{alarm_id}',
        )
        return SuccessResponse.model_validate(response.json())

"""Divera 24/7 event API endpoints."""

from typing import TYPE_CHECKING

from divera247.client import Divera247Client
from divera247.v2.models.alarm import SuccessResponse
from divera247.v2.models.event import (
    EventConfirmPayload,
    EventInput,
    EventSingleResponse,
    EventsResponse,
    ReachResponse,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class EventEndpoint:
    """Divera 24/7 event API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_events(self) -> EventsResponse:
        """Get all non-archived events (GET /api/v2/events)."""
        response = await self.client.get('v2/events')
        return EventsResponse.model_validate(response.json())

    async def create_event(self, payload: EventInput) -> EventSingleResponse:
        """Create a new event (POST /api/v2/events)."""
        response = await self.client.post(
            'v2/events',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return EventSingleResponse.model_validate(response.json())

    async def get_event(self, event_id: int) -> EventSingleResponse:
        """Get a single event by ID (GET /api/v2/events/{id})."""
        response = await self.client.get(f'v2/events/{event_id}')
        return EventSingleResponse.model_validate(response.json())

    async def update_event(
        self,
        event_id: int,
        payload: EventInput,
    ) -> EventSingleResponse:
        """Update an event (PUT /api/v2/events/{id})."""
        response = await self.client.put(
            f'v2/events/{event_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return EventSingleResponse.model_validate(response.json())

    async def delete_event(self, event_id: int) -> SuccessResponse:
        """Delete an event (DELETE /api/v2/events/{id})."""
        response = await self.client.delete(f'v2/events/{event_id}')
        return SuccessResponse.model_validate(response.json())

    async def add_attachment(
        self,
        event_id: int,
        *,
        upload: bytes,
        title: str,
        description: str,
        filename: str = 'attachment',
    ) -> SuccessResponse:
        """Add an attachment to an event (POST /api/v2/events/attachment/{id})."""
        files: Mapping[str, object] = {
            'Attachment[upload]': (filename, upload, 'application/octet-stream'),
        }
        data: Mapping[str, str] = {
            'Attachment[title]': title,
            'Attachment[description]': description,
        }
        response = await self.client.post_multipart(
            f'v2/events/attachment/{event_id}',
            files=files,
            data=data,
        )
        return SuccessResponse.model_validate(response.json())

    async def archive_event(self, event_id: int) -> SuccessResponse:
        """Archive an event (POST /api/v2/events/archive/{id})."""
        response = await self.client.post(f'v2/events/archive/{event_id}')
        return SuccessResponse.model_validate(response.json())

    async def confirm_event(
        self,
        event_id: int,
        payload: EventConfirmPayload | None = None,
    ) -> SuccessResponse:
        """Create a response to an event (POST /api/v2/events/confirm/{id})."""
        data = payload.model_dump(by_alias=False, exclude_none=True) if payload else None
        response = await self.client.post(
            f'v2/events/confirm/{event_id}',
            data=data,
        )
        return SuccessResponse.model_validate(response.json())

    async def read_event(self, event_id: int) -> SuccessResponse:
        """Mark an event as read (POST /api/v2/events/read/{id})."""
        response = await self.client.post(f'v2/events/read/{event_id}')
        return SuccessResponse.model_validate(response.json())

    async def get_event_reach(self, event_id: int) -> ReachResponse:
        """Get event reach stats (GET /api/v2/events/reach/{id})."""
        response = await self.client.get(f'v2/events/reach/{event_id}')
        return ReachResponse.model_validate(response.json())

    async def download_event(self, event_id: int) -> bytes:
        """Download event as PDF (GET /api/v2/events/download/{id})."""
        response = await self.client.get(f'v2/events/download/{event_id}')
        return response.content

    async def get_events_ics(self) -> bytes:
        """Download own events as ICS (GET /api/v2/events/ics)."""
        response = await self.client.get('v2/events/ics')
        return response.content

    async def reset_responses(self, event_id: int) -> SuccessResponse:
        """Reset all participation responses (DELETE /api/v2/events/reset-responses/{id})."""
        response = await self.client.delete(
            f'v2/events/reset-responses/{event_id}',
        )
        return SuccessResponse.model_validate(response.json())

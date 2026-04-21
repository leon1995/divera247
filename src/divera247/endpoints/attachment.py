"""Divera 24/7 attachment API endpoints."""

from divera247.client import Divera247Client
from divera247.models.alarm import SuccessResponse
from divera247.models.attachment import (
    AttachmentSingleResponse,
    AttachmentsResponse,
)


class AttachmentEndpoint:
    """Divera 24/7 attachment API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_attachments(self) -> AttachmentsResponse:
        """Get metadata of all attachments (GET /api/v2/attachments).

        File download is available under /api/v2/file/open/{id}.
        """
        response = await self.client.get('v2/attachments')
        return AttachmentsResponse.model_validate(response.json())

    async def get_attachment(self, attachment_id: int) -> AttachmentSingleResponse:
        """Get metadata of a single attachment (GET /api/v2/attachments/{id})."""
        response = await self.client.get(f'v2/attachments/{attachment_id}')
        return AttachmentSingleResponse.model_validate(response.json())

    async def delete_attachment(self, attachment_id: int) -> SuccessResponse:
        """Delete an attachment including its file (DELETE /api/v2/attachments/{id})."""
        response = await self.client.delete(f'v2/attachments/{attachment_id}')
        return SuccessResponse.model_validate(response.json())

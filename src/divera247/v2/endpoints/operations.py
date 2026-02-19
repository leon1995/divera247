"""Divera 24/7 operations API endpoints."""

from collections.abc import Sequence

from divera247.client import Divera247Client
from divera247.v2.models.operations import (
    Operation,
    OperationFile,
    OperationFileResponse,
    OperationResponse,
    OperationRicItem,
)


class OperationsEndpoint:
    """Divera 24/7 operations API endpoints (Leitstellen)."""

    def __init__(self, client: Divera247Client):
        self.client = client

    def _params(self, foreign_id: str | None) -> dict[str, str] | None:
        return {'foreign_id': foreign_id} if foreign_id else None

    async def get_operation(self, foreign_id: str) -> OperationResponse:
        """Get operation by foreign_id (GET /api/v2/operations)."""
        response = await self.client.get(
            'v2/operations',
            params={'foreign_id': foreign_id},
        )
        return OperationResponse.model_validate(response.json())

    async def get_operations(self) -> Sequence[OperationResponse]:
        """Get all running operations (GET /api/v2/operations)."""
        response = await self.client.get('v2/operations')
        data = response.json()
        return [OperationResponse.model_validate(op) for op in data]

    async def create_or_update_operation(
        self,
        payload: Operation,
    ) -> OperationResponse:
        """Create or update operation (POST /api/v2/operations)."""
        response = await self.client.post(
            'v2/operations',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return OperationResponse.model_validate(response.json())

    async def get_attachments_by_foreign_id(
        self,
        foreign_id: str,
    ) -> Sequence[OperationFileResponse]:
        """Get attachments (GET /api/v2/operations/attachments)."""
        response = await self.client.get(
            'v2/operations/attachments',
            params={'foreign_id': foreign_id},
        )
        return [OperationFileResponse.model_validate(f) for f in response.json()]

    async def add_attachment_by_foreign_id(
        self,
        foreign_id: str,
        payload: OperationFile,
    ) -> OperationFileResponse:
        """Add attachment (POST /api/v2/operations/attachments)."""
        response = await self.client.post(
            'v2/operations/attachments',
            data=payload.model_dump(by_alias=False, exclude_none=True),
            params={'foreign_id': foreign_id},
        )
        return OperationFileResponse.model_validate(response.json())

    async def replace_attachments_by_foreign_id(
        self,
        foreign_id: str,
        payload: Sequence[OperationFile],
    ) -> Sequence[OperationFileResponse]:
        """Replace attachments (PUT /api/v2/operations/attachments)."""
        data = [p.model_dump(by_alias=False, exclude_none=True) for p in payload]
        response = await self.client.put(
            'v2/operations/attachments',
            data=data,
            params={'foreign_id': foreign_id},
        )
        return [OperationFileResponse.model_validate(f) for f in response.json()]

    async def get_attachments(
        self,
        operation_id: int | str,
    ) -> Sequence[OperationFileResponse]:
        """Get attachments (GET /api/v2/operations/{id}/attachments)."""
        response = await self.client.get(
            f'v2/operations/{operation_id}/attachments',
        )
        return [OperationFileResponse.model_validate(f) for f in response.json()]

    async def add_attachment(
        self,
        operation_id: int | str,
        payload: OperationFile,
    ) -> OperationFileResponse:
        """Add attachment (POST /api/v2/operations/{id}/attachments)."""
        response = await self.client.post(
            f'v2/operations/{operation_id}/attachments',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return OperationFileResponse.model_validate(response.json())

    async def replace_attachments(
        self,
        operation_id: int | str,
        payload: Sequence[OperationFile],
    ) -> Sequence[OperationFileResponse]:
        """Replace attachments (PUT /api/v2/operations/{id}/attachments)."""
        data = [p.model_dump(by_alias=False, exclude_none=True) for p in payload]
        response = await self.client.put(
            f'v2/operations/{operation_id}/attachments',
            data=data,
        )
        return [OperationFileResponse.model_validate(f) for f in response.json()]

    async def get_attachment(
        self,
        operation_id: int | str,
        attachment_id: int,
    ) -> OperationFileResponse:
        """Get single attachment (GET /api/v2/operations/{id}/attachments/{attachmentId})."""
        response = await self.client.get(
            f'v2/operations/{operation_id}/attachments/{attachment_id}',
        )
        return OperationFileResponse.model_validate(response.json())

    async def delete_attachment(
        self,
        operation_id: int | str,
        attachment_id: int,
    ) -> None:
        """Delete attachment (DELETE /api/v2/operations/{id}/attachments/{attachmentId})."""
        await self.client.delete(
            f'v2/operations/{operation_id}/attachments/{attachment_id}',
        )

    async def get_ric(self, foreign_id: str) -> Sequence[OperationRicItem]:
        """Get assigned RICs (GET /api/v2/operations/ric)."""
        response = await self.client.get(
            'v2/operations/ric',
            params={'foreign_id': foreign_id},
        )
        return [OperationRicItem.model_validate(r) for r in response.json()]

    async def add_ric(
        self,
        foreign_id: str,
        payload: Sequence[OperationRicItem],
    ) -> Sequence[OperationRicItem]:
        """Add RICs (POST /api/v2/operations/ric)."""
        data = [p.model_dump(by_alias=False, exclude_none=True) for p in payload]
        response = await self.client.post(
            'v2/operations/ric',
            data=data,
            params={'foreign_id': foreign_id},
        )
        return [OperationRicItem.model_validate(r) for r in response.json()]

    async def put_ric(
        self,
        foreign_id: str,
        payload: Sequence[OperationRicItem],
    ) -> Sequence[OperationRicItem]:
        """Replace RICs (PUT /api/v2/operations/ric)."""
        data = [p.model_dump(by_alias=False, exclude_none=True) for p in payload]
        response = await self.client.put(
            'v2/operations/ric',
            data=data,
            params={'foreign_id': foreign_id},
        )
        return [OperationRicItem.model_validate(r) for r in response.json()]

    async def delete_ric(
        self,
        foreign_id: str,
        payload: Sequence[OperationRicItem],
    ) -> Sequence[OperationRicItem]:
        """Remove RICs (DELETE /api/v2/operations/ric)."""
        data = [p.model_dump(by_alias=False, exclude_none=True) for p in payload]
        response = await self.client.delete(
            'v2/operations/ric',
            params={'foreign_id': foreign_id},
            json=data,
        )
        return [OperationRicItem.model_validate(r) for r in response.json()]

    async def alert_by_foreign_id(
        self,
        foreign_id: str,
        ric_names: Sequence[OperationRicItem] | None = None,
    ) -> Sequence[OperationRicItem]:
        """Alert RICs (POST /api/v2/operations/alert)."""
        data = [p.model_dump(by_alias=False, exclude_none=True) for p in ric_names] if ric_names else None
        response = await self.client.post(
            'v2/operations/alert',
            data=data,
            params={'foreign_id': foreign_id},
        )
        return [OperationRicItem.model_validate(r) for r in response.json()]

    async def archive_by_foreign_id(self, foreign_id: str) -> Operation:
        """Archive operation (POST /api/v2/operations/archive)."""
        response = await self.client.post(
            'v2/operations/archive',
            params={'foreign_id': foreign_id},
        )
        return Operation.model_validate(response.json())

    async def close_by_foreign_id(self, foreign_id: str) -> Operation:
        """Close operation (POST /api/v2/operations/state/close)."""
        response = await self.client.post(
            'v2/operations/state/close',
            params={'foreign_id': foreign_id},
        )
        return Operation.model_validate(response.json())

    async def open_by_foreign_id(self, foreign_id: str) -> Operation:
        """Reopen operation (POST /api/v2/operations/state/open)."""
        response = await self.client.post(
            'v2/operations/state/open',
            params={'foreign_id': foreign_id},
        )
        return Operation.model_validate(response.json())

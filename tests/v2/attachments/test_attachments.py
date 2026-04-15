"""Attachment API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.v2.endpoints import AttachmentEndpoint
from divera247.v2.models.alarm import SuccessResponse
from divera247.v2.models.attachment import AttachmentSingleResponse, AttachmentsResponse
from tests.v2._helpers import load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def attachment_endpoint(api_client: Divera247Client) -> AttachmentEndpoint:
    """Provide ``AttachmentEndpoint`` using the shared mock client."""
    return AttachmentEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('get_attachments_response.json', AttachmentsResponse),
        ('get_attachments_id_response.json', AttachmentSingleResponse),
        ('delete_attachments_id_response.json', SuccessResponse),
    ],
)
def test_attachment_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('attachments', filename))


async def test_get_attachments(
    attachment_endpoint: AttachmentEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET attachments returns success."""
    httpx_mock.add_response(json=load_v2_json('attachments', 'get_attachments_response.json'))
    response = await attachment_endpoint.get_attachments()
    assert response.success is True

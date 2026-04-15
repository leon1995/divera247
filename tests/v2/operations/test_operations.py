"""Operations API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.v2.endpoints import OperationsEndpoint
from divera247.v2.models.operations import (
    Operation,
    OperationFile,
    OperationFileResponse,
    OperationResponse,
)
from tests.v2._helpers import EXAMPLE_FOREIGN_ID, load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def operations_endpoint(api_client: Divera247Client) -> OperationsEndpoint:
    """Provide ``OperationsEndpoint`` using the shared mock client."""
    return OperationsEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_operations_request.json', Operation),
        ('post_operations_response.json', OperationResponse),
        ('get_operations_foreign_id_response.json', OperationResponse),
        ('post_operations_attachments_foreign_id_request.json', OperationFile),
        ('post_operations_attachments_foreign_id_response.json', OperationFileResponse),
        ('get_operations_id_attachments_attachment_id_response.json', OperationFileResponse),
    ],
)
def test_operations_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('operations', filename))


def test_operations_list_fixture_parses() -> None:
    """List response JSON must parse each element as ``OperationResponse``."""
    data = load_v2_json('operations', 'get_operations_response.json')
    assert isinstance(data, list)
    for item in data:
        OperationResponse.model_validate(item)


async def test_get_operations(
    operations_endpoint: OperationsEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET operations returns a non-empty list."""
    httpx_mock.add_response(json=load_v2_json('operations', 'get_operations_response.json'))
    response = await operations_endpoint.get_operations()
    assert len(response) >= 1


async def test_get_operation(
    operations_endpoint: OperationsEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET operation by foreign id returns matching foreign id."""
    httpx_mock.add_response(json=load_v2_json('operations', 'get_operations_foreign_id_response.json'))
    response = await operations_endpoint.get_operation(EXAMPLE_FOREIGN_ID)
    assert response.foreign_id == EXAMPLE_FOREIGN_ID

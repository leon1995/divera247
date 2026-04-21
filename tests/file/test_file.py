"""File API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.endpoints import FileEndpoint
from tests._helpers import EXAMPLE_ID

if TYPE_CHECKING:
    import pytest_httpx

    from divera247.client import Divera247Client


@pytest.fixture
def file_endpoint(api_client: Divera247Client) -> FileEndpoint:
    """Provide ``FileEndpoint`` using the shared mock client."""
    return FileEndpoint(api_client)


async def test_open_file(file_endpoint: FileEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    """Open file by id returns raw content from mock."""
    content = b'binary-bytes'
    httpx_mock.add_response(content=content)
    response = await file_endpoint.open_file(EXAMPLE_ID)
    assert response == content

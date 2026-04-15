"""File API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from tests.v2._helpers import EXAMPLE_ID

from divera247.client import Divera247Client
from divera247.v2.endpoints.file import FileEndpoint


@pytest.fixture
def file_endpoint(api_client: Divera247Client) -> FileEndpoint:
    return FileEndpoint(api_client)


async def test_open_file(file_endpoint: FileEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    content = b'binary-bytes'
    httpx_mock.add_response(content=content)
    response = await file_endpoint.open_file(EXAMPLE_ID)
    assert response == content

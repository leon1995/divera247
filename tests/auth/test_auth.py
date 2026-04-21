"""Auth API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.endpoints import AuthEndpoint
from divera247.models.auth import AuthJwtResponse, AuthLoginPayload, AuthLoginResponse
from tests._helpers import load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def auth_endpoint(api_client: Divera247Client) -> AuthEndpoint:
    """Provide ``AuthEndpoint`` using the shared mock client."""
    return AuthEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_login_request.json', AuthLoginPayload),
        ('post_login_response.json', AuthLoginResponse),
        ('get_jwt_response.json', AuthJwtResponse),
    ],
)
def test_auth_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('auth', filename))


async def test_login(auth_endpoint: AuthEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    """POST login returns success."""
    payload = AuthLoginPayload.model_validate(load_v2_json('auth', 'post_login_request.json'))
    httpx_mock.add_response(json=load_v2_json('auth', 'post_login_response.json'))
    response = await auth_endpoint.login(payload)
    assert response.success is True

"""Password API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.v2.endpoints import PasswordEndpoint
from divera247.v2.models.password import PasswordValidatePayload, PasswordValidateResponse
from tests.v2._helpers import load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def password_endpoint(api_client: Divera247Client) -> PasswordEndpoint:
    """Provide ``PasswordEndpoint`` using the shared mock client."""
    return PasswordEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_password_validate_request.json', PasswordValidatePayload),
        ('get_password_validate_request.json', PasswordValidatePayload),
        ('post_password_validate_response.json', PasswordValidateResponse),
        ('get_password_validate_response.json', PasswordValidateResponse),
    ],
)
def test_password_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('password', filename))


async def test_validate_password(
    password_endpoint: PasswordEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST password validate returns payload error flag."""
    payload = PasswordValidatePayload.model_validate(
        load_v2_json('password', 'post_password_validate_request.json'),
    )
    httpx_mock.add_response(json=load_v2_json('password', 'post_password_validate_response.json'))
    response = await password_endpoint.validate_post(payload)
    assert response.error is True


async def test_validate_password_get(
    password_endpoint: PasswordEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET password validate returns payload error flag."""
    payload = PasswordValidatePayload.model_validate(
        load_v2_json('password', 'get_password_validate_request.json'),
    )
    httpx_mock.add_response(json=load_v2_json('password', 'get_password_validate_response.json'))
    response = await password_endpoint.validate_get(payload)
    assert response.error is True

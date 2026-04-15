"""Password API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from pydantic import BaseModel
from tests.v2._helpers import load_v2_json

from divera247.client import Divera247Client
from divera247.v2.endpoints.password import PasswordEndpoint
from divera247.v2.models.password import PasswordValidatePayload, PasswordValidateResponse


@pytest.fixture
def password_endpoint(api_client: Divera247Client) -> PasswordEndpoint:
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
    model.model_validate(load_v2_json('password', filename))


async def test_validate_password(
    password_endpoint: PasswordEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
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
    payload = PasswordValidatePayload.model_validate(
        load_v2_json('password', 'get_password_validate_request.json'),
    )
    httpx_mock.add_response(json=load_v2_json('password', 'get_password_validate_response.json'))
    response = await password_endpoint.validate_get(payload)
    assert response.error is True

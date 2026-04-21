"""Unit tests for :mod:`divera247.auth`.

The refresh behaviour is exercised via ``pytest-httpx`` which intercepts the
internal :class:`httpx.AsyncClient` that :class:`RefreshingJwtAuth` builds for
JWT refresh requests, so no network IO happens. The JWT used in fixtures is
the same shape the server emits -- header/payload/signature separated by
dots -- with the signature slot filled with obviously fake data.
"""

from __future__ import annotations

import base64
import datetime
import json
from typing import TYPE_CHECKING

import httpx
import pytest

from divera247.auth import RefreshingJwtAuth
from divera247.errors import DiveraAuthError

if TYPE_CHECKING:
    import pytest_httpx


def _fake_jwt(*, exp_offset: int = 3600, ucr: int = 123) -> str:
    """Build a three-segment JWT with a decodable payload for tests.

    The middle segment is real base64url-encoded JSON; the outer segments are
    placeholders because ``AuthJwtPayload.from_token`` never inspects them.
    """
    now = datetime.datetime.now(tz=datetime.UTC)
    payload = {
        'iat': now.timestamp(),
        'exp': (now + datetime.timedelta(seconds=exp_offset)).timestamp(),
        'ucr': ucr,
    }
    middle = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    return f'header.{middle}.signature'


async def _first_prepared(auth: RefreshingJwtAuth) -> httpx.Request:
    """Drive ``auth.async_auth_flow`` once and return the prepared request."""
    request = httpx.Request('GET', 'https://app.divera247.com/api/v2/pull/all')
    async for prepared in auth.async_auth_flow(request):
        return prepared
    msg = 'async_auth_flow did not yield a prepared request'
    raise AssertionError(msg)


async def test_refreshing_jwt_auth_fetches_and_caches_token(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """A first request triggers a JWT fetch and caches the payload for later requests."""
    jwt = _fake_jwt()
    httpx_mock.add_response(
        url='https://app.divera247.com/api/v2/auth/jwt?accesskey=my-key',
        json={'success': True, 'data': {'jwt': jwt}},
    )
    auth = RefreshingJwtAuth('my-key')

    prepared = await _first_prepared(auth)

    assert prepared.headers['Authorization'] == f'Bearer {jwt}'
    assert auth.payload is not None
    assert auth.payload.token == jwt


async def test_refreshing_jwt_auth_uses_initial_jwt_without_fetching() -> None:
    """``initial_jwt`` short-circuits the first fetch when the token is still valid."""
    jwt = _fake_jwt()
    auth = RefreshingJwtAuth('my-key', initial_jwt=jwt)

    prepared = await _first_prepared(auth)

    assert prepared.headers['Authorization'] == f'Bearer {jwt}'


async def test_refreshing_jwt_auth_raises_auth_error_on_http_error(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """A 401 from the JWT endpoint must surface as :class:`DiveraAuthError`, not a raw httpx error."""
    httpx_mock.add_response(
        url='https://app.divera247.com/api/v2/auth/jwt?accesskey=bad',
        status_code=401,
        json={'success': False, 'errors': {'auth': 'denied'}},
    )
    auth = RefreshingJwtAuth('bad')

    with pytest.raises(DiveraAuthError) as excinfo:
        await _first_prepared(auth)
    assert excinfo.value.status_code == 401


async def test_refreshing_jwt_auth_raises_auth_error_on_success_false(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """A 200 response with ``success=false`` must still surface as :class:`DiveraAuthError`."""
    httpx_mock.add_response(
        url='https://app.divera247.com/api/v2/auth/jwt?accesskey=bad',
        json={'success': False},
    )
    auth = RefreshingJwtAuth('bad')

    with pytest.raises(DiveraAuthError):
        await _first_prepared(auth)


async def test_refreshing_jwt_auth_raises_auth_error_on_malformed_body(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """A schema-violating response (no JWT) is converted into :class:`DiveraAuthError`."""
    httpx_mock.add_response(
        url='https://app.divera247.com/api/v2/auth/jwt?accesskey=k',
        json={'success': True, 'data': {'jwt': 'not-a-jwt'}},
    )
    auth = RefreshingJwtAuth('k')

    with pytest.raises(DiveraAuthError):
        await _first_prepared(auth)


async def test_refreshing_jwt_auth_refreshes_when_token_near_expiry(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """An expired cached JWT triggers a refresh before attaching a new header."""
    stale = _fake_jwt(exp_offset=-60)
    fresh = _fake_jwt(exp_offset=3600)
    httpx_mock.add_response(
        url='https://app.divera247.com/api/v2/auth/jwt?accesskey=k',
        json={'success': True, 'data': {'jwt': fresh}},
    )
    auth = RefreshingJwtAuth('k', initial_jwt=stale)

    prepared = await _first_prepared(auth)

    assert prepared.headers['Authorization'] == f'Bearer {fresh}'

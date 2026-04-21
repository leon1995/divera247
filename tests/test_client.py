"""Tests for :class:`divera247.Divera247Client` configuration and endpoint wiring."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from divera247 import AccessKeyAuth, Divera247Client, DiveraAuthError, DiveraRateLimitError
from divera247.endpoints import (
    AlarmEndpoint,
    AuthEndpoint,
    PullEndpoint,
    UsingVehicleEndpoint,
)

if TYPE_CHECKING:
    import pytest_httpx


async def test_client_accepts_injected_session_and_does_not_close_it() -> None:
    """Injected sessions are borrowed: the caller retains ownership on ``__aexit__``."""
    external = httpx.AsyncClient()
    client = Divera247Client(auth=AccessKeyAuth('k'), session=external)
    async with client:
        pass
    assert not external.is_closed
    await external.aclose()


async def test_client_uses_injected_session_configuration() -> None:
    """A caller-configured session is used as-is, including custom headers and timeouts."""
    external = httpx.AsyncClient(
        headers={'User-Agent': 'my-app/1.0'},
        timeout=httpx.Timeout(5.0),
    )
    client = Divera247Client(auth=AccessKeyAuth('k'), session=external)
    async with client:
        assert client.session is external
        assert client.session.headers['User-Agent'] == 'my-app/1.0'
    await external.aclose()


@pytest.mark.parametrize(
    ('endpoint_attr', 'endpoint_cls'),
    [
        ('alarm', AlarmEndpoint),
        ('pull', PullEndpoint),
        ('auth_api', AuthEndpoint),
        ('using_vehicle', UsingVehicleEndpoint),
    ],
)
async def test_client_exposes_endpoints_as_cached_attributes(
    endpoint_attr: str,
    endpoint_cls: type,
) -> None:
    """Endpoint attributes return the expected type and are cached across accesses."""
    async with Divera247Client(auth=AccessKeyAuth('k')) as client:
        endpoint = getattr(client, endpoint_attr)
        assert isinstance(endpoint, endpoint_cls)
        assert getattr(client, endpoint_attr) is endpoint


async def test_client_raises_divera_auth_error_on_401(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """Transport-level 401 propagates as :class:`DiveraAuthError`."""
    httpx_mock.add_response(status_code=401, json={'success': False, 'errors': {'auth': 'bad'}})
    async with Divera247Client(auth=AccessKeyAuth('k')) as client:
        with pytest.raises(DiveraAuthError) as excinfo:
            await client.get('v2/anything')
    assert excinfo.value.status_code == 401


async def test_client_raises_rate_limit_error_on_429(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """429 responses raise :class:`DiveraRateLimitError` with ``retry_after``."""
    httpx_mock.add_response(status_code=429, json={'success': False}, headers={'Retry-After': '5'})
    async with Divera247Client(auth=AccessKeyAuth('k')) as client:
        with pytest.raises(DiveraRateLimitError) as excinfo:
            await client.get('v2/anything')
    assert excinfo.value.retry_after == pytest.approx(5.0)

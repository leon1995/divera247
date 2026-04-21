"""httpx auth flows for the Divera 24/7 API.

These classes provide ``Authorization: Bearer <token>`` based authentication
as alternatives to appending the access key as a query parameter.

- :class:`AccessKeyAuth` -- static access key sent as a bearer token.
- :class:`JwtAuth` -- static JWT sent as a bearer token.
- :class:`RefreshingJwtAuth` -- JWT fetched from ``/api/v2/auth/jwt`` and
  transparently renewed shortly before its ``exp`` claim.
"""

from __future__ import annotations

import datetime
import typing

import anyio
import httpx
from pydantic import ValidationError

from divera247.errors import DiveraAuthError
from divera247.models.auth import AuthJwtPayload, AuthJwtResponse

if typing.TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


class AccessKeyAuth(httpx.Auth):
    """Send the Divera access key as ``Authorization: Bearer <access_key>``."""

    def __init__(self, access_key: str) -> None:
        self._access_key = access_key

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        """Attach the access key as a bearer token to ``request``."""
        request.headers['Authorization'] = f'Bearer {self._access_key}'
        yield request


class JwtAuth(httpx.Auth):
    """Send a pre-obtained JWT as ``Authorization: Bearer <jwt>``."""

    def __init__(self, jwt: str) -> None:
        self._jwt = jwt

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        """Attach the JWT as a bearer token to ``request``."""
        request.headers['Authorization'] = f'Bearer {self._jwt}'
        yield request


class RefreshingJwtAuth(httpx.Auth):
    """Transparently obtain and refresh a JWT backed by an access key.

    The JWT is requested from ``GET {base_url}v2/auth/jwt?accesskey=...`` on
    first use and re-fetched ``refresh_leeway`` before the ``exp`` claim.
    Concurrent requests share a single refresh; this class is safe to use
    from multiple tasks on the same :class:`httpx.AsyncClient`.

    Only async clients are supported, because refreshing the JWT requires
    issuing an HTTP request of its own.
    """

    def __init__(
        self,
        access_key: str,
        *,
        base_url: str = 'https://app.divera247.com/api/',
        refresh_leeway: datetime.timedelta = datetime.timedelta(seconds=30),
        initial_jwt: str | None = None,
    ) -> None:
        self.access_key: typing.Final[str] = access_key
        self.base_url: typing.Final[str] = f'{base_url.rstrip("/")}/'
        self._refresh_leeway = refresh_leeway
        self._payload: AuthJwtPayload | None = AuthJwtPayload.from_token(initial_jwt) if initial_jwt else None
        self._lock = anyio.Lock()

    @property
    def payload(self) -> AuthJwtPayload | None:
        """Return the decoded claims of the cached JWT, if one has been obtained."""
        return self._payload

    @property
    def expires_at(self) -> datetime.datetime | None:
        """Return the cached JWT's ``exp`` claim as UTC datetime, if known."""
        return self._payload.exp if self._payload else None

    def _needs_refresh(self) -> bool:
        if self._payload is None:
            return True
        if self._payload.exp is None:
            return False
        return datetime.datetime.now(tz=datetime.UTC) + self._refresh_leeway >= self._payload.exp

    async def _refresh(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.base_url}v2/auth/jwt',
                    params={'accesskey': self.access_key},
                )
        except httpx.HTTPError as exc:
            transport_msg = f'failed to refresh JWT: transport error ({exc})'
            raise DiveraAuthError(transport_msg) from exc

        if response.is_error:
            http_msg = f'failed to refresh JWT: HTTP {response.status_code}'
            raise DiveraAuthError(
                http_msg,
                status_code=response.status_code,
                response=response,
                body=response.text,
            )

        try:
            parsed = AuthJwtResponse.model_validate_json(response.content)
        except ValidationError as exc:
            raise DiveraAuthError(
                'failed to refresh JWT: response did not match expected schema',
                status_code=response.status_code,
                response=response,
                body=response.text,
            ) from exc

        if not parsed.success or parsed.data is None:
            raise DiveraAuthError(
                'failed to refresh JWT: server reported success=false',
                status_code=response.status_code,
                response=response,
            )
        self._payload = parsed.data.jwt

    def sync_auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:  # noqa: ARG002
        """Reject sync clients; refreshing a JWT requires an async HTTP call."""
        raise RuntimeError('RefreshingJwtAuth only supports async httpx clients')
        yield  # pragma: no cover - unreachable, keeps return type a generator

    async def async_auth_flow(
        self,
        request: httpx.Request,
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        """Refresh the JWT if needed and attach it as a bearer token to ``request``."""
        if self._needs_refresh():
            async with self._lock:
                if self._needs_refresh():
                    await self._refresh()
        assert self._payload is not None
        request.headers['Authorization'] = f'Bearer {self._payload.token}'
        yield request

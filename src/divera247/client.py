"""Async HTTP client for the Divera 24/7 REST API.

The :class:`Divera247Client` owns an :class:`httpx.AsyncClient`, applies one of
the auth flows from :mod:`divera247.auth` to every request, and exposes each v2
endpoint group as a lazily-instantiated attribute (``client.alarm``,
``client.pull`` and so on).

Errors from the API -- both HTTP-level (4xx / 5xx) and envelope-level
(``success: false``) -- are converted into the hierarchy defined in
:mod:`divera247.errors` so callers can write a single ``except DiveraAPIError``
block.
"""

from __future__ import annotations

import contextlib
import functools
import typing
from typing import TYPE_CHECKING, Any

import anyio
import httpx

from divera247 import errors

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Mapping, Sequence

    from divera247.endpoints import (
        AlarmEndpoint,
        AttachmentEndpoint,
        AuthEndpoint,
        DashboardEndpoint,
        EventEndpoint,
        FileEndpoint,
        MessageChannelEndpoint,
        MessageEndpoint,
        NewsEndpoint,
        OperationsEndpoint,
        PasswordEndpoint,
        PullEndpoint,
        ReporttypeEndpoint,
        ShiftPlansEndpoint,
        StatusgeberEndpoint,
        UsingVehicleCrewEndpoint,
        UsingVehicleEndpoint,
        UsingVehiclePropertyEndpoint,
    )

QueryParams = typing.Union[
    'Mapping[str, Any]',
    'Sequence[tuple[str, Any]]',
    None,
]
"""Accepted shape for ``params=`` on every request method.

Kept narrow on purpose: matches what :class:`httpx.AsyncClient` actually
honours in practice without pulling ``httpx._types`` (a private module) into
the public surface.
"""

JsonBody = typing.Union['Mapping[str, Any]', 'Sequence[object]', None]
"""JSON request body payload accepted by :meth:`Divera247Client.post`/``put``/``delete``."""


class Divera247Client(anyio.AsyncContextManagerMixin):
    """Async client for the Divera 24/7 REST API.

    Endpoint groups are exposed as lazily-instantiated attributes
    (``client.alarm``, ``client.pull``, ...). Anything you'd normally
    configure on :class:`httpx.AsyncClient` -- timeouts, headers, ``User-Agent``,
    proxies, transports, event hooks -- is done by building your own client
    and passing it in via ``session=``.

    :param auth: The :class:`httpx.Auth` instance used to authenticate every
        request. See :mod:`divera247.auth` for the built-in options.
    :param base_url: API base URL, defaults to the production endpoint. A
        trailing slash is added if missing so relative paths like
        ``'v2/alarms'`` resolve cleanly. Ignored when ``session`` is passed.
    :param session: An optional pre-built :class:`httpx.AsyncClient` to reuse.
        When provided the caller keeps ownership: the session is **not**
        closed on ``__aexit__`` and its own ``auth`` / ``base_url`` /
        ``timeout`` / ``headers`` configuration is used as-is.
    """

    def __init__(
        self,
        auth: httpx.Auth,
        *,
        base_url: str = 'https://app.divera247.com/api/',
        session: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = f'{base_url.rstrip("/")}/'
        self.auth: typing.Final[httpx.Auth] = auth
        self._owns_session = session is None
        if session is None:
            session = httpx.AsyncClient(auth=auth, base_url=self.base_url)
        self.session: typing.Final[httpx.AsyncClient] = session

    @contextlib.asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[typing.Self]:
        """Enter the client's lifecycle; closes the owned session on exit."""
        if self._owns_session:
            async with self.session:
                yield self
        else:
            yield self

    async def aclose(self) -> None:
        """Close the underlying session if we own it; no-op otherwise."""
        if self._owns_session:
            await self.session.aclose()

    async def _request(  # noqa: PLR0913
        self,
        method: str,
        path: str,
        *,
        params: QueryParams = None,
        json: JsonBody = None,
        files: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        """Issue a request and convert any HTTP error into a :class:`DiveraAPIError`."""
        response = await self.session.request(
            method,
            path,
            params=typing.cast('Any', params),
            json=json,
            files=files,
            data=data,
        )
        errors.raise_from_response(response)
        return response

    async def get(self, path: str, params: QueryParams = None) -> httpx.Response:
        """Get a resource."""
        return await self._request('GET', path, params=params)

    async def post(
        self,
        path: str,
        data: JsonBody = None,
        params: QueryParams = None,
    ) -> httpx.Response:
        """Create a resource."""
        return await self._request('POST', path, params=params, json=data)

    async def post_multipart(
        self,
        path: str,
        *,
        files: Mapping[str, Any] | None = None,
        data: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Create a resource with multipart data."""
        return await self._request('POST', path, files=files, data=data)

    async def put(
        self,
        path: str,
        data: JsonBody = None,
        params: QueryParams = None,
    ) -> httpx.Response:
        """Update a resource."""
        return await self._request('PUT', path, params=params, json=data)

    async def delete(
        self,
        path: str,
        params: QueryParams = None,
        *,
        json: JsonBody = None,
    ) -> httpx.Response:
        """Delete a resource. Pass ``json=`` for request body (e.g. operation RIC delete)."""
        return await self._request('DELETE', path, params=params, json=json)

    @functools.cached_property
    def alarm(self) -> AlarmEndpoint:
        """Alarm endpoints (``/api/v2/alarms``)."""
        from divera247.endpoints.alarm import AlarmEndpoint

        return AlarmEndpoint(self)

    @functools.cached_property
    def attachment(self) -> AttachmentEndpoint:
        """Attachment endpoints (``/api/v2/attachments``)."""
        from divera247.endpoints.attachment import AttachmentEndpoint

        return AttachmentEndpoint(self)

    @functools.cached_property
    def auth_api(self) -> AuthEndpoint:
        """Auth endpoints (``/api/v2/auth``). Named ``auth_api`` to avoid clashing with :attr:`auth`."""
        from divera247.endpoints.auth import AuthEndpoint

        return AuthEndpoint(self)

    @functools.cached_property
    def dashboard(self) -> DashboardEndpoint:
        """Dashboard endpoints (``/api/v2/dashboard``)."""
        from divera247.endpoints.dashboard import DashboardEndpoint

        return DashboardEndpoint(self)

    @functools.cached_property
    def event(self) -> EventEndpoint:
        """Event endpoints (``/api/v2/events``)."""
        from divera247.endpoints.event import EventEndpoint

        return EventEndpoint(self)

    @functools.cached_property
    def file(self) -> FileEndpoint:
        """File endpoints (``/api/v2/file``)."""
        from divera247.endpoints.file import FileEndpoint

        return FileEndpoint(self)

    @functools.cached_property
    def message(self) -> MessageEndpoint:
        """Message endpoints (``/api/v2/messages``)."""
        from divera247.endpoints.message import MessageEndpoint

        return MessageEndpoint(self)

    @functools.cached_property
    def message_channel(self) -> MessageChannelEndpoint:
        """Message channel endpoints (``/api/v2/message-channels``)."""
        from divera247.endpoints.message_channel import MessageChannelEndpoint

        return MessageChannelEndpoint(self)

    @functools.cached_property
    def news(self) -> NewsEndpoint:
        """News endpoints (``/api/v2/news``)."""
        from divera247.endpoints.news import NewsEndpoint

        return NewsEndpoint(self)

    @functools.cached_property
    def operations(self) -> OperationsEndpoint:
        """Operations endpoints (``/api/v2/operations``)."""
        from divera247.endpoints.operations import OperationsEndpoint

        return OperationsEndpoint(self)

    @functools.cached_property
    def password(self) -> PasswordEndpoint:
        """Password endpoints (``/api/v2/password``)."""
        from divera247.endpoints.password import PasswordEndpoint

        return PasswordEndpoint(self)

    @functools.cached_property
    def pull(self) -> PullEndpoint:
        """Pull endpoints (``/api/v2/pull``)."""
        from divera247.endpoints.pull import PullEndpoint

        return PullEndpoint(self)

    @functools.cached_property
    def reporttype(self) -> ReporttypeEndpoint:
        """Reporttype endpoints (``/api/v2/reporttypes``)."""
        from divera247.endpoints.reporttype import ReporttypeEndpoint

        return ReporttypeEndpoint(self)

    @functools.cached_property
    def shift_plans(self) -> ShiftPlansEndpoint:
        """Shift-plans endpoints (``/api/v2/shift-plans``)."""
        from divera247.endpoints.shift_plans import ShiftPlansEndpoint

        return ShiftPlansEndpoint(self)

    @functools.cached_property
    def statusgeber(self) -> StatusgeberEndpoint:
        """Statusgeber endpoints (``/api/v2/statusgeber``)."""
        from divera247.endpoints.statusgeber import StatusgeberEndpoint

        return StatusgeberEndpoint(self)

    @functools.cached_property
    def using_vehicle(self) -> UsingVehicleEndpoint:
        """Using-vehicle endpoints (``/api/v2/using-vehicles``)."""
        from divera247.endpoints.using_vehicle import UsingVehicleEndpoint

        return UsingVehicleEndpoint(self)

    @functools.cached_property
    def using_vehicle_crew(self) -> UsingVehicleCrewEndpoint:
        """Using-vehicle crew endpoints."""
        from divera247.endpoints.using_vehicle_crew import UsingVehicleCrewEndpoint

        return UsingVehicleCrewEndpoint(self)

    @functools.cached_property
    def using_vehicle_property(self) -> UsingVehiclePropertyEndpoint:
        """Using-vehicle property endpoints."""
        from divera247.endpoints.using_vehicle_property import UsingVehiclePropertyEndpoint

        return UsingVehiclePropertyEndpoint(self)

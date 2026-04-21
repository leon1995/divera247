import contextlib
import typing
from collections.abc import AsyncGenerator, Mapping, Sequence
from typing import Any

import anyio
import httpx
from httpx._types import QueryParamTypes


class Divera247Client(anyio.AsyncContextManagerMixin):
    """Divera 24/7 client."""

    def __init__(self, auth: httpx.Auth, base_url: str = 'https://app.divera247.com/api/'):
        self.base_url = f'{base_url.rstrip("/")}/'
        self.auth: typing.Final[httpx.Auth] = auth
        self.session: typing.Final[httpx.AsyncClient] = httpx.AsyncClient(auth=auth, base_url=self.base_url)

    @contextlib.asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[typing.Self]:
        async with self.session:
            yield self

    async def get(self, path: str, params: QueryParamTypes | None = None) -> httpx.Response:
        """Get a resource."""
        response = await self.session.get(path, params=params)
        response.raise_for_status()
        return response

    async def post(
        self,
        path: str,
        data: Mapping[str, Any] | Sequence[object] | None = None,
        params: QueryParamTypes | None = None,
    ) -> httpx.Response:
        """Create a resource."""
        response = await self.session.post(path, json=data, params=params)
        response.raise_for_status()
        return response

    async def post_multipart(
        self,
        path: str,
        *,
        files: Mapping[str, Any] | None = None,
        data: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Create a resource with multipart data."""
        response = await self.session.post(path, files=files, data=data)
        response.raise_for_status()
        return response

    async def put(
        self,
        path: str,
        data: Mapping[str, Any] | Sequence[object] | None = None,
        params: QueryParamTypes | None = None,
    ) -> httpx.Response:
        """Update a resource."""
        response = await self.session.put(path, json=data, params=params)
        response.raise_for_status()
        return response

    async def delete(
        self,
        path: str,
        params: QueryParamTypes | None = None,
        *,
        json: Mapping[str, object] | Sequence[object] | None = None,
    ) -> httpx.Response:
        """Delete a resource. Pass json= for request body (e.g. operation RIC delete)."""
        if json is not None:
            response = await self.session.request('DELETE', path, params=params, json=json)
        else:
            response = await self.session.delete(path, params=params)
        response.raise_for_status()
        return response

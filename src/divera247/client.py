import contextlib
import typing
from collections.abc import AsyncGenerator, Mapping, Sequence
from typing import Any

import anyio
import httpx
from httpx._types import QueryParamTypes


class Divera247Client(anyio.AsyncContextManagerMixin):
    """Divera 24/7 client."""

    def __init__(self, access_key: str, base_url: str = 'https://app.divera247.com/api/'):
        self.base_url = f'{base_url.rstrip("/")}/'
        self.access_key = access_key
        self._session = httpx.AsyncClient()

    @contextlib.asynccontextmanager
    async def __asynccontextmanager__(self) -> AsyncGenerator[typing.Self]:
        async with self._session:
            yield self

    def _merge_params(self, params: QueryParamTypes | None = None) -> httpx.QueryParams:
        return httpx.QueryParams(params or {}).merge({'accesskey': self.access_key})

    async def get(self, path: str, params: QueryParamTypes | None = None) -> httpx.Response:
        """Get a resource."""
        response = await self._session.get(f'{self.base_url}{path}', params=self._merge_params(params))
        response.raise_for_status()
        return response

    async def post(
        self,
        path: str,
        data: Mapping[str, Any] | Sequence[object] | None = None,
        params: QueryParamTypes | None = None,
    ) -> httpx.Response:
        """Create a resource."""
        response = await self._session.post(
            f'{self.base_url}{path}',
            json=data,
            params=self._merge_params(params),
        )
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
        response = await self._session.post(
            f'{self.base_url}{path}',
            files=files,
            data=data,
            params=self._merge_params(),
        )
        response.raise_for_status()
        return response

    async def put(
        self,
        path: str,
        data: Mapping[str, Any] | Sequence[object] | None = None,
        params: QueryParamTypes | None = None,
    ) -> httpx.Response:
        """Update a resource."""
        response = await self._session.put(
            f'{self.base_url}{path}',
            json=data,
            params=self._merge_params(params),
        )
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
        url = f'{self.base_url}{path}'
        if json is not None:
            response = await self._session.request(
                'DELETE',
                url,
                params=self._merge_params(params),
                json=json,
            )
        else:
            response = await self._session.delete(
                url,
                params=self._merge_params(params),
            )
        response.raise_for_status()
        return response

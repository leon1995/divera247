"""Divera 24/7 WebSocket subscription loop.

Two entry points are exposed:

* :func:`subscribe_websocket` -- single-session async iterator of push events
  with bounded JWT re-auth. Exits when the server disconnects, so callers in
  control of their own retry strategy can wrap it as they see fit.
* :func:`stream_websocket` -- long-running async iterator that transparently
  reconnects with jittered exponential backoff, re-authenticating on every
  reconnect. Use this when you want a "just keep me subscribed" loop.

The ``Authorization: Bearer <token>`` value for the ``authenticate`` frame is
obtained by running the :class:`httpx.Auth` attached to the provided
:class:`~divera247.client.Divera247Client`. **Only auth flows that set
exactly that header work** -- any other scheme (Basic, query-param-only, etc.)
raises :class:`RuntimeError`. All built-in auth classes in
:mod:`divera247.auth` satisfy this contract.

.. code-block:: python

    async for event in stream_websocket(client, ucr_id=ucr_id):
        ...
"""

from __future__ import annotations

import contextlib
import json
import logging
import random
from typing import TYPE_CHECKING, Any

import anyio
import httpx

try:
    import httpx_ws
except ImportError as exc:
    _hint = (
        "divera247 WebSocket support requires the optional 'httpx-ws' package; "
        "install it via the 'ws' extra, e.g. `pip install 'divera247[ws]'` or "
        "`uv add 'divera247[ws]'`."
    )
    raise ImportError(_hint) from exc

from divera247.websocket import models

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping

    from divera247.client import Divera247Client

logger = logging.getLogger(__name__)


class WebSocketAuthenticationError(RuntimeError):
    """Raised when the Divera WebSocket keeps rejecting our authentication.

    Signals a persistent credential/JWT problem that reconnecting will not
    fix; :func:`subscribe_websocket` and :func:`stream_websocket` therefore
    propagate this instead of silently looping.
    """


def _build_auth_message(jwt: str, ucr_id: int | None) -> Mapping[str, Any]:
    payload: dict[str, Any] = {'jwt': jwt}
    if ucr_id is not None:
        payload['ucr'] = ucr_id
    return {'type': 'authenticate', 'payload': payload}


async def _bearer_token_from_auth(auth: httpx.Auth) -> str:
    """Drive ``auth``'s flow with a dummy request and return the Bearer token it attaches.

    Works with any :class:`httpx.Auth` that sets an ``Authorization: Bearer <token>``
    header on outgoing requests, so the WebSocket frame builder does not need
    to know whether the token is a static access key, a pre-shared JWT, or
    one that is transparently refreshed.
    """
    dummy = httpx.Request('GET', 'https://app.divera247.com/')
    async with contextlib.aclosing(auth.async_auth_flow(dummy)) as flow:
        prepared = await anext(flow)
    authorization = prepared.headers.get('Authorization', '')
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        msg = f'auth did not yield a bearer token (got {authorization!r})'
        raise RuntimeError(msg)
    return token


async def _send_auth(
    ws: httpx_ws.AsyncWebSocketSession,
    client: Divera247Client,
    ucr_id: int | None,
) -> None:
    jwt = await _bearer_token_from_auth(client.auth)
    await ws.send_json(_build_auth_message(jwt, ucr_id))


async def _ws_session(
    client: Divera247Client,
    ucr_id: int | None,
    ws_url: str,
    max_auth_attempts: int,
) -> AsyncIterator[Mapping[str, Any]]:
    """Yield business events from a single WebSocket session until it disconnects.

    Session-level frames (``init`` / ``jwtExpired``) are consumed internally and
    not surfaced to the caller. Tracks consecutive ``jwtExpired`` events since
    the last successful ``init`` and raises :class:`WebSocketAuthenticationError`
    once ``max_auth_attempts`` is exceeded, so the outer reconnect loop stops
    retrying a credential that is clearly not accepted.
    """
    async with httpx_ws.aconnect_ws(ws_url, client.session, keepalive_ping_interval_seconds=25) as ws:
        await _send_auth(ws, client, ucr_id)
        auth_attempts = 1

        while True:
            raw = await ws.receive_text()
            try:
                event = json.loads(raw)
            except ValueError:
                logger.error('non-json message received: %s', raw)  # noqa: TRY400
                continue

            msg_type = event.get('type', '')
            if msg_type == 'init':
                logger.info('websocket authenticated')
                auth_attempts = 0
                continue
            if msg_type == 'jwtExpired':
                if auth_attempts >= max_auth_attempts:
                    msg = (
                        f'websocket rejected authentication {auth_attempts} times in a row; aborting instead of looping'
                    )
                    raise WebSocketAuthenticationError(msg)
                auth_attempts += 1
                logger.info('jwt expired - re-authenticating')
                await _send_auth(ws, client, ucr_id)
                continue

            yield event


async def subscribe_websocket(
    client: Divera247Client,
    *,
    ucr_id: int | None = None,
    ws_url: str = 'wss://ws.divera247.com/ws',
    max_auth_attempts: int = 3,
) -> AsyncIterator[models.UserStatusEvent | models.ClusterPullEvent | models.UnknownEvent]:
    """Yield typed Divera 24/7 WebSocket events from a single session.

    Exits when the underlying socket disconnects (by raising
    :class:`httpx_ws.WebSocketDisconnect`). If you want transparent
    reconnection, use :func:`stream_websocket` instead.
    """
    async for event in _ws_session(client, ucr_id, ws_url, max_auth_attempts):
        yield models.parse_event(event)


async def stream_websocket(  # noqa: PLR0913
    client: Divera247Client,
    *,
    ucr_id: int | None = None,
    ws_url: str = 'wss://ws.divera247.com/ws',
    max_auth_attempts: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    backoff_factor: float = 2.0,
    backoff_jitter: float = 0.2,
) -> AsyncIterator[models.UserStatusEvent | models.ClusterPullEvent | models.UnknownEvent]:
    """Yield events forever, transparently reconnecting on any disconnect.

    Reconnect delay follows jittered exponential backoff bounded by
    ``max_backoff``. The counter resets every time a session successfully
    yields at least one business event, so flapping networks don't starve a
    client that is otherwise making progress.

    :class:`WebSocketAuthenticationError` is propagated (bad credentials won't
    get better by retrying), while transport-layer failures are logged and
    retried.
    """
    backoff = initial_backoff
    while True:
        delivered = False
        try:
            async for event in subscribe_websocket(
                client,
                ucr_id=ucr_id,
                ws_url=ws_url,
                max_auth_attempts=max_auth_attempts,
            ):
                delivered = True
                yield event
        except WebSocketAuthenticationError:
            raise
        except (httpx_ws.WebSocketDisconnect, httpx_ws.WebSocketNetworkError, httpx.HTTPError) as exc:
            logger.warning('websocket disconnected (%s); reconnecting in %.1fs', exc, backoff)
        except Exception:
            logger.exception('websocket raised an unexpected error; reconnecting in %.1fs', backoff)
        else:
            logger.info('websocket ended cleanly; reconnecting in %.1fs', backoff)

        if delivered:
            backoff = initial_backoff
        jitter = random.uniform(-backoff_jitter, backoff_jitter) * backoff
        await anyio.sleep(max(0.0, backoff + jitter))
        backoff = min(max_backoff, backoff * backoff_factor)

"""Tests for :mod:`divera247.websocket.session` with a mocked WebSocket server.

The real ``httpx_ws.aconnect_ws`` is patched with a fake async context manager
that surfaces a scripted list of incoming frames and records every frame the
session sends back. This lets us exercise the handshake, the internal
``init`` / ``jwtExpired`` handling, the auth-attempt budget and the business
event dispatch without any network IO.
"""

from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Any

import httpx
import httpx_ws
import pytest

from divera247.auth import AccessKeyAuth
from divera247.client import Divera247Client
from divera247.websocket import session as session_module
from divera247.websocket.models import (
    UnknownEvent,
    UserStatusEvent,
)
from divera247.websocket.session import (
    WebSocketAuthenticationError,
    _bearer_token_from_auth,
    _build_auth_message,
    subscribe_websocket,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable, Sequence


EXPECTED_UCR = 527459
EXPECTED_AUTH_ATTEMPT_BUDGET = 3
EXPECTED_REAUTH_FRAMES = 2

_USER_STATUS_FRAME = {
    'type': 'user-status',
    'payload': {
        'type': 'user-status',
        'status': {
            'status_id': 33035,
            'status_skip_statusplan': False,
            'status_skip_geofence': False,
            'status_set_date': 1776767153,
            'status_reset_date': '',
            'status_reset_id': 0,
            'status_log': [],
            'status_changes': [],
            'note': '',
            'vehicle': 0,
            'ts': 1776767153,
            'cached': False,
        },
        'ucr': EXPECTED_UCR,
    },
}


class FakeWebSocketSession:
    """Minimal stand-in for :class:`httpx_ws.AsyncWebSocketSession`.

    Pops frames off a pre-scripted queue on ``receive_text`` and records every
    ``send_json`` call; once the queue is empty it raises
    :class:`httpx_ws.WebSocketDisconnect` to end the session, matching how the
    real server terminates the stream.
    """

    def __init__(self, incoming: Iterable[Any]) -> None:
        self._incoming: list[str] = [frame if isinstance(frame, str) else json.dumps(frame) for frame in incoming]
        self.sent: list[dict[str, Any]] = []

    async def send_json(self, payload: dict[str, Any]) -> None:
        """Record ``payload`` as if it had been sent on the wire."""
        self.sent.append(payload)

    async def receive_text(self) -> str:
        """Return the next scripted frame or raise ``WebSocketDisconnect`` when drained."""
        if not self._incoming:
            raise httpx_ws.WebSocketDisconnect(code=1000, reason='no more messages')
        return self._incoming.pop(0)


def _install_fake_ws(
    monkeypatch: pytest.MonkeyPatch,
    fake_session: FakeWebSocketSession,
) -> list[tuple[str, httpx.AsyncClient | None]]:
    """Replace ``httpx_ws.aconnect_ws`` so it yields ``fake_session``."""
    calls: list[tuple[str, httpx.AsyncClient | None]] = []

    @contextlib.asynccontextmanager
    async def fake_aconnect_ws(
        url: str,
        client: httpx.AsyncClient | None = None,
        **_: object,
    ) -> AsyncGenerator[FakeWebSocketSession]:
        calls.append((url, client))
        yield fake_session

    monkeypatch.setattr(session_module.httpx_ws, 'aconnect_ws', fake_aconnect_ws)
    return calls


async def _collect(events: Any, limit: int | None = None) -> list[Any]:
    """Drain an async iterator and return its items, capped by ``limit``."""
    out: list[Any] = []
    async for event in events:
        out.append(event)
        if limit is not None and len(out) >= limit:
            break
    return out


@pytest.fixture
async def ws_client() -> AsyncGenerator[Divera247Client]:
    """Provide a client whose access-key bearer token is deterministic for assertions."""
    async with Divera247Client(auth=AccessKeyAuth('test-access-key')) as client:
        yield client


def test_build_auth_message_without_ucr() -> None:
    """Without a UCR id, only the JWT is wrapped in the ``authenticate`` envelope."""
    msg = _build_auth_message('my-jwt', None)
    assert msg == {'type': 'authenticate', 'payload': {'jwt': 'my-jwt'}}


def test_build_auth_message_with_ucr() -> None:
    """A provided UCR id is included next to the JWT under ``payload``."""
    msg = _build_auth_message('my-jwt', 4711)
    assert msg == {'type': 'authenticate', 'payload': {'jwt': 'my-jwt', 'ucr': 4711}}


async def test_bearer_token_from_auth_extracts_access_key_token() -> None:
    """``AccessKeyAuth`` yields the key as a bearer token."""
    token = await _bearer_token_from_auth(AccessKeyAuth('abc123'))
    assert token == 'abc123'  # noqa: S105


async def test_bearer_token_from_auth_rejects_non_bearer_scheme() -> None:
    """Any other ``Authorization`` scheme is explicitly rejected."""

    class BasicAuth(httpx.Auth):
        def auth_flow(self, request: httpx.Request) -> Any:
            """Emit a Basic auth header to prove the guard."""
            request.headers['Authorization'] = 'Basic dXNlcjpwYXNz'
            yield request

    with pytest.raises(RuntimeError, match='bearer'):
        await _bearer_token_from_auth(BasicAuth())


async def test_bearer_token_from_auth_rejects_missing_header() -> None:
    """An auth that sets no ``Authorization`` header must fail loudly."""

    class NoAuth(httpx.Auth):
        def auth_flow(self, request: httpx.Request) -> Any:
            """Pass the request through without touching headers."""
            yield request

    with pytest.raises(RuntimeError, match='bearer'):
        await _bearer_token_from_auth(NoAuth())


async def test_subscribe_websocket_sends_authenticate_frame(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """First frame on the wire must be an ``authenticate`` envelope with the bearer token."""
    fake = FakeWebSocketSession([{'type': 'init'}])
    _install_fake_ws(monkeypatch, fake)

    with contextlib.suppress(httpx_ws.WebSocketDisconnect):
        await _collect(subscribe_websocket(ws_client))

    assert fake.sent == [{'type': 'authenticate', 'payload': {'jwt': 'test-access-key'}}]


async def test_subscribe_websocket_includes_ucr_id_when_provided(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """``ucr_id`` is forwarded into the authenticate payload."""
    fake = FakeWebSocketSession([{'type': 'init'}])
    _install_fake_ws(monkeypatch, fake)

    with contextlib.suppress(httpx_ws.WebSocketDisconnect):
        await _collect(subscribe_websocket(ws_client, ucr_id=EXPECTED_UCR))

    assert fake.sent[0]['payload'] == {'jwt': 'test-access-key', 'ucr': EXPECTED_UCR}


async def test_subscribe_websocket_uses_configured_ws_url(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """A custom ``ws_url`` is passed through to ``aconnect_ws`` unchanged."""
    fake = FakeWebSocketSession([{'type': 'init'}])
    calls = _install_fake_ws(monkeypatch, fake)

    with contextlib.suppress(httpx_ws.WebSocketDisconnect):
        await _collect(subscribe_websocket(ws_client, ws_url='wss://example.test/ws'))

    assert calls[0][0] == 'wss://example.test/ws'


async def test_subscribe_websocket_yields_known_event_types(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """Known events are dispatched to their typed Pydantic envelopes."""
    fake = FakeWebSocketSession(
        [
            {'type': 'init'},
            _USER_STATUS_FRAME,
        ]
    )
    _install_fake_ws(monkeypatch, fake)

    events = await _collect(subscribe_websocket(ws_client), limit=1)

    assert isinstance(events[0], UserStatusEvent)
    assert events[0].ucr == EXPECTED_UCR


async def test_subscribe_websocket_unknown_event_falls_back_to_unknown_model(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """Unknown ``type`` frames surface as UnknownEvent with the original data intact."""
    raw_extras = {'payload': {'id': 42}, 'cluster': 8381}
    fake = FakeWebSocketSession(
        [
            {'type': 'init'},
            {'type': 'some-brand-new-event', **raw_extras},
        ]
    )
    _install_fake_ws(monkeypatch, fake)

    events = await _collect(subscribe_websocket(ws_client), limit=1)

    assert isinstance(events[0], UnknownEvent)
    assert events[0].type == 'some-brand-new-event'
    assert events[0].model_extra == raw_extras


async def test_subscribe_websocket_init_frame_is_not_yielded(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """``init`` is session-level and must stay internal to the session loop."""
    fake = FakeWebSocketSession([{'type': 'init'}, _USER_STATUS_FRAME])
    _install_fake_ws(monkeypatch, fake)

    events = await _collect(subscribe_websocket(ws_client), limit=1)

    assert len(events) == 1
    assert isinstance(events[0], UserStatusEvent)


async def test_subscribe_websocket_ignores_non_json_frames(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """Malformed non-JSON frames are logged and skipped instead of aborting the stream."""
    fake = FakeWebSocketSession(
        [
            {'type': 'init'},
            'this is not json',
            _USER_STATUS_FRAME,
        ]
    )
    _install_fake_ws(monkeypatch, fake)

    events = await _collect(subscribe_websocket(ws_client), limit=1)

    assert isinstance(events[0], UserStatusEvent)


async def test_subscribe_websocket_reauthenticates_on_jwt_expired(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """A ``jwtExpired`` frame triggers a fresh ``authenticate`` frame on the same socket."""
    fake = FakeWebSocketSession(
        [
            {'type': 'init'},
            {'type': 'jwtExpired'},
            {'type': 'init'},
            _USER_STATUS_FRAME,
        ]
    )
    _install_fake_ws(monkeypatch, fake)

    events = await _collect(subscribe_websocket(ws_client), limit=1)

    assert isinstance(events[0], UserStatusEvent)
    auth_frames = [frame for frame in fake.sent if frame.get('type') == 'authenticate']
    assert len(auth_frames) == EXPECTED_REAUTH_FRAMES


async def test_subscribe_websocket_bounded_retries_raise_authentication_error(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """Repeated ``jwtExpired`` without any ``init`` trips the attempt budget and raises."""
    fake = FakeWebSocketSession(
        [
            {'type': 'jwtExpired'},
            {'type': 'jwtExpired'},
            {'type': 'jwtExpired'},
        ]
    )
    _install_fake_ws(monkeypatch, fake)

    with pytest.raises(WebSocketAuthenticationError, match='3 times in a row'):
        await _collect(subscribe_websocket(ws_client, max_auth_attempts=EXPECTED_AUTH_ATTEMPT_BUDGET))


async def test_subscribe_websocket_init_resets_auth_attempt_budget(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """A successful ``init`` after retries wipes the failure counter for later rounds."""
    frames: Sequence[dict[str, Any]] = [
        {'type': 'jwtExpired'},
        {'type': 'init'},
        {'type': 'jwtExpired'},
        {'type': 'jwtExpired'},
        {'type': 'init'},
        _USER_STATUS_FRAME,
    ]
    fake = FakeWebSocketSession(frames)
    _install_fake_ws(monkeypatch, fake)

    events = await _collect(
        subscribe_websocket(ws_client, max_auth_attempts=EXPECTED_AUTH_ATTEMPT_BUDGET),
        limit=1,
    )

    assert isinstance(events[0], UserStatusEvent)


async def test_subscribe_websocket_propagates_disconnect(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """Server-side closure surfaces as :class:`WebSocketDisconnect` (no silent reconnect)."""
    fake = FakeWebSocketSession([{'type': 'init'}])
    _install_fake_ws(monkeypatch, fake)

    with pytest.raises(httpx_ws.WebSocketDisconnect):
        await _collect(subscribe_websocket(ws_client))

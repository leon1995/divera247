"""Tests for :func:`divera247.websocket.stream_websocket` reconnect behaviour.

Uses the same ``FakeWebSocketSession`` style as ``test_session.py``, but here
multiple sessions are queued up so we can exercise the reconnect loop. Sleeps
between reconnects are stubbed out to keep the suite fast.
"""

from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING, Any

import httpx_ws
import pytest

from divera247.auth import AccessKeyAuth
from divera247.client import Divera247Client
from divera247.websocket import session as session_module
from divera247.websocket.models import UserStatusEvent
from divera247.websocket.session import (
    WebSocketAuthenticationError,
    stream_websocket,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable, Sequence

EXPECTED_UCR = 527459
_USER_STATUS_FRAME: dict[str, Any] = {
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


class _FakeSession:
    """Scripted WebSocket session that hands out pre-baked frames."""

    def __init__(self, incoming: Iterable[Any]) -> None:
        self._incoming: list[str] = [frame if isinstance(frame, str) else json.dumps(frame) for frame in incoming]
        self.sent: list[dict[str, Any]] = []

    async def send_json(self, payload: dict[str, Any]) -> None:
        """Accept and record outgoing frames."""
        self.sent.append(payload)

    async def receive_text(self) -> str:
        """Yield queued frames then signal disconnect."""
        if not self._incoming:
            raise httpx_ws.WebSocketDisconnect(code=1000, reason='end of script')
        return self._incoming.pop(0)


def _install_stream_ws(
    monkeypatch: pytest.MonkeyPatch,
    sessions: Sequence[_FakeSession],
) -> list[_FakeSession]:
    """Route successive ``aconnect_ws`` calls to successive fake sessions."""
    opened: list[_FakeSession] = []
    iterator = iter(sessions)

    @contextlib.asynccontextmanager
    async def fake_aconnect_ws(*_args: object, **_kwargs: object) -> AsyncGenerator[_FakeSession]:
        session = next(iterator)
        opened.append(session)
        yield session

    monkeypatch.setattr(session_module.httpx_ws, 'aconnect_ws', fake_aconnect_ws)
    return opened


@pytest.fixture(autouse=True)
def _no_backoff_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip real sleeps between reconnects; they're covered by unit-tested args."""

    async def fast_sleep(_: float) -> None:
        """No-op replacement so the reconnect loop does not actually wait."""

    monkeypatch.setattr(session_module.anyio, 'sleep', fast_sleep)


@pytest.fixture
async def ws_client() -> AsyncGenerator[Divera247Client]:
    """Provide a client with a deterministic bearer token for auth-frame assertions."""
    async with Divera247Client(auth=AccessKeyAuth('k')) as client:
        yield client


async def _collect(events: Any, limit: int) -> list[Any]:
    """Drain up to ``limit`` events out of an async iterator."""
    out: list[Any] = []
    async for event in events:
        out.append(event)
        if len(out) >= limit:
            break
    return out


async def test_stream_websocket_reconnects_after_disconnect(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """A disconnect between frames is handled transparently; the caller sees a single stream."""
    opened = _install_stream_ws(
        monkeypatch,
        [
            _FakeSession([{'type': 'init'}, _USER_STATUS_FRAME]),
            _FakeSession([{'type': 'init'}, _USER_STATUS_FRAME]),
        ],
    )

    events = await _collect(stream_websocket(ws_client, initial_backoff=0.0), limit=2)

    assert len(events) == 2
    assert all(isinstance(event, UserStatusEvent) for event in events)
    assert len(opened) == 2


async def test_stream_websocket_propagates_authentication_error(
    monkeypatch: pytest.MonkeyPatch,
    ws_client: Divera247Client,
) -> None:
    """Repeated ``jwtExpired`` aborts the stream instead of reconnecting forever."""
    _install_stream_ws(
        monkeypatch,
        [_FakeSession([{'type': 'jwtExpired'}, {'type': 'jwtExpired'}, {'type': 'jwtExpired'}])],
    )

    with pytest.raises(WebSocketAuthenticationError):
        await _collect(stream_websocket(ws_client, max_auth_attempts=3), limit=1)

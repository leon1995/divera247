"""Regression test for the ``ws`` optional extra guard in ``divera247.websocket``.

Simulates a missing ``httpx-ws`` install by sticking ``None`` into
``sys.modules['httpx_ws']`` (which makes ``import httpx_ws`` raise
``ImportError``) and verifies that importing :mod:`divera247.websocket.session`
surfaces a helpful message pointing at the ``[ws]`` extra instead of the raw
upstream error.
"""

from __future__ import annotations

import importlib
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

_WS_MODULES = (
    'divera247.websocket',
    'divera247.websocket.session',
    'divera247.websocket.models',
)


@pytest.fixture
def without_httpx_ws(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Make ``import httpx_ws`` raise, mirroring a missing optional extra."""
    monkeypatch.setitem(sys.modules, 'httpx_ws', None)
    for name in _WS_MODULES:
        monkeypatch.delitem(sys.modules, name, raising=False)
    yield
    for name in _WS_MODULES:
        sys.modules.pop(name, None)


def test_importing_session_hints_at_ws_extra(without_httpx_ws: None) -> None:  # noqa: ARG001
    """The ``ImportError`` must name ``httpx-ws`` and point at the ``[ws]`` extra."""
    with pytest.raises(ImportError) as excinfo:
        importlib.import_module('divera247.websocket.session')

    message = str(excinfo.value)
    assert 'httpx-ws' in message
    assert "'divera247[ws]'" in message


def test_importing_package_hints_at_ws_extra(without_httpx_ws: None) -> None:  # noqa: ARG001
    """Importing the package propagates the same actionable hint."""
    with pytest.raises(ImportError) as excinfo:
        importlib.import_module('divera247.websocket')

    assert "'divera247[ws]'" in str(excinfo.value)

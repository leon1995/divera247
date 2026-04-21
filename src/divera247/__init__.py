"""Async Python client for the DIVERA 24/7 REST API + WebSocket stream.

Curated public surface. Typical usage::

    from divera247 import Divera247Client, AccessKeyAuth

    async with Divera247Client(auth=AccessKeyAuth('my-key')) as client:
        alarms = await client.alarm.get_alarms()

The full endpoint set is available as lazily-instantiated attributes on
:class:`Divera247Client` (``client.alarm``, ``client.pull``,
``client.using_vehicle``, ...). See :mod:`divera247.errors` for the exception
hierarchy and :mod:`divera247.websocket` (optional ``[ws]`` extra) for the
push-event subscription.
"""

from __future__ import annotations

from divera247.auth import AccessKeyAuth, JwtAuth, RefreshingJwtAuth
from divera247.client import Divera247Client
from divera247.errors import (
    DiveraAPIError,
    DiveraAuthError,
    DiveraError,
    DiveraRateLimitError,
    DiveraValidationError,
    ensure_success,
    raise_from_response,
)

__all__ = [
    'AccessKeyAuth',
    'Divera247Client',
    'DiveraAPIError',
    'DiveraAuthError',
    'DiveraError',
    'DiveraRateLimitError',
    'DiveraValidationError',
    'JwtAuth',
    'RefreshingJwtAuth',
    'ensure_success',
    'raise_from_response',
]

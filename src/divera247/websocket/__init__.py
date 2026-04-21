"""Divera 24/7 WebSocket subpackage.

The runtime session loop depends on the optional ``httpx-ws`` package; install
it via the ``ws`` extra (``pip install 'divera247[ws]'`` / ``uv add 'divera247[ws]'``).
Importing this subpackage without the extra raises a :class:`ModuleNotFoundError`
that points at the missing extra (see :mod:`divera247.websocket.session`).

Public API:

* :func:`subscribe_websocket` - async iterator of push events with bounded
  JWT re-auth.
* :class:`WebSocketAuthenticationError` - raised when authentication keeps
  failing so the caller can react instead of silently looping.
* Pydantic event envelopes (:class:`ClusterPullEvent`,
  :class:`UserStatusEvent`, :class:`UnknownEvent`) and the
  :data:`DiveraEvent` discriminated union plus :func:`parse_event` for
  dispatching raw frames onto typed models.

Typical usage:

.. code-block:: python

    from divera247.websocket import (
        ClusterPullEvent,
        UnknownEvent,
        UserStatusEvent,
        subscribe_websocket,
    )

    async for event in subscribe_websocket(client, ucr_id=ucr_id):
        match event:
            case UserStatusEvent(payload=payload, ucr=ucr):
                ...
            case ClusterPullEvent(pull=pull):
                ...
            case UnknownEvent(type=msg_type):
                ...
"""

from divera247.websocket.models import (
    ClusterPullEvent,
    ClusterPullRef,
    DiveraEvent,
    UnknownEvent,
    UserStatusEvent,
    parse_event,
)
from divera247.websocket.session import WebSocketAuthenticationError, subscribe_websocket

__all__ = [
    'ClusterPullEvent',
    'ClusterPullRef',
    'DiveraEvent',
    'UnknownEvent',
    'UserStatusEvent',
    'WebSocketAuthenticationError',
    'parse_event',
    'subscribe_websocket',
]

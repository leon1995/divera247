"""Pydantic models for Divera 24/7 WebSocket push events."""

import logging
from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    Tag,
    TypeAdapter,
    ValidationError,
)

from divera247.models.pull import PullStatusData

logger = logging.getLogger(__name__)


class UserStatusEvent(BaseModel):
    """``user-status`` WebSocket event: own status changed for a given UCR.

    The ``payload`` has the exact same shape as the ``status`` block of
    ``GET /api/v2/pull/all`` (see :class:`PullStatusData`); the envelope
    adds the event ``type`` discriminator and the ``ucr`` of the affected
    UserClusterRelation.
    """

    type: Literal['user-status'] = Field(description='Event-Typ')
    payload: PullStatusData = Field(description='Aktueller Status der UCR')
    ucr: int = Field(description='ID der betroffenen UserClusterRelation')


class UnknownEvent(BaseModel):
    """Fallback for any WebSocket event type we don't have a dedicated model for.

    Keeps the raw ``type`` string so callers can still dispatch on it, and
    preserves every other top-level field as extras (accessible via
    :attr:`model_extra` or direct attribute access). Used both for genuinely
    unknown event types (e.g. ``cluster-pull``, ``cluster-vehicle``) and as
    a defensive fallback when a known event's inner payload fails its
    dedicated validation (see :func:`parse_event`).
    """

    model_config = ConfigDict(extra='allow')

    type: str = Field(description='Raw event type as sent by the server')


_KNOWN_EVENT_TYPES: frozenset[str] = frozenset({'user-status'})


def _event_discriminator(value: Any) -> str:
    """Return the tag under which ``value`` should be routed in :data:`DiveraEvent`.

    Known ``type`` strings tag themselves; anything else (including missing
    ``type``) falls through to ``'unknown'`` so :class:`UnknownEvent` wins
    and validation never fails on an unfamiliar event.
    """
    event_type = value.get('type') if isinstance(value, Mapping) else getattr(value, 'type', None)
    if isinstance(event_type, str) and event_type in _KNOWN_EVENT_TYPES:
        return event_type
    return 'unknown'


DiveraEvent = Annotated[
    Annotated[UserStatusEvent, Tag('user-status')] | Annotated[UnknownEvent, Tag('unknown')],
    Discriminator(_event_discriminator),
]
"""Discriminated union of every typed WebSocket event plus the catch-all.

Use :func:`parse_event` for the common case; keep this type available for
places that want to build their own :class:`pydantic.TypeAdapter`.
"""


_event_adapter: TypeAdapter[UserStatusEvent | UnknownEvent] = TypeAdapter(DiveraEvent)


def parse_event(event: Mapping[str, Any]) -> UserStatusEvent | UnknownEvent:
    """Parse a raw WebSocket event into the matching typed model.

    Dispatches on ``type`` via :data:`DiveraEvent`; unknown or missing types
    fall back to :class:`UnknownEvent` instead of raising, so the subscribe
    loop never dies on a newly introduced server-side event name.

    If a frame carries a known ``type`` but its nested payload fails the
    dedicated validation (e.g. the server changed the wire format in a way
    we don't yet model), this also falls back to :class:`UnknownEvent` and
    logs the raw frame at WARNING level -- the subscribe loop keeps
    yielding events instead of dying on a single unexpected shape, and
    the log line gives you everything needed to update the typed model.

    Frames that are missing a ``type`` field entirely (or whose ``type`` is
    not a string) are still rejected, since they are malformed and cannot
    be routed to any model, not even :class:`UnknownEvent`.
    """
    try:
        return _event_adapter.validate_python(event)
    except ValidationError:
        event_type = event.get('type') if isinstance(event, Mapping) else None
        if not isinstance(event_type, str) or not event_type:
            raise
        logger.warning(
            'failed to validate %r WebSocket event against its typed model; '
            'falling back to UnknownEvent. raw frame: %r',
            event_type,
            dict(event),
        )
        return UnknownEvent.model_validate(event)

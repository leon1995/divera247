"""Pydantic models for Divera 24/7 WebSocket push events."""

from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, TypeAdapter

from divera247.models.pull import PullStatusData


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


class ClusterPullRef(BaseModel):
    """Reference to the specific cluster sub-resource that changed."""

    type: str = Field(description='Name des betroffenen Pull-Blocks')
    id: int = Field(description='ID des geänderten Eintrags')


class ClusterPullEvent(BaseModel):
    """``cluster-pull`` WebSocket event: a cluster resource was updated.

    Clients use this as a hint to re-fetch the affected block via
    ``GET /api/v2/pull/all`` (or the matching scoped endpoint) to obtain the
    new state. The event itself only carries the reference, not the payload.
    """

    type: Literal['cluster-pull'] = Field(description='Event-Typ')
    pull: ClusterPullRef = Field(description='Referenz auf das geänderte Element')
    cluster: int = Field(description='ID der betroffenen Einheit')


class UnknownEvent(BaseModel):
    """Fallback for any WebSocket event type we don't have a dedicated model for.

    Keeps the raw ``type`` string so callers can still dispatch on it, and
    preserves every other top-level field as extras (accessible via
    :attr:`model_extra` or direct attribute access). Use this to log
    previously unseen event types so dedicated models can be added later.
    """

    model_config = ConfigDict(extra='allow')

    type: str = Field(description='Raw event type as sent by the server')


_KNOWN_EVENT_TYPES: frozenset[str] = frozenset({'user-status', 'cluster-pull'})


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
    Annotated[UserStatusEvent, Tag('user-status')]
    | Annotated[ClusterPullEvent, Tag('cluster-pull')]
    | Annotated[UnknownEvent, Tag('unknown')],
    Discriminator(_event_discriminator),
]
"""Discriminated union of every typed WebSocket event plus the catch-all.

Use :func:`parse_event` for the common case; keep this type available for
places that want to build their own :class:`pydantic.TypeAdapter`.
"""


_event_adapter: TypeAdapter[UserStatusEvent | ClusterPullEvent | UnknownEvent] = TypeAdapter(
    DiveraEvent,
)


def parse_event(event: Mapping[str, Any]) -> UserStatusEvent | ClusterPullEvent | UnknownEvent:
    """Parse a raw WebSocket event into the matching typed model.

    Dispatches on ``type`` via :data:`DiveraEvent`; unknown or missing types
    fall back to :class:`UnknownEvent` instead of raising, so the subscribe
    loop never dies on a newly introduced server-side event name.
    """
    return _event_adapter.validate_python(event)

"""Pydantic models for Divera 24/7 WebSocket push events."""

import datetime
import logging
from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import (
    AliasPath,
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


class ClusterPullRef(BaseModel):
    """Reference to the cluster resource that triggered a ``cluster-pull`` event.

    The ``type`` names the resource family (observed: ``alarm``; likely
    also ``message``, ``event``, ``news``, ``vehicle``, etc., i.e. the
    same families exposed by ``GET /api/v2/pull/all``) and ``id`` is the
    primary key within that family. Callers should re-fetch the matching
    pull endpoint to get the full object.
    """

    model_config = ConfigDict(extra='allow')

    type: str = Field(description='Ressource-Typ, der neu gepullt werden soll (z. B. ``alarm``)')
    id: int = Field(description='ID der betroffenen Ressource innerhalb ihres Typs')


class ClusterPullEvent(BaseModel):
    """``cluster-pull`` WebSocket event: a cluster-scoped resource changed.

    The server tells us *that* something in a given cluster changed and
    *which* resource to refresh (type + id). The actual object is not
    inlined; the client is expected to re-fetch the relevant pull
    endpoint to materialise the update.

    Wire format, mirroring :class:`UserStatusEvent`:

    .. code-block:: json

        {
          "type": "cluster-pull",
          "payload": {
            "type": "cluster-pull",
            "pull": {"type": "alarm", "id": 1234},
            "cluster": 1234
          }
        }

    Flattened via :class:`~pydantic.AliasPath` so callers access
    ``event.pull`` / ``event.cluster`` directly.
    """

    type: Literal['cluster-pull'] = Field(description='Event-Typ')
    pull: ClusterPullRef = Field(
        validation_alias=AliasPath('payload', 'pull'),
        description='Referenz auf die geänderte Ressource (aus payload.pull)',
    )
    cluster: int = Field(
        validation_alias=AliasPath('payload', 'cluster'),
        description='ID des betroffenen Clusters (aus payload.cluster)',
    )


class ClusterVehicleState(BaseModel):
    """Vehicle status snapshot carried by a ``cluster-vehicle`` event."""

    model_config = ConfigDict(extra='allow')

    id: int = Field(description='ID des betroffenen Fahrzeugs')
    fmsstatus_id: int = Field(description='Aktuelle FMS-Status-ID')
    fmsstatus_note: str = Field(description='Optionaler Freitext zum FMS-Status')
    fmsstatus_ts: datetime.datetime = Field(description='Zeitpunkt der letzten Statusaenderung')


class ClusterVehicleEvent(BaseModel):
    """``cluster-vehicle`` WebSocket event: vehicle status changed in a cluster.

    Wire format:

    .. code-block:: json

        {
          "type": "cluster-vehicle",
          "payload": {
            "type": "cluster-vehicle",
            "vehicle": {
              "id": 1234,
              "fmsstatus_id": 6,
              "fmsstatus_note": "",
              "fmsstatus_ts": 1700000000
            },
            "cluster": 1234
          }
        }
    """

    type: Literal['cluster-vehicle'] = Field(description='Event-Typ')
    vehicle: ClusterVehicleState = Field(
        validation_alias=AliasPath('payload', 'vehicle'),
        description='Aktueller Fahrzeugstatus (aus payload.vehicle)',
    )
    cluster: int = Field(
        validation_alias=AliasPath('payload', 'cluster'),
        description='ID des betroffenen Clusters (aus payload.cluster)',
    )


class ClusterMonitorEvent(BaseModel):
    """``cluster-monitor`` WebSocket event with monitor counters per status.

    ``monitor`` mirrors the structure from ``pull/all`` monitor data:
    group/category -> status_id -> bucket map (e.g. ``all`` + ``qualification``).
    """

    model_config = ConfigDict(extra='allow')

    type: Literal['cluster-monitor'] = Field(description='Event-Typ')
    monitor: Mapping[str, Any] = Field(
        validation_alias=AliasPath('payload', 'monitor'),
        description='Monitor-Daten je Gruppe und Status (aus payload.monitor)',
    )
    cluster: int = Field(
        validation_alias=AliasPath('payload', 'cluster'),
        description='ID des betroffenen Clusters (aus payload.cluster)',
    )


class UserStatusEvent(BaseModel):
    """``user-status`` WebSocket event: own status changed for a given UCR.

    The server wire-format wraps the actual status (same fields as the
    ``status`` block of ``GET /api/v2/pull/all`` -- see
    :class:`PullStatusData`) and the affected ``ucr`` inside a nested
    ``payload`` object, with the event type repeated redundantly at both
    levels:

    .. code-block:: json

        {
          "type": "user-status",
          "payload": {
            "type": "user-status",
            "status": { ...PullStatusData... },
            "ucr": 1234
          }
        }

    We flatten this on validation via :class:`~pydantic.AliasPath`, so
    callers only deal with ``event.status`` / ``event.ucr`` and never have
    to reach through a redundant payload wrapper.
    """

    type: Literal['user-status'] = Field(description='Event-Typ')
    status: PullStatusData = Field(
        validation_alias=AliasPath('payload', 'status'),
        description='Aktueller Status der UCR (aus payload.status)',
    )
    ucr: int = Field(
        validation_alias=AliasPath('payload', 'ucr'),
        description='ID der betroffenen UserClusterRelation (aus payload.ucr)',
    )


class UnknownEvent(BaseModel):
    """Fallback for any WebSocket event type we don't have a dedicated model for.

    Keeps the raw ``type`` string so callers can still dispatch on it, and
    preserves every other top-level field as extras (accessible via
    :attr:`model_extra` or direct attribute access). Used both for genuinely
    unknown event types and as a defensive fallback when a known event's
    inner payload fails its dedicated validation (see :func:`parse_event`).
    """

    model_config = ConfigDict(extra='allow')

    type: str = Field(description='Raw event type as sent by the server')


_KNOWN_EVENT_TYPES: frozenset[str] = frozenset({'user-status', 'cluster-pull', 'cluster-vehicle', 'cluster-monitor'})


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
    | Annotated[ClusterVehicleEvent, Tag('cluster-vehicle')]
    | Annotated[ClusterMonitorEvent, Tag('cluster-monitor')]
    | Annotated[UnknownEvent, Tag('unknown')],
    Discriminator(_event_discriminator),
]
"""Discriminated union of every typed WebSocket event plus the catch-all.

Use :func:`parse_event` for the common case; keep this type available for
places that want to build their own :class:`pydantic.TypeAdapter`.
"""


_event_adapter: TypeAdapter[
    UserStatusEvent | ClusterPullEvent | ClusterVehicleEvent | ClusterMonitorEvent | UnknownEvent
] = TypeAdapter(DiveraEvent)


def parse_event(
    event: Mapping[str, Any],
) -> UserStatusEvent | ClusterPullEvent | ClusterVehicleEvent | ClusterMonitorEvent | UnknownEvent:
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

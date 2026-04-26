"""Pydantic models for Divera 24/7 event API.

These models map to the schemas defined in ``api_v2_event.yaml``.
"""

import datetime
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

from divera247.models.alarm import JsonPayload


class EventResult(BaseModel):
    """Event result schema (event-result)."""

    id: int | None = Field(default=None, description='ID/Primärschlüssel')
    foreign_id: str | None = Field(default=None, description='Fremdschlüssel')
    author_id: int | None = Field(default=None, description='ID des Nutzers')
    date: datetime.datetime | None = Field(default=None, description='Terminszeit als UNIX-Timestamp')
    title: str | None = Field(default=None, description='Titel')
    text: str | None = Field(default=None, description='Meldung')
    address: str | None = Field(default=None, description='Ort')
    cluster: Sequence[int] | None = Field(default=None, description='IDs der Standorte')
    group: Sequence[int] | None = Field(default=None, description='IDs der Gruppen')
    user_cluster_relation: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer',
    )
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    notification_type: int | None = Field(
        default=None,
        description='Empfänger-Auswahl (1-4)',
    )
    new: bool | None = Field(default=None, description='Neu/Ungelesen')
    editable: bool | None = Field(default=None, description='Bearbeitbar')
    answerable: bool | None = Field(default=None, description='Beantwortbar')
    hidden: bool | None = Field(default=None, description='Entwurf')
    deleted: bool | None = Field(default=None, description='Im Archiv')
    ts_create: datetime.datetime | None = Field(default=None, description='UNIX-Timestamp Erstelldatum')
    ts_update: datetime.datetime | None = Field(
        default=None,
        description='UNIX-Timestamp zuletzt bearbeitet',
    )


class EventsData(BaseModel):
    """Data payload for GET /api/v2/events."""

    items: Mapping[str, EventResult] = Field(
        default_factory=dict,
        description='Termine nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Reihenfolge der Termine, absteigend',
    )


class EventsResponse(BaseModel):
    """Response schema for GET /api/v2/events."""

    success: bool = Field(description='Whether the request succeeded')
    data: EventsData | None = Field(default=None, description='Events payload')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class EventSingleResponse(BaseModel):
    """Response schema for GET/POST/PUT /api/v2/events/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: EventResult | None = Field(default=None, description='Event data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class ReachData(BaseModel):
    """Reach data for GET /api/v2/events/reach/{id}."""

    transports: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Abgeschlossene Versand-Prozesse',
    )
    received: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Benachrichtigung erhalten',
    )
    viewed: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Meldung gelesen',
    )
    confirmed: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Aktive Rückmeldung',
    )


class ReachResponse(BaseModel):
    """Response schema for GET /api/v2/events/reach/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: ReachData | None = Field(default=None, description='Reach data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class EventInputEvent(BaseModel):
    """Event object for create/update (event-input.Event)."""

    foreign_id: str | None = Field(default=None, description='Fremdschlüssel')
    title: str = Field(description='Titel')
    text: str | None = Field(default=None, description='Meldung')
    address: str | None = Field(default=None, description='Ort')
    ts_start: datetime.datetime | None = Field(
        default=None,
        description='Beginn als UNIX-Timestamp',
    )
    ts_end: datetime.datetime | None = Field(
        default=None,
        description='Ende als UNIX-Timestamp',
    )
    fullday: bool | None = Field(
        default=None,
        description='ganztägiger Termin',
    )
    days: int | None = Field(default=None, description='Dauer in Tagen')
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    notification_type: int = Field(
        description='Empfänger-Auswahl (1-4)',
    )
    send_push: bool | None = Field(default=None, description='Push senden')
    send_sms: bool | None = Field(default=None, description='SMS senden')
    send_call: bool | None = Field(default=None, description='Sprachanruf senden')
    send_mail: bool | None = Field(default=None, description='E-Mail senden')
    send_pager: bool | None = Field(default=None, description='Pager senden')
    group: Sequence[int] | None = Field(default=None, description='IDs der Gruppen')
    user_cluster_relation: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer',
    )
    cluster: Mapping[str, Mapping[str, int]] | None = Field(
        default=None,
        description='Cluster config (PRO)',
    )


class EventInputReminder(BaseModel):
    """Reminder for event (event-input.Reminder)."""

    ts: datetime.datetime | None = Field(
        default=None,
        description='Zeitpunkt als UNIX-Timestamp',
    )
    send_push: bool | None = Field(default=None, description='Push als Erinnerung')
    send_mail: bool | None = Field(default=None, description='E-Mail als Erinnerung')


class EventInput(BaseModel):
    """Request body for creating/updating events (event-input)."""

    Event: EventInputEvent = Field(description='Event data')
    Reminder: EventInputReminder | None = Field(
        default=None,
        description='Erinnerung',
    )
    using_groups: Sequence[int] | None = Field(
        default=None,
        description='IDs der Gruppen',
    )
    using_user_cluster_relations: Sequence[int] | None = Field(
        default=None,
        description='IDs der UCRs',
    )
    instructions: Mapping[str, Mapping[str, str]] | None = Field(
        default=None,
        description='Mapping instructions',
    )


class EventConfirmEvent(BaseModel):
    """Event object for POST /api/v2/events/confirm/{id}."""

    participation: int | None = Field(
        default=None,
        description='Rückmeldung (1=Ja, 2=Unsicher, 3=Nein)',
    )
    custom_answer: str | None = Field(
        default=None,
        description='Freitext-Rückmeldung',
    )


class EventConfirmPayload(BaseModel):
    """Request body for POST /api/v2/events/confirm/{id}."""

    Event: EventConfirmEvent | None = Field(
        default=None,
        description='Confirm options',
    )

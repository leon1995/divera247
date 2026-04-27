"""Pydantic models for Divera 24/7 event API.

These models map to the schemas defined in ``api_v2_event.yaml``.
"""

import datetime
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

from divera247.models.alarm import JsonPayload


class EventResult(BaseModel):
    """Event result schema (event-result)."""

    class EventReminder(BaseModel):
        """Reminder details in event result."""

        notification_filter: int | None = Field(default=None, description='Benachrichtigungsfilter')
        ts: datetime.datetime | None = Field(default=None, description='UNIX-Timestamp Erinnerung')
        send_push: bool | None = Field(default=None, description='Push-Erinnerung aktiv')
        send_mail: bool | None = Field(default=None, description='Mail-Erinnerung aktiv')
        executed: bool | None = Field(default=None, description='Erinnerung bereits ausgeführt')

    id: int | None = Field(default=None, description='ID/Primärschlüssel')
    foreign_id: str | None = Field(default=None, description='Fremdschlüssel')
    author_id: int | None = Field(default=None, description='ID des Nutzers')
    cluster_id: int | None = Field(default=None, description='ID der Einheit')
    message_channel_id: int | None = Field(default=None, description='ID des Nachrichtenkanals')
    date: datetime.datetime | None = Field(default=None, description='Datum als UNIX-Timestamp')
    start: datetime.datetime | None = Field(default=None, description='Beginn als UNIX-Timestamp')
    end: datetime.datetime | None = Field(default=None, description='Ende als UNIX-Timestamp')
    title: str | None = Field(default=None, description='Titel')
    text: str | None = Field(default=None, description='Meldung')
    address: str | None = Field(default=None, description='Ort')
    lat: float | int | None = Field(default=None, description='Breitengrad')
    lng: float | int | None = Field(default=None, description='Längengrad')
    fullday: bool | None = Field(default=None, description='Ganztägiger Termin')
    days: int | None = Field(default=None, description='Dauer in Tagen')
    archive: bool | None = Field(default=None, description='Archiviert')
    ts_archive: datetime.datetime | None = Field(default=None, description='Archiv-Zeitpunkt')
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
    custom_answers: bool | None = Field(default=None, description='Eigene Antwortoptionen aktiv')
    participation: int | None = Field(
        default=None,
        description='Eigene Rückmeldung (1=Ja, 2=Unsicher, 3=Nein)',
    )
    note: str | None = Field(default=None, description='Eigene Freitext-Rückmeldung')
    show_result_count: int | None = Field(default=None, description='Ergebnisanzeige Anzahl')
    show_result_names: int | None = Field(default=None, description='Ergebnisanzeige Namen')
    count_recipients: int | None = Field(default=None, description='Anzahl Empfänger')
    count_read: int | None = Field(default=None, description='Anzahl Gelesen')
    ucr_addressed: Sequence[int] | None = Field(default=None, description='Adressierte Benutzer')
    ucr_self_addressed: bool | None = Field(default=None, description='Selbst adressiert')
    ucr_read: Sequence[int] | None = Field(default=None, description='Lesende Benutzer')
    hidden: bool | None = Field(default=None, description='Entwurf')
    deleted: bool | None = Field(default=None, description='Im Archiv')
    message_channel: bool | None = Field(default=None, description='Ist Nachrichtenkanal')
    attachment_count: int | None = Field(default=None, description='Anzahl Anhänge')
    response_type: int | None = Field(default=None, description='Rückmeldetyp')
    response_until: bool | None = Field(default=None, description='Rückmeldung zeitlich begrenzt')
    ts_response: datetime.datetime | None = Field(default=None, description='Rückmeldung bis')
    send_reminder: bool | None = Field(default=None, description='Erinnerung senden')
    access_names: bool | None = Field(default=None, description='Namen sichtbar')
    access_count: bool | None = Field(default=None, description='Anzahl sichtbar')
    participationlist: Mapping[str, Sequence[int]] | None = Field(
        default=None,
        description='Rückmeldungen nach Antwortoption',
    )
    participationcount: Mapping[str, int] | None = Field(
        default=None,
        description='Anzahl Rückmeldungen nach Antwortoption',
    )
    participationnotes: Sequence[JsonPayload] | None = Field(
        default=None,
        description='Freitext-Rückmeldungen',
    )
    multiple_answers: bool | None = Field(default=None, description='Mehrfachauswahl möglich')
    send_push: bool | None = Field(default=None, description='Push senden')
    send_sms: bool | None = Field(default=None, description='SMS senden')
    send_call: bool | None = Field(default=None, description='Sprachanruf senden')
    send_mail: bool | None = Field(default=None, description='E-Mail senden')
    send_pager: bool | None = Field(default=None, description='Pager senden')
    ucr_answered: Sequence[int] | Mapping[str, JsonPayload] | None = Field(
        default=None,
        description='Rückmeldende Benutzer',
    )
    reminder: EventReminder | None = Field(default=None, description='Erinnerung')
    ts_publish: datetime.datetime | None = Field(default=None, description='Veröffentlichungszeitpunkt')
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

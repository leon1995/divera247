"""Pydantic models for Divera 24/7 alarm API.

These models map to the schemas defined in ``api_v2_alarm.yaml``:
``success``, ``alarm-result``, and ``alarm-input``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

# JSON-serializable types for dynamic API payloads (avoids Any)
# Uses object as values since reach/success payloads have nested structures
JsonPayload = Mapping[str, int | float | str | bool | None | Sequence[object] | Mapping[str, object]]


class SuccessResponse(BaseModel):
    """Success response schema."""

    success: bool = Field(description='Whether the request succeeded')
    ucr: int | None = Field(
        default=None,
        description='ID of the UserClusterRelation in the current request',
    )
    data: JsonPayload | None = Field(
        default=None,
        description='Data payload',
    )


class UcrAnsweredEntry(BaseModel):
    """Single user response entry in ucr_answered (status_id -> ucr_id -> this)."""

    ts: int = Field(description='UNIX timestamp of response')
    note: str = Field(default='', description='Freitext-Rückmeldung')


class AlarmsData(BaseModel):
    """Data payload for GET /api/v2/alarms.

    :param items: Alarms by ID.
    :param sorting: Order of alarms, ascending.
    """

    items: Mapping[str, AlarmResult] = Field(
        default_factory=dict,
        description='Alarms by ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Order of alarms, ascending',
    )


class AlarmsResponse(BaseModel):
    """Response schema for GET /api/v2/alarms.

    :param success: Whether the request succeeded.
    :param data: Alarms payload with items and sorting.
    :param ucr: ID of the UserClusterRelation in the current request.
    """

    success: bool = Field(description='Whether the request succeeded')
    data: AlarmsData | None = Field(
        default=None,
        description='Alarms payload',
    )
    ucr: int | None = Field(
        default=None,
        description='ID of the UserClusterRelation in the current request',
    )


class AlarmSingleResponse(BaseModel):
    """Response schema for GET/POST/PUT /api/v2/alarms/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: AlarmResult | None = Field(default=None, description='Alarm data')
    ucr: int | None = Field(
        default=None,
        description='ID of the UserClusterRelation in the current request',
    )


class AlarmsListResponse(BaseModel):
    """Response schema for GET /api/v2/alarms/list."""

    success: bool = Field(description='Whether the request succeeded')
    data: Sequence[AlarmResult] = Field(
        default_factory=tuple,
        description='List of alarms',
    )
    ucr: int | None = Field(
        default=None,
        description='ID of the UserClusterRelation in the current request',
    )


class ReachTransports(BaseModel):
    """Reach transports for GET /api/v2/alarms/reach/{id}."""

    id: int = Field(description='ID of the transport')
    notification_type: int = Field(description='Notification type')
    count_send: int = Field(description='Count of send')
    ts: int = Field(description='UNIX timestamp of the transport')


class ReachReceived(BaseModel):
    """Reach received for GET /api/v2/alarms/reach/{id}."""

    id: int = Field(description='ID of the received')
    log_notification_transport_id: int = Field(description='ID of the notification transport')
    notification_product: str = Field(description='Notification product')
    user_device_token_id: int = Field(description='ID of the user device token')
    user_phonenumber_cluster_id: int = Field(description='ID of the user phonenumber cluster')


class ReachViewed(BaseModel):
    """Reach viewed for GET /api/v2/alarms/reach/{id}."""

    id: int = Field(description='ID of the viewed')
    ts: int = Field(description='UNIX timestamp of the viewed')


class ReachConfirmed(BaseModel):
    """Reach confirmed for GET /api/v2/alarms/reach/{id}."""

    id: int = Field(description='ID of the confirmed')
    ts: int = Field(description='UNIX timestamp of the confirmed')
    note: str = Field(description='Note of the confirmed')


class ReachData(BaseModel):
    """Reach data for GET /api/v2/alarms/reach/{id}."""

    transports: Mapping[str, ReachTransports] = Field(
        default_factory=dict,
        description='Abgeschlossene Versand-Prozesse',
    )
    received: Mapping[str, ReachReceived] = Field(
        default_factory=dict,
        description='Benachrichtigung erhalten (Push/Pager/SMS/Anruf)',
    )
    viewed: Mapping[str, ReachViewed] = Field(
        default_factory=dict,
        description='Meldung gelesen',
    )
    confirmed: Mapping[str, ReachConfirmed] = Field(
        default_factory=dict,
        description='Aktive Rückmeldung',
    )


class ReachResponse(BaseModel):
    """Response schema for GET /api/v2/alarms/reach/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: ReachData | None = Field(default=None, description='Reach data')
    ucr: int | None = Field(
        default=None,
        description='ID of the UserClusterRelation in the current request',
    )


class AlarmResultCustomItem(BaseModel):
    """Custom data point attached to an alarm.

    :param key: Unique key of the data point (1-64 chars).
    :param title: Title of the data point (1-255 chars).
    :param value: Value of the data point (0-64000 chars).
    """

    key: str = Field(description='Unique key of the data point', min_length=1, max_length=64)
    title: str = Field(description='Title of the data point', min_length=1, max_length=255)
    value: str = Field(description='Value of the data point', min_length=0, max_length=64000)


class AlarmResult(BaseModel):
    """Alarm result schema (alarm-result).

    Structure returned by GET /api/v2/alarms, /api/v2/alarms/{id}, etc.
    """

    id: int | None = Field(default=None, description='ID/Primärschlüssel')
    foreign_id: str | None = Field(
        default=None,
        description='Einsatznummer/Fremdschlüssel',
    )
    author_id: int | None = Field(
        default=None,
        description='ID des Nutzers (UserClusterRelation)',
    )
    alarmcode_id: int | None = Field(
        default=None,
        description='ID der Alarmvorlage (Alarmcode)',
    )
    date: int | None = Field(
        default=None,
        description='Alarmierungszeit als UNIX-Timestamp',
    )
    priority: bool | None = Field(default=None, description='Priorität/Sonderrechte')
    title: str | None = Field(default=None, description='Stichwort')
    text: str | None = Field(default=None, description='Meldung')
    address: str | None = Field(default=None, description='Einsatzort')
    lat: float | None = Field(default=None, description='Breitengrad')
    lng: float | None = Field(default=None, description='Längengrad')
    scene_object: str | None = Field(
        default=None,
        description='Angaben zum Objekt/Gebäude',
    )
    caller: str | None = Field(default=None, description='Angaben zur meldenden Personen')
    patient: str | None = Field(default=None, description='Angaben zum Patienten')
    remark: str | None = Field(
        default=None,
        description='Bemerkungen/Hinweise für die Einsatzkräfte',
    )
    units: str | None = Field(default=None, description='Beteiligte Einsatzmittel')
    destination: bool | None = Field(default=None, description='Gibt es ein Fahrtziel?')
    destination_address: str | None = Field(
        default=None,
        description='Adresse des Fahrtziels',
    )
    destination_lat: float | None = Field(
        default=None,
        description='Breitengrad des Fahrtziels',
    )
    destination_lng: float | None = Field(
        default=None,
        description='Längengrad des Fahrtziels',
    )
    additional_text_1: str | None = Field(default=None, description='Zusatz 1')
    additional_text_2: str | None = Field(default=None, description='Zusatz 2')
    additional_text_3: str | None = Field(default=None, description='Zusatz 3')
    report: str | None = Field(default=None, description='Einsatzbericht')
    cluster: Sequence[int] | None = Field(
        default=None,
        description='IDs der Standorte (bedingt notification_type = 1)',
    )
    group: Sequence[int] | None = Field(
        default=None,
        description='IDs der Gruppen (bedingt notification_type = 1 oder 3)',
    )
    user_cluster_relation: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer (bedingt notification_type = 1 oder 4)',
    )
    vehicle: Sequence[int] | None = Field(
        default=None,
        description='IDs der Fahrzeuge/Einsatzmittel',
    )
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    notification_type: int | None = Field(
        default=None,
        description='Empfänger-Auswahl (1-4)',
    )
    notification_filter_vehicle: bool | None = Field(
        default=None,
        description='Nur Personen alarmieren, die sich auf einem zugeteilten Fahrzeuge befinden',
    )
    notification_filter_status: bool | None = Field(
        default=None,
        description='Nur Personen alarmieren, die sich in einem bestimmten Status befinden',
    )
    notification_filter_access: bool | None = Field(
        default=None,
        description='Einsatz auch für nicht benachrichtigte Empfänger sichtbar machen',
    )
    notification_filter_status_ids: Sequence[int] | None = Field(
        default=None,
        description='IDs der ausgewählten Status (notification_filter_status = TRUE)',
    )
    send_push: bool | None = Field(
        default=None,
        description='Push-Nachricht an die App senden',
    )
    send_sms: bool | None = Field(default=None, description='SMS senden')
    send_call: bool | None = Field(default=None, description='Sprachanruf senden')
    send_mail: bool | None = Field(default=None, description='E-Mail senden')
    send_pager: bool | None = Field(
        default=None,
        description='An verknüpfte Pager senden',
    )
    response_time: int | None = Field(
        default=None,
        description='Rückmeldung innerhalb des Zeitraums in Minuten',
    )
    closed: bool | None = Field(default=None, description='Einsatz beendet')
    new: bool | None = Field(default=None, description='Neu/Ungelesen')
    editable: bool | None = Field(default=None, description='Bearbeitbar')
    answerable: bool | None = Field(default=None, description='Beantwortbar')
    hidden: bool | None = Field(default=None, description='Entwurf')
    deleted: bool | None = Field(
        default=None,
        description='Im Archiv, nur noch für Schreibberechtigte zugänglich',
    )
    ucr_adressed: Sequence[int] | None = Field(
        default=None,
        description='Adressierte Benutzer',
    )
    ucr_answered: Mapping[str, Mapping[str, UcrAnsweredEntry]] | None = Field(
        default=None,
        description='Rückmeldungen (status_id -> ucr_id -> {ts, note})',
    )
    ucr_self_addressed: bool | None = Field(
        default=None,
        description='Selbst adressiert, Rückmeldung ist möglich',
    )
    ucr_self_status_id: int | None = Field(
        default=None,
        description='Eigene Rückmeldung (ID des Status)',
    )
    ucr_self_note: str | None = Field(
        default=None,
        description='Eigene Rückmeldung (Freitext)',
    )
    count_recipients: int | None = Field(
        default=None,
        description='Anzahl der Empfänger',
    )
    count_read: int | None = Field(default=None, description='Anzahl gelesen')
    ts_response: int | None = Field(
        default=None,
        description='Berechneter UNIX-Timestamp für Rückmeldung bis',
    )
    ts_publish: int | None = Field(
        default=None,
        description='UNIX-Timestamp für zeitgesteuerte Alarmierung',
    )
    ts_close: int | None = Field(
        default=None,
        description='UNIX-Timestamp Einsatzende',
    )
    ts_create: int | None = Field(
        default=None,
        description='UNIX-Timestamp des Erstelldatums',
    )
    ts_update: int | None = Field(
        default=None,
        description='UNIX-Timestamp zuletzt bearbeitet',
    )
    notification_filter_status_access: bool | None = Field(
        default=None,
        description='deprecated, use notification_filter_access',
    )
    custom: Sequence[AlarmResultCustomItem] | None = Field(
        default=None,
        description='Weitere Daten im Zusammenhang mit der Operation',
    )
    cluster_id: int | None = Field(default=None, description='ID des Clusters/Standorts')
    message_channel_id: int | None = Field(default=None, description='ID des Nachrichtenkanals')
    message_channel: bool | None = Field(default=None, description='Nachrichtenkanal aktiv')
    custom_answers: bool | None = Field(default=None, description='Eigene Rückmeldungsoptionen')
    attachment_count: int | None = Field(default=None, description='Anzahl Anhänge')
    close_state: int | None = Field(default=None, description='Zustand geschlossen (0/1)')
    duration: str | None = Field(
        default=None,
        description="Einsatzdauer (z.B. '35 Minuten')",
    )
    ucr_addressed: Sequence[int] | None = Field(
        default=None,
        description='Adressierte Benutzer (API spelling)',
    )
    ucr_answeredcount: Mapping[str, int] | None = Field(
        default=None,
        description='Anzahl Rückmeldungen pro Status (status_id -> count)',
    )
    ucr_read: Sequence[int] | None = Field(
        default=None,
        description='Benutzer die gelesen haben',
    )
    notification_filter_shift_plan: int | None = Field(
        default=None,
        description='Statusplan-Filter',
    )


class AlarmClusterConfig(BaseModel):
    """Per-cluster config for alarm-input.Alarm.cluster (PRO, notification_type=1)."""

    notification_type: int = Field(
        description='Empfänger-Auswahl innerhalb der Untereinheit (2-4)',
    )


class AlarmInputAlarm(BaseModel):
    """Alarm object for create/update (alarm-input.Alarm)."""

    foreign_id: str | None = Field(
        default=None,
        description='Einsatznummer/Fremdschlüssel',
    )
    alarmcode_id: float | None = Field(
        default=None,
        description='ID der Alarmvorlage',
    )
    priority: bool | None = Field(default=None, description='Priorität/Sonderrechte')
    title: str = Field(description='Stichwort')
    text: str | None = Field(default=None, description='Meldung')
    address: str | None = Field(default=None, description='Einsatzort')
    lat: float | None = Field(default=None, description='Breitengrad')
    lng: float | None = Field(default=None, description='Längengrad')
    scene_object: str | None = Field(
        default=None,
        description='Angaben zum Objekt/Gebäude',
    )
    caller: str | None = Field(default=None, description='Angaben zur meldenden Personen')
    patient: str | None = Field(default=None, description='Angaben zum Patienten')
    remark: str | None = Field(
        default=None,
        description='Bemerkungen/Hinweise für die Einsatzkräfte',
    )
    units: str | None = Field(default=None, description='Beteiligte Einsatzmittel')
    destination: bool | None = Field(default=None, description='Gibt es ein Fahrtziel?')
    destination_address: str | None = Field(
        default=None,
        description='Adresse des Fahrtziels',
    )
    destination_lat: float | None = Field(
        default=None,
        description='Breitengrad des Fahrtziels',
    )
    destination_lng: float | None = Field(
        default=None,
        description='Längengrad des Fahrtziels',
    )
    additional_text_1: str | None = Field(default=None, description='Zusatz 1')
    additional_text_2: str | None = Field(default=None, description='Zusatz 2')
    additional_text_3: str | None = Field(default=None, description='Zusatz 3')
    report: str | None = Field(default=None, description='Einsatzbericht')
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    notification_type: int = Field(
        description='Empfänger-Auswahl (1-4)',
    )
    notification_filter_vehicle: bool | None = Field(
        default=None,
        description='Nur Personen alarmieren auf zugeteilten Fahrzeugen',
    )
    notification_filter_status: bool | None = Field(
        default=None,
        description='Nur Personen in bestimmtem Status alarmieren',
    )
    notification_filter_access: bool | None = Field(
        default=None,
        description='Einsatz auch für nicht alarmierte sichtbar',
    )
    send_push: bool | None = Field(
        default=None,
        description='Push-Nachricht senden',
    )
    send_sms: bool | None = Field(default=None, description='SMS senden')
    send_call: bool | None = Field(default=None, description='Sprachanruf senden')
    send_mail: bool | None = Field(default=None, description='E-Mail senden')
    send_pager: bool | None = Field(default=None, description='Pager senden')
    response_time: float | None = Field(
        default=None,
        description='Rückmeldung innerhalb Sekunden',
    )
    closed: bool | None = Field(default=None, description='Einsatz beendet')
    ts_close: float | None = Field(
        default=None,
        description='Einsatzende als UNIX-Timestamp',
    )
    ts_publish: float | None = Field(
        default=None,
        description='Alarmierung zeitgesteuert nach UNIX-Timestamp',
    )
    cluster: Mapping[str, AlarmClusterConfig] | None = Field(
        default=None,
        description='Cluster config (PRO, notification_type=1)',
    )
    group: Sequence[int] | None = Field(
        default=None,
        description='IDs der Gruppen',
    )
    user_cluster_relation: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer',
    )
    vehicle: Sequence[int] | None = Field(
        default=None,
        description='IDs der Fahrzeuge',
    )
    status: Sequence[int] | None = Field(
        default=None,
        description='IDs der Status (notification_filter_status=TRUE)',
    )


class AlarmInputInstructions(BaseModel):
    """Instructions for mapping IDs/names (alarm-input.instructions)."""

    cluster: Mapping[str, str] | None = Field(
        default=None,
        description='Mögliche Werte: id, title',
    )
    group: Mapping[str, str] | None = Field(
        default=None,
        description='Mögliche Werte: id, title',
    )
    user_cluster_relation: Mapping[str, str] | None = Field(
        default=None,
        description='Mögliche Werte: id, foreign_id, status_id',
    )
    vehicle: Mapping[str, str] | None = Field(
        default=None,
        description='Mögliche Werte: id, name, number, ric, issi, opta, fmsstatus_id',
    )


class AlarmInput(BaseModel):
    """Request body for creating/updating alarms (alarm-input)."""

    Alarm: AlarmInputAlarm = Field(description='Alarm data')
    Instructions: AlarmInputInstructions | None = Field(
        default=None,
        description='Mapping instructions for groups, users, vehicles',
    )


class ConfirmStatus(BaseModel):
    """Status object for POST /api/v2/alarms/confirm/{id}."""

    id: int = Field(description='ID des Status')
    note: str | None = Field(default=None, description='Freitext-Rückmeldung')


class ConfirmPayload(BaseModel):
    """Request body for POST /api/v2/alarms/confirm/{id}."""

    Status: ConfirmStatus = Field(description='Status for the response')


class CloseAlarmData(BaseModel):
    """Alarm object for POST /api/v2/alarms/close/{id}."""

    closed: bool | None = Field(
        default=None,
        description='Zustand geschlossen oder geöffnet',
    )
    report: str | None = Field(default=None, description='Einsatzbericht')
    ts: int | None = Field(
        default=None,
        description='Datum/Uhrzeit als Unix-Timestamp',
    )


class CloseAlarmPayload(BaseModel):
    """Request body for POST /api/v2/alarms/close/{id}."""

    Alarm: CloseAlarmData | None = Field(default=None, description='Close options')

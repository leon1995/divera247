"""Pydantic models for Divera 24/7 pull API.

These models map to the schemas defined in ``api_v2_pull.yaml``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from divera247.v2.models.alarm import AlarmResult
    from divera247.v2.models.event import EventResult
    from divera247.v2.models.message import MessageResult
    from divera247.v2.models.message_channel import MessageChannelResult
    from divera247.v2.models.news import NewsResult


class UcrEntry(BaseModel):
    """Single UserClusterRelation in pull data."""

    model_config = ConfigDict(extra='allow')

    id: int | None = Field(default=None, description='ID der UserClusterRelation')
    usergroup_id: int | None = Field(default=None, description='ID der Benutzergruppe')
    cluster_id: int | None = Field(default=None, description='ID der Einheit')
    status_id: int | None = Field(default=None, description='ID des aktuellen Status')
    new_messages: int | None = Field(
        default=None,
        description='Anzahl neue Mitteilungen und Termine',
    )
    new_alarms: int | None = Field(default=None, description='Anzahl neue Einsätze')
    name: str | None = Field(default=None, description='Name der Einheit')
    shortname: str | None = Field(default=None, description='Abkürzung der Einheit')


class PullUser(BaseModel):
    """User settings and permissions in pull data."""

    model_config = ConfigDict(extra='allow')

    accesskey: str | None = Field(default=None, description='Zugangsschlüssel')
    firstname: str | None = Field(default=None, description='Vorname')
    lastname: str | None = Field(default=None, description='Nachname')
    shortname: str | None = Field(default=None, description='Initialen')
    email: str | None = Field(default=None, description='Benutzername/Login')
    emails: Mapping[str, str] | None = Field(
        default=None,
        description='Eigene E-Mail-Adressen',
    )
    status_default: int | None = Field(
        default=None,
        description='Persönlicher Standard-Status bei Zurücksetzen',
    )
    alarmbehaviour: int | None = Field(default=None, description='Alarmverhalten')
    alarmsound: int | None = Field(default=None, description='Alarm-Sound')
    messagesound: int | None = Field(default=None, description='Mitteilungs-Sound')
    statussound: int | None = Field(default=None, description='Status-Sound')
    hide_name_in_monitor: bool | None = Field(
        default=None,
        description='Eigenen Namen im Monitor verbergen',
    )
    push_alarm: bool | None = Field(
        default=None,
        description='Push-Benachrichtigung bei Alarmierungen',
    )
    push_message: bool | None = Field(
        default=None,
        description='Push-Benachrichtigung bei Mitteilungen',
    )
    push_message_channel: bool | None = Field(
        default=None,
        description='Push-Benachrichtigung bei Nachrichtenkanal',
    )
    push_statuschange: bool | None = Field(
        default=None,
        description='Push-Benachrichtigung bei Statusänderung',
    )
    phonenumbers: Mapping[str, object] | None = Field(
        default=None,
        description='Eigene Telefonnummern',
    )
    access: Mapping[str, object] | None = Field(
        default=None,
        description='Berechtigungen',
    )
    geofences: Sequence[Mapping[str, object]] | None = Field(
        default=None,
        description='Geofence-Konfiguration',
    )
    onboarding_tour_state: int | None = Field(
        default=None,
        description='Onboarding-Tour Status',
    )
    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )


class StatusChangeEntry(BaseModel):
    """Single entry in status.status_changes or status.status_log."""

    model_config = ConfigDict(extra='allow')

    ts: int | None = Field(default=None, description='UNIX-Timestamp')
    status: int | None = Field(default=None, description='ID des Status')
    note: str | None = Field(default=None, description='Status-Notiz')
    vehicle: int | None = Field(default=None, description='ID des Fahrzeugs')
    event: int | None = Field(default=None, description='ID des Termins')
    type: int | None = Field(default=None, description='Typ der Änderung')


class PullStatusData(BaseModel):
    """Current user status in pull data."""

    model_config = ConfigDict(extra='allow')

    status_id: int | None = Field(
        default=None,
        description='ID des aktuellen Status',
    )
    status_skip_statusplan: bool | None = Field(
        default=None,
        description='Alle Termine im Zeitraum überschreiben',
    )
    status_skip_geofence: bool | None = Field(
        default=None,
        description='Alle Geofences im Zeitraum ignorieren',
    )
    status_set_date: int | None = Field(
        default=None,
        description='UNIX-Timestamp der letzten Statusänderung',
    )
    status_reset_date: int | str | None = Field(
        default=None,
        description='Nächstes Zurücksetzen gemäß UNIX-Timestamp',
    )
    status_reset_id: int | None = Field(
        default=None,
        description='Status als nächstes zurücksetzen auf',
    )
    status_log: Sequence[StatusChangeEntry] | None = Field(
        default=None,
        description='Vorherige Status-Änderungen',
    )
    status_changes: Sequence[StatusChangeEntry] | None = Field(
        default=None,
        description='Bevorstehende Status-Änderungen',
    )
    note: str | None = Field(default=None, description='Status-Notiz')
    vehicle: int | None = Field(default=None, description='ID des aktuellen Fahrzeugs')
    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )
    cached: bool | None = Field(default=None, description='Aus Cache')


class PullItemsData(BaseModel):
    """Generic container for items + sorting + ts + new (alarm, news, events, dm)."""

    model_config = ConfigDict(extra='allow')

    items: Mapping[str, object] = Field(
        default_factory=dict,
        description='Items by ID',
    )

    @field_validator('items', mode='before')
    @classmethod
    def _coerce_items(cls, v: object) -> Mapping[str, object]:
        """Coerce empty list to dict (API returns [] when empty)."""
        if isinstance(v, list) and len(v) == 0:
            return cast('Mapping[str, object]', {})
        if isinstance(v, dict):
            return cast('Mapping[str, object]', v)
        raise ValueError('items must be dict or empty list')
    sorting: Sequence[int] = Field(
        default_factory=tuple,
        description='Reihenfolge aufsteigend',
    )
    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )
    new: int | None = Field(
        default=None,
        description='Anzahl neuer Einträge',
    )


class PullAlarmData(PullItemsData):
    """Alarms in pull data."""

    items: Mapping[str, AlarmResult] = Field(
        default_factory=dict,
        description='Alarmierungen nach ID',
    )


class PullNewsData(PullItemsData):
    """News in pull data."""

    items: Mapping[str, NewsResult] = Field(
        default_factory=dict,
        description='Mitteilungen nach ID',
    )


class PullEventsData(PullItemsData):
    """Events in pull data."""

    items: Mapping[str, EventResult] = Field(
        default_factory=dict,
        description='Termine nach ID',
    )


class PullDmData(PullItemsData):
    """Direct messages in pull data."""


class StatusPlanEntry(BaseModel):
    """Single status plan entry in pull data."""

    model_config = ConfigDict(extra='allow')

    id: int | None = Field(
        default=None,
        description='ID des UserClusterRelationStatusPlan',
    )
    status_plan_category_id: int | None = Field(
        default=None,
        description='ID der Kalender-Kategorie',
    )
    title: str | None = Field(default=None, description='Beschreibung')
    begin_ts: int | None = Field(
        default=None,
        description='Beginn als UNIX-Timestamp',
    )
    end_ts: int | None = Field(
        default=None,
        description='Ende als UNIX-Timestamp',
    )
    fullday: bool | None = Field(
        default=None,
        description='ganztägig (0:00 bis 23:59 Uhr)',
    )
    repeat: bool | None = Field(default=None, description='Wiederholung aktivieren')
    repeat_type: int | None = Field(
        default=None,
        description='Wiederholungs-Typ (1=täglich, 2=wöchentlich, 3=monatlich)',
    )
    repeat_frequency: int | None = Field(
        default=None,
        description='Frequenz, alle x Tage/Wochen/Monate wiederholen',
    )
    repeat_weekly_days: Sequence[int] | None = Field(
        default=None,
        description='Wochentage bei wöchentlicher Wiederholung',
    )
    repeat_monthly_day: int | None = Field(
        default=None,
        description='Fixpunkt bei monatlicher Wiederholung',
    )
    repeat_until_bool: bool | None = Field(
        default=None,
        description='Laufzeit begrenzen',
    )
    repeat_until_ts: int | None = Field(
        default=None,
        description='Wiederholung bis als UNIX-Timestamp',
    )
    during_status_id: int | None = Field(
        default=None,
        description='ID des Status während des Termins',
    )
    during_status_vehicle: int | None = Field(
        default=None,
        description='ID des Fahrzeugs während des Termins',
    )
    during_status_note: str | None = Field(
        default=None,
        description='Status-Notiz während des Termins',
    )
    after_status_id: int | None = Field(
        default=None,
        description='ID des Status nach dem Termin',
    )
    prio: bool | None = Field(
        default=None,
        description='Priorität (überschreibt gleichzeitige Einträge)',
    )
    public: bool | None = Field(
        default=None,
        description='Beschreibung für Führungskräfte sichtbar',
    )


class PullStatusplanData(BaseModel):
    """Status plan data in pull."""

    model_config = ConfigDict(extra='allow')

    items: Mapping[str, StatusPlanEntry] = Field(
        default_factory=dict,
        description='Statusplan-Einträge nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=tuple,
        description='Reihenfolge (deprecated)',
    )
    categories: Sequence[int | str] | None = Field(
        default=None,
        description='Statusplan-Kategorien (deprecated)',
    )
    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )


class LocalMonitorEntry(BaseModel):
    """Single local monitor config in pull data."""

    model_config = ConfigDict(extra='allow')

    id: int | None = Field(default=None, description='ID des Monitors')
    name: str | None = Field(default=None, description='Name')
    type: int | None = Field(default=None, description='Monitor-Typ')
    groups: Sequence[int] | None = Field(default=None, description='IDs der Gruppen')
    vehicles: Sequence[int] | None = Field(
        default=None,
        description='IDs der Fahrzeuge',
    )
    show_alarm: bool | None = Field(default=None, description='Alarm anzeigen')
    show_alarm_duration: bool | None = Field(
        default=None,
        description='Alarm-Dauer anzeigen',
    )
    show_alarm_vehicle: bool | None = Field(
        default=None,
        description='Alarm-Fahrzeug anzeigen',
    )
    show_alarm_vehicle_fms_status: bool | None = Field(
        default=None,
        description='FMS-Status anzeigen',
    )
    show_alarm_group: bool | None = Field(
        default=None,
        description='Alarm-Gruppe anzeigen',
    )
    show_alarm_response: bool | None = Field(
        default=None,
        description='Alarm-Rückmeldung anzeigen',
    )
    filter_addressed: bool | None = Field(
        default=None,
        description='Nur adressierte anzeigen',
    )


class PullLocalmonitorData(BaseModel):
    """Local monitor config in pull data."""

    model_config = ConfigDict(extra='allow')

    items: Mapping[str, LocalMonitorEntry] = Field(
        default_factory=dict,
        description='Monitor-Konfigurationen nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=tuple,
        description='Reihenfolge',
    )
    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )


class PullMonitorData(BaseModel):
    """Personnel availability (monitor) in pull data."""

    model_config = ConfigDict(extra='allow')

    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )
    cached: bool | None = Field(default=None, description='Aus Cache')
    # Keys "1", "2", "3" etc. are group/category IDs, values are status_id -> count mappings
    # Use extra='allow' to capture dynamic keys


class PullClusterData(BaseModel):
    """Cluster/unit data in pull."""

    model_config = ConfigDict(extra='allow')

    id: int | None = Field(default=None, description='ID der Einheit')
    is_root: bool | None = Field(
        default=None,
        description='Ist übergeordnete (Mutter-) Einheit',
    )
    version_id: int | None = Field(
        default=None,
        description='Genutzte Version von DIVERA 24/7',
    )
    name: str | None = Field(default=None, description='Name der Einheit')
    shortname: str | None = Field(default=None, description='Abkürzung der Einheit')
    status_default: int | None = Field(
        default=None,
        description='Standard-Status bei Zurücksetzen',
    )
    status_default_overwrite_by_user: bool | None = Field(
        default=None,
        description='Standard-Status kann von Nutzer überschrieben werden',
    )
    address: Mapping[str, object] | None = Field(
        default=None,
        description='Adresse der Einheit',
    )
    consumer: Mapping[str, object] | None = Field(
        default=None,
        description='Stammdaten der Benutzer',
    )
    consumersorting: Sequence[int] | None = Field(
        default=None,
        description='Sortierte IDs der Benutzer',
    )
    qualification: Mapping[str, object] | None = Field(
        default=None,
        description='Qualifikationen',
    )
    qualificationsorting: Sequence[int] | None = Field(
        default=None,
        description='Sortierte Qualifikations-IDs',
    )
    operationrole: Mapping[str, object] | None = Field(
        default=None,
        description='Einsatzrollen',
    )
    operationrolesorting: Sequence[int] | None = Field(
        default=None,
        description='Sortierte Einsatzrollen-IDs',
    )
    status: Mapping[str, object] | None = Field(
        default=None,
        description='Status-Definitionen',
    )
    statussorting: Sequence[int] | None = Field(
        default=None,
        description='Sortierte Status-IDs',
    )
    statussorting_alarm: Sequence[int] | None = Field(default=None)
    statussorting_statusgeber: Sequence[int] | None = Field(default=None)
    statussorting_statusplaner: Sequence[int] | None = Field(default=None)
    statussorting_geofence: Sequence[int] | None = Field(default=None)
    statusplancategory: Mapping[str, object] | None = Field(
        default=None,
        description='Statusplan-Kategorien',
    )
    statusplancategorysorting: Sequence[int] | None = Field(
        default=None,
        description='Sortierte Statusplan-Kategorien',
    )


class PullMessageChannelData(BaseModel):
    """Message channels in pull data."""

    model_config = ConfigDict(extra='allow')

    items: Mapping[str, MessageChannelResult] = Field(
        default_factory=dict,
        description='Nachrichtenkanäle nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=tuple,
        description='Reihenfolge',
    )
    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )


class PullMessageData(BaseModel):
    """Messages in pull data."""

    model_config = ConfigDict(extra='allow')

    items: Mapping[str, MessageResult] = Field(
        default_factory=dict,
        description='Nachrichten nach ID',
    )
    parents: Mapping[str, int] | None = Field(
        default=None,
        description='Parent-ID pro Nachricht',
    )
    updated: Mapping[str, int] | None = Field(
        default=None,
        description='Aktualisierte Nachrichten (id -> ts)',
    )
    message_channel: Mapping[str, object] | Sequence[int] | None = Field(
        default=None,
        description='Nachrichtenkanäle (ID -> data oder Liste)',
    )
    limit: int | None = Field(
        default=None,
        description='Limit',
    )
    ts: int | None = Field(
        default=None,
        description='Letzte Änderung als UNIX-Timestamp',
    )


class PullData(BaseModel):
    """Data payload for GET /api/v2/pull/all."""

    model_config = ConfigDict(extra='allow')

    ucr: Mapping[str, UcrEntry] | None = Field(
        default=None,
        description='UserClusterRelations (ucr_id -> entry)',
    )
    ucr_default: int | None = Field(
        default=None,
        description='ID der UserClusterRelation in der Stammeinheit',
    )
    ucr_active: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )
    ts: int | None = Field(
        default=None,
        description='Aktueller UNIX-Timestamp des Servers',
    )
    user: PullUser | None = Field(
        default=None,
        description='Einstellungen und Berechtigungen',
    )
    alarm: PullAlarmData | None = Field(
        default=None,
        description='Alarmierungen',
    )
    news: PullNewsData | None = Field(
        default=None,
        description='Mitteilungen',
    )
    events: PullEventsData | None = Field(
        default=None,
        description='Termine',
    )
    status: PullStatusData | None = Field(
        default=None,
        description='Aktueller Status',
    )
    statusplan: PullStatusplanData | None = Field(
        default=None,
        description='Terminbasierte Statusplanung',
    )
    cluster: PullClusterData | None = Field(
        default=None,
        description='Daten und Einstellungen der Einheit',
    )
    localmonitor: PullLocalmonitorData | None = Field(
        default=None,
        description='Monitor-Konfiguration',
    )
    monitor: PullMonitorData | None = Field(
        default=None,
        description='Personalverfügbarkeit',
    )
    dm: PullDmData | None = Field(
        default=None,
        description='Direktnachrichten',
    )
    message_channel: PullMessageChannelData | None = Field(
        default=None,
        description='Nachrichtenkanäle',
    )
    message: PullMessageData | None = Field(
        default=None,
        description='Nachrichten',
    )


class PullAllResponse(BaseModel):
    """Response schema for GET /api/v2/pull/all."""

    success: bool = Field(description='Whether the request succeeded')
    data: PullData | None = Field(default=None, description='Pull data')


class VehicleStatusItem(BaseModel):
    """Vehicle status item for GET /api/v2/pull/vehicle-status."""

    model_config = ConfigDict(extra='allow')

    id: int | None = Field(default=None, description='ID des Fahrzeugs')
    name: str | None = Field(default=None, description='Funkrufname')
    shortname: str | None = Field(default=None, description='Fahrzeugtyp abgekürzt')
    fullname: str | None = Field(default=None, description='Fahrzeugtyp ausgeschrieben')
    fmsstatus: int | None = Field(default=None, description='Fahrzeug-Status')
    fmsstatus_id: int | None = Field(default=None, description='ID des Fahrzeug-Status')
    fmsstatus_note: str | None = Field(
        default=None,
        description='Notiz/Freitext-Rückmeldung',
    )
    fmsstatus_ts: int | None = Field(default=None, description='UNIX-Timestamp')
    lat: float | None = Field(default=None, description='Breitengrad')
    lng: float | None = Field(default=None, description='Längengrad')


class VehicleStatusResponse(BaseModel):
    """Response schema for GET /api/v2/pull/vehicle-status."""

    success: bool = Field(description='Whether the request succeeded')
    data: Sequence[VehicleStatusItem] = Field(
        default_factory=tuple,
        description='Fahrzeuge mit Status',
    )

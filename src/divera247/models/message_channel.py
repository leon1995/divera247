"""Pydantic models for Divera 24/7 message-channel API.

These models map to the schemas defined in ``api_v2_message-channel.yaml``.
"""

import datetime
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

from divera247.models.alarm import JsonPayload


class MessageChannelConfigDefault(BaseModel):
    """Default channel access config."""

    editable: bool | None = Field(default=None, description='Bearbeitbar')
    notification: bool | None = Field(default=None, description='Benachrichtigung aktiv')
    writable: bool | None = Field(default=None, description='Schreibbar')
    attachable: bool | None = Field(default=None, description='Anhänge erlaubt')
    access_earlier_messages: bool | None = Field(default=None, description='Zugriff auf ältere Nachrichten')
    access_start: bool | int | None = Field(default=None, description='Zugriff ab')
    access_expire: bool | int | None = Field(default=None, description='Zugriff bis')
    ts_access_start: datetime.datetime | None = Field(
        default=None,
        description='Zugriff ab als Timestamp',
    )
    ts_access_expire: datetime.datetime | None = Field(
        default=None,
        description='Zugriff bis als Timestamp',
    )


class MessageChannelConfig(BaseModel):
    """Message channel config container."""

    default: MessageChannelConfigDefault | None = Field(default=None, description='Default-Konfiguration')


class MessageChannelAccessEntry(BaseModel):
    """Single ucr_access entry."""

    user_cluster_relation_id: int | None = Field(default=None, description='UCR ID')
    access: int | bool | None = Field(default=None, description='Zugriff')
    access_start: bool | int | None = Field(default=None, description='Teilnahme ab')
    access_expire: bool | int | None = Field(default=None, description='Teilnahme bis')
    access_earlier_messages: int | bool | None = Field(default=None, description='Ältere Nachrichten')
    attachable: bool | None = Field(default=None, description='Anhänge erlaubt')
    confirmed: int | None = Field(default=None, description='Bestätigt')
    editable: bool | None = Field(default=None, description='Bearbeitbar')
    notification: bool | None = Field(default=None, description='Benachrichtigung')
    silent: bool | None = Field(default=None, description='Stumm')
    ts_access_expire: datetime.datetime | None = Field(default=None, description='Zugriff bis')
    ts_access_start: datetime.datetime | None = Field(default=None, description='Zugriff ab')
    writable: bool | None = Field(default=None, description='Schreibbar')
    ts_create: datetime.datetime | None = Field(default=None, description='Erstellt')


class MessageChannelSelfAccess(BaseModel):
    """Self access information."""

    editable: bool | None = Field(default=None, description='Bearbeitbar')
    writable: bool | None = Field(default=None, description='Schreibbar')
    attachable: bool | None = Field(default=None, description='Anhänge erlaubt')
    notification: bool | None = Field(default=None, description='Benachrichtigung')
    access: bool | None = Field(default=None, description='Zugriff')
    access_start: bool | None = Field(default=None, description='Zugriff ab gesetzt')
    access_expire: bool | None = Field(default=None, description='Zugriff bis gesetzt')
    access_earlier_messages: bool | None = Field(default=None, description='Ältere Nachrichten')
    ts_access_start: datetime.datetime | None = Field(default=None, description='Zugriff ab')
    ts_access_expire: datetime.datetime | None = Field(default=None, description='Zugriff bis')
    ts_create: datetime.datetime | None = Field(default=None, description='Erstellt')


class MessageChannelResult(BaseModel):
    """Message channel result schema (message-channel-result)."""

    id: int | None = Field(default=None, description='ID des Kanals')
    foreign_type: str | None = Field(
        default=None,
        description='alarm|news|event',
    )
    foreign_id: str | None = Field(default=None, description='ID der Meldung')
    cluster_id: int | None = Field(default=None, description='ID der Einheit')
    author_id: int | None = Field(default=None, description='ID des Nutzers')
    first_message_id: int | None = Field(
        default=None,
        description='ID der ersten Nachricht',
    )
    last_message_id: int | None = Field(
        default=None,
        description='ID der letzten Nachricht',
    )
    title: str | None = Field(default=None, description='Titel')
    description: str | None = Field(default=None, description='Beschreibung')
    access_all: bool | None = Field(
        default=None,
        description='Für alle Mitglieder zugänglich',
    )
    entities: Mapping[str, Sequence[int]] | None = Field(
        default=None,
        description='Adressierung nach Typ',
    )
    config: MessageChannelConfig | None = Field(default=None, description='Kanal-Konfiguration')
    ucr_access: Mapping[str, MessageChannelAccessEntry] | None = Field(
        default=None,
        description='Zugriffseinträge je UCR',
    )
    self_access: MessageChannelSelfAccess | None = Field(
        default=None,
        description='Eigener Zugriff',
    )
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    editable: bool | None = Field(default=None, description='Bearbeitbar')
    ts_publish: datetime.datetime | None = Field(default=None, description='Veröffentlichung')
    archive: bool | None = Field(default=None, description='Archiviert')
    ts_archive: datetime.datetime | None = Field(default=None, description='Archivierung')
    delete: bool | None = Field(default=None, description='Zum Löschen markiert')
    ts_delete: datetime.datetime | None = Field(default=None, description='Löschen am')
    ts_create: datetime.datetime | None = Field(default=None, description='UNIX-Timestamp Erstelldatum')
    ts_update: datetime.datetime | None = Field(
        default=None,
        description='UNIX-Timestamp zuletzt bearbeitet',
    )
    ts_last_message: datetime.datetime | None = Field(default=None, description='Zeitpunkt letzte Nachricht')


class MessageChannelsData(BaseModel):
    """Data payload for GET /api/v2/message-channels."""

    items: Mapping[str, MessageChannelResult] = Field(
        default_factory=dict,
        description='Kanäle nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Reihenfolge der Kanäle',
    )


class MessageChannelsResponse(BaseModel):
    """Response schema for GET /api/v2/message-channels."""

    success: bool = Field(description='Whether the request succeeded')
    data: MessageChannelsData | None = Field(
        default=None,
        description='Message channels payload',
    )
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class MessageChannelSingleResponse(BaseModel):
    """Response schema for GET/POST/PUT /api/v2/message-channels/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: MessageChannelResult | None = Field(
        default=None,
        description='Message channel data',
    )
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class MessageChannelInputMessageChannel(BaseModel):
    """MessageChannel object for create/update."""

    title: str | None = Field(default=None, description='Titel')
    description: str | None = Field(default=None, description='Beschreibung')
    access_all: bool | None = Field(
        default=None,
        description='Für alle Mitglieder zugänglich',
    )
    entities: Mapping[str, Sequence[int]] | None = Field(
        default=None,
        description='IDs der Nutzer, Gruppen, Standorte',
    )
    config: MessageChannelConfig | None = Field(
        default=None,
        description='Standard-Berechtigungen',
    )
    ucr_access: Mapping[str, MessageChannelAccessEntry] | None = Field(
        default=None,
        description='Berechtigungen je UserClusterRelation',
    )
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    ts_publish: datetime.datetime | None = Field(
        default=None,
        description='Zeitgesteuerte Veröffentlichung',
    )
    ts_archive: datetime.datetime | None = Field(
        default=None,
        description='Zeitgesteuerte Archivierung',
    )
    ts_delete: datetime.datetime | None = Field(
        default=None,
        description='Zeitgesteuertes Löschen',
    )


class MessageChannelInput(BaseModel):
    """Request body for creating/updating message channels."""

    MessageChannel: MessageChannelInputMessageChannel = Field(
        description='Message channel data',
    )


class MessageChannelActivityMessageChannel(BaseModel):
    """Payload for activity endpoint."""

    last_message_id: int = Field(
        description='ID der zuletzt gelesenen Nachricht',
    )


class MessageChannelActivityPayload(BaseModel):
    """Request body for POST /api/v2/message-channels/activity/{id}."""

    MessageChannel: MessageChannelActivityMessageChannel = Field(
        description='Activity data',
    )


class MessageChannelNotificationSelfAccess(BaseModel):
    """Self access for notification settings."""

    silent: bool | None = Field(
        default=None,
        description='Stumm schalten ab sofort',
    )
    ts_silent_expire: datetime.datetime | None = Field(
        default=None,
        description='Stumm ab als Timestamp',
    )
    ts_silent_start: datetime.datetime | None = Field(
        default=None,
        description='Stumm bis als Timestamp',
    )


class MessageChannelNotificationMessageChannel(BaseModel):
    """MessageChannel for notification settings."""

    self_access: MessageChannelNotificationSelfAccess | None = Field(
        default=None,
        description='Benachrichtigungseinstellungen',
    )


class MessageChannelNotificationPayload(BaseModel):
    """Request body for POST /api/v2/message-channels/notification-settings/{id}."""

    MessageChannel: MessageChannelNotificationMessageChannel = Field(
        description='Notification settings',
    )


class MessagesItemsData(BaseModel):
    """Data for GET /api/v2/message-channels/messages/{id}."""

    items: Mapping[str, JsonPayload] = Field(
        default_factory=dict,
        description='Nachrichten nach ID',
    )
    message_count: int | None = Field(default=None, description='Anzahl Nachrichten')
    first_message_id: int | None = Field(default=None, description='ID erste Nachricht')
    last_message_id: int | None = Field(default=None, description='ID letzte Nachricht')
    ts_last_message: datetime.datetime | None = Field(
        default=None,
        description='UNIX-Timestamp letzte Nachricht',
    )


class MessagesResponse(BaseModel):
    """Response schema for GET /api/v2/message-channels/messages/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: MessagesItemsData | None = Field(default=None, description='Messages data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class MessageSortingData(BaseModel):
    """Data for GET /api/v2/message-channels/message-sorting/{id}."""

    ucr: int | None = Field(default=None, description='UCR ID im Response-Objekt')
    sorting: Mapping[str, datetime.datetime] = Field(
        default_factory=dict,
        description='ID -> UNIX-Timestamp',
    )
    message_count: int | None = Field(default=None, description='Anzahl Nachrichten')
    first_message_id: int | None = Field(default=None, description='ID erste Nachricht')
    last_message_id: int | None = Field(default=None, description='ID letzte Nachricht')
    ts_last_message: datetime.datetime | None = Field(
        default=None,
        description='UNIX-Timestamp letzte Nachricht',
    )


class MessageSortingResponse(BaseModel):
    """Response schema for GET /api/v2/message-channels/message-sorting/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: MessageSortingData | None = Field(default=None, description='Sorting data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )

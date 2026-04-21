"""Pydantic models for Divera 24/7 message-channel API.

These models map to the schemas defined in ``api_v2_message-channel.yaml``.
"""

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field

from divera247.models.alarm import JsonPayload


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
    ts_create: int | None = Field(default=None, description='UNIX-Timestamp Erstelldatum')
    ts_update: int | None = Field(
        default=None,
        description='UNIX-Timestamp zuletzt bearbeitet',
    )


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
    private_mode: bool | None = Field(default=None, description='Sichtbarkeit privat')
    ts_publish: int | None = Field(
        default=None,
        description='Zeitgesteuerte Veröffentlichung',
    )
    ts_archive: int | None = Field(
        default=None,
        description='Zeitgesteuerte Archivierung',
    )
    ts_delete: int | None = Field(
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
    ts_silent_expire: int | None = Field(
        default=None,
        description='Stumm ab als Timestamp',
    )
    ts_silent_start: int | None = Field(
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
    ts_last_message: int | None = Field(
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

    sorting: Mapping[str, int] = Field(
        default_factory=dict,
        description='ID -> UNIX-Timestamp',
    )
    message_count: int | None = Field(default=None, description='Anzahl Nachrichten')
    first_message_id: int | None = Field(default=None, description='ID erste Nachricht')
    last_message_id: int | None = Field(default=None, description='ID letzte Nachricht')
    ts_last_message: int | None = Field(
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

"""Pydantic models for Divera 24/7 message API.

These models map to the schemas defined in ``api_v2_message.yaml``.
"""

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field


class MessageAttachment(BaseModel):
    """Attachment in message-result."""

    id: int | None = Field(default=None, description='ID des Anhangs')
    file_reference_id: int | None = Field(default=None, description='ID der FileReference')
    foreign_type: str | None = Field(default=None, description='Typ des Objekts')
    foreign_id: int | None = Field(default=None, description='ID des Objekts')
    author_id: int | None = Field(default=None, description='Urheber des Anhangs')
    title: str | None = Field(default=None, description='Dateiname')


class MessageResult(BaseModel):
    """Message result schema (message-result)."""

    id: int | None = Field(default=None, description='ID/Primärschlüssel')
    message_channel_id: int | None = Field(default=None, description='ID des Kanals')
    parent_id: int | None = Field(
        default=None,
        description='ID der vorausgehenden Nachricht (Thread)',
    )
    author_id: int | None = Field(default=None, description='ID des Nutzers')
    text: str | None = Field(default=None, description='Text')
    attachment_count: int | None = Field(default=None, description='Anzahl Anhänge')
    attachments: Sequence[MessageAttachment] | None = Field(
        default=None,
        description='Anhänge der Nachricht',
    )
    messages: Sequence[int] | None = Field(
        default=None,
        description='IDs der untergeordneten Nachrichten',
    )
    hidden: bool | None = Field(default=None, description='Entwurf')
    deleted: bool | None = Field(default=None, description='Gelöscht/Archiviert')
    ts_create: int | None = Field(default=None, description='UNIX-Timestamp Erstelldatum')
    ts_update: int | None = Field(
        default=None,
        description='UNIX-Timestamp zuletzt bearbeitet',
    )


class MessagesData(BaseModel):
    """Data payload for GET /api/v2/messages."""

    items: Mapping[str, MessageResult] = Field(
        default_factory=dict,
        description='Nachrichten nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Reihenfolge der Nachrichten',
    )


class MessagesResponse(BaseModel):
    """Response schema for GET /api/v2/messages."""

    success: bool = Field(description='Whether the request succeeded')
    data: MessagesData | None = Field(default=None, description='Messages payload')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class MessageSingleResponse(BaseModel):
    """Response schema for GET/POST/PUT /api/v2/messages/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: MessageResult | None = Field(default=None, description='Message data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class MessageInputMessage(BaseModel):
    """Message object for create/update (message-input.Message)."""

    message_channel_id: int = Field(description='ID des Kanals')
    parent_id: int | None = Field(
        default=None,
        description='ID der vorausgehenden Nachricht (Thread)',
    )
    text: str | None = Field(default=None, description='Text')


class MessageInput(BaseModel):
    """Request body for creating/updating messages (message-input)."""

    Message: MessageInputMessage = Field(description='Message data')

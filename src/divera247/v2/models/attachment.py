"""Pydantic models for Divera 24/7 attachment API.

These models map to the schemas defined in ``api_v2_attachment.yaml``:
``attachment-result`` and the response structures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


class AttachmentResult(BaseModel):
    """Attachment result schema (attachment-result).

    Structure returned by GET /api/v2/attachments and GET /api/v2/attachments/{id}.
    File download is available at /api/v2/file/open/{id}.
    """

    model_config = ConfigDict(extra='allow')

    id: int | None = Field(default=None, description='ID/Primärschlüssel')
    file_reference_id: int | None = Field(
        default=None,
        description='ID der Referenz (enthält Meta-Daten)',
    )
    foreign_type: str | None = Field(
        default=None,
        description='Typ der Verknüpfung (z.B. alarm)',
    )
    foreign_id: int | float | None = Field(
        default=None,
        description='Primärschlüssel des verknüpften Datensatzes',
    )
    type: int | None = Field(default=None, description='Interner Typ')
    title: str | None = Field(default=None, description='Titel des Anhangs')
    description: str | None = Field(
        default=None,
        description='Beschreibung des Anhangs',
    )
    encrypted: bool | None = Field(default=None, description='Verschlüsselt')
    encryption_iv: str | None = Field(
        default=None,
        description='Initialisierungsvektor',
    )


class AttachmentsData(BaseModel):
    """Data payload for GET /api/v2/attachments."""

    items: Mapping[str, AttachmentResult] = Field(
        default_factory=dict,
        description='Attachments by ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Order of attachments, ascending',
    )


class AttachmentsResponse(BaseModel):
    """Response schema for GET /api/v2/attachments."""

    success: bool = Field(description='Whether the request succeeded')
    data: AttachmentsData | None = Field(
        default=None,
        description='Attachments payload',
    )


class AttachmentSingleResponse(BaseModel):
    """Response schema for GET /api/v2/attachments/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: AttachmentResult | None = Field(
        default=None,
        description='Attachment data',
    )

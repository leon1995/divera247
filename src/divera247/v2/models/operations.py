"""Pydantic models for Divera 24/7 operations API.

These models map to the schemas defined in ``api_v2_operations.yaml``.
"""

from collections.abc import Sequence

from pydantic import BaseModel, Field


class OperationCustomItem(BaseModel):
    """Custom data point for operation."""

    key: str = Field(description='Eindeutiger key', min_length=1, max_length=64)
    title: str = Field(description='Titel', min_length=1, max_length=255)
    value: str = Field(description='Wert', min_length=0, max_length=64000)


class Operation(BaseModel):
    """Operation schema for create/update (operation)."""

    foreign_id: str | None = Field(
        default=None,
        description='Schlüssel zur Identifizierung',
    )
    number: str | None = Field(
        default=None,
        description='Einsatznummer',
    )
    priority: bool | None = Field(default=None, description='Sonderrechte')
    title: str | None = Field(default=None, description='Einsatzstichwort')
    text: str | None = Field(default=None, description='Freitext')
    reporter: str | None = Field(default=None, description='Meldender')
    patient: str | None = Field(default=None, description='Patient')
    address: str | None = Field(default=None, description='Adresse')
    address_freetext: str | None = Field(default=None, description='Freitext Adresse')
    scene_object: str | None = Field(default=None, description='Objekt')
    lat: float | None = Field(default=None, description='Breitengrad')
    lng: float | None = Field(default=None, description='Längengrad')
    destination: bool | None = Field(default=None, description='Transportziel')
    destination_address: str | None = Field(
        default=None,
        description='Transportziel Adresse',
    )
    destination_lat: float | None = Field(
        default=None,
        description='Breitengrad Transportziel',
    )
    destination_lng: float | None = Field(
        default=None,
        description='Längengrad Transportziel',
    )
    destination_freetext: str | None = Field(
        default=None,
        description='Freitext Transportziel',
    )
    units: str | None = Field(
        default=None,
        description='Kommaseparierte Rettungsmittel',
    )
    custom: Sequence[OperationCustomItem] | None = Field(
        default=None,
        description='Weitere Daten',
    )


class OperationResponse(Operation):
    """Operation response (operation-response)."""

    id: int | None = Field(
        default=None,
        description='Interne Id innerhalb von DIVERA',
    )


class OperationRicItem(BaseModel):
    """RIC item for operations."""

    id: int | None = Field(default=None, description='Id des Einsatzmittel')
    name: str | None = Field(default=None, description='RIC/Namen')
    subric: str | None = Field(default=None, description='Sub-RIC')


class OperationFile(BaseModel):
    """File for operation attachments."""

    title: str | None = Field(default=None, description='Beschreibung')
    description: str | None = Field(default=None, description='Beschreibung Inhalt')
    filename: str | None = Field(default=None, description='Anzeige-Name')
    content_type: str | None = Field(default=None, description='MIME-Type')
    file_content: str | None = Field(
        default=None,
        description='Datei base64',
    )


class OperationFileResponse(BaseModel):
    """File response for operation attachments."""

    id: int | None = Field(default=None, description='Id des Anhangs')
    author_id: int | None = Field(default=None, description='Id des Authors')
    title: str | None = Field(default=None, description='Beschreibung')
    description: str | None = Field(default=None, description='Beschreibung Inhalt')
    filename: str | None = Field(default=None, description='Anzeige-Name')
    content_type: str | None = Field(default=None, description='MIME-Type')

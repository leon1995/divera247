"""Pydantic models for Divera 24/7 reporttype API.

These models map to the schemas defined in ``api_v2_reporttype.yaml``.
"""

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field


class ReporttypeFieldOption(BaseModel):
    """Option in reporttype field."""

    id: str | None = Field(default=None, description='Eindeutige ID')
    name: str | None = Field(default=None, description='Bezeichnung')


class ReporttypeField(BaseModel):
    """Field in reporttype."""

    id: str | None = Field(default=None, description='Eindeutige Eingabefeld ID')
    name: str | None = Field(default=None, description='Eingabefeldbezeichnung')
    type: str | None = Field(
        default=None,
        description='text, textinput, textarea, checkbox, radio, etc.',
    )
    options: Sequence[ReporttypeFieldOption] | None = Field(
        default=None,
        description='Optionen',
    )
    required: str | None = Field(default=None, description='Pflichtfeld (1=ja)')


class ReporttypeResult(BaseModel):
    """Reporttype result schema."""

    id: int | None = Field(default=None, description='Formular ID')
    name: str | None = Field(default=None, description='Formularname')
    description: str | None = Field(default=None, description='Formularbeschreibung')
    version: int | None = Field(default=None, description='Versionsnummer')
    uploads: bool | None = Field(default=None, description='Dateianhänge möglich')
    anonym: bool | None = Field(default=None, description='Anonyme Datenerfassung')
    location: bool | None = Field(default=None, description='Adresse erfassen')
    fields: Sequence[ReporttypeField] | None = Field(
        default=None,
        description='Eingabefelder',
    )


class ReporttypesData(BaseModel):
    """Data payload for GET /api/v2/reporttypes."""

    items: Mapping[str, ReporttypeResult] = Field(
        default_factory=dict,
        description='Formulare nach ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Sortierung',
    )


class ReporttypesResponse(BaseModel):
    """Response schema for GET /api/v2/reporttypes."""

    success: bool = Field(description='Whether the request succeeded')
    data: ReporttypesData | None = Field(default=None, description='Reporttypes payload')
    ucr: int | None = Field(default=None, description='UserClusterRelation ID')


class ReporttypeSingleResponse(BaseModel):
    """Response schema for GET /api/v2/reporttypes/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: ReporttypeResult | None = Field(default=None, description='Reporttype data')
    ucr: int | None = Field(default=None, description='UserClusterRelation ID')


class ReportItem(BaseModel):
    """Report item in reports list."""

    id: str | None = Field(default=None, description='ID der Formulareingabe')
    cluster_id: int | None = Field(default=None, description='ID der Einheit')
    user_cluster_relation_id: int | None = Field(default=None, description='Benutzer ID')
    reporttype_id: int | None = Field(default=None, description='Formular ID')
    status: int | None = Field(default=None, description='Status')
    attachment_count: int | None = Field(default=None, description='Anzahl Anhänge')
    lat: float | None = Field(default=None, description='Breitengrad')
    lng: float | None = Field(default=None, description='Längengrad')
    address: str | None = Field(default=None, description='Adresse')
    fields: Sequence[Mapping[str, object]] | None = Field(
        default=None,
        description='Eingabefelder mit Werten',
    )
    ts_create: float | None = Field(default=None, description='UNIX-Timestamp')


class ReportsData(BaseModel):
    """Data payload for GET /api/v2/reporttypes/{id}/reports."""

    items: Sequence[ReportItem] = Field(
        default_factory=tuple,
        description='Benutzereingaben',
    )
    itemcount: int | None = Field(
        default=None,
        description='Anzahl der Benutzereingaben gesamt',
    )


class ReportsResponse(BaseModel):
    """Response schema for GET /api/v2/reporttypes/{id}/reports."""

    success: bool = Field(description='Whether the request succeeded')
    data: ReportsData | None = Field(default=None, description='Reports payload')
    ucr: int | None = Field(default=None, description='UserClusterRelation ID')


class ReportInputReport(BaseModel):
    """Report object for POST /api/v2/reports."""

    reporttype_id: int = Field(description='Formular ID')
    address: str | None = Field(default=None, description='Adresse')
    cluster_use_vehicle_id: int | None = Field(default=None, description='Fahrzeug ID')
    lat: float | None = Field(default=None, description='Breitengrad')
    lng: float | None = Field(default=None, description='Längengrad')
    fields: Sequence[Mapping[str, object]] | None = Field(
        default=None,
        description='Eingabefelder',
    )


class ReportInput(BaseModel):
    """Request body for POST /api/v2/reports."""

    Report: ReportInputReport = Field(description='Report data')


class ReportStatusReport(BaseModel):
    """Report status for POST /api/v2/reports/{id}/status."""

    status: int = Field(
        description='Status (0-6)',
    )


class ReportStatusPayload(BaseModel):
    """Request body for POST /api/v2/reports/{id}/status."""

    Report: ReportStatusReport = Field(description='Status update')

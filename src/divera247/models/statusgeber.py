"""Pydantic models for Divera 24/7 statusgeber API.

These models map to the schemas defined in ``api_v2_statusgeber.yaml``.
"""

from __future__ import annotations

import datetime  # noqa: TC003

from pydantic import BaseModel, Field


class StatusgeberStatus(BaseModel):
    """Status object for POST /api/v2/statusgeber/set-status."""

    id: int = Field(description='ID des neuen Status')
    vehicle: int | None = Field(
        default=None,
        description='ID des Fahrzeugs',
    )
    note: str | None = Field(
        default=None,
        description='Freitext zur Statusmeldung',
    )
    reset_date: datetime.datetime | None = Field(
        default=None,
        description='UNIX-Timestamp für Zurücksetzen',
    )
    reset_to: int | None = Field(
        default=None,
        description='ID des Folgestatus bei Zurücksetzen',
    )
    alarm_skip: bool | None = Field(
        default=None,
        description='Statusänderung bei Einsatz ignorieren',
    )
    status_skip_statusplan: bool | None = Field(
        default=None,
        description='Termine im Zeitraum überschreiben',
    )
    status_skip_geofence: bool | None = Field(
        default=None,
        description='Geofences ignorieren',
    )


class StatusgeberPayload(BaseModel):
    """Request body for POST /api/v2/statusgeber/set-status."""

    Status: StatusgeberStatus = Field(description='Status data')

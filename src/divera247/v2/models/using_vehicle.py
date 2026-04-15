"""Pydantic models for Divera 24/7 using-vehicle API.

These models map to the schemas defined in ``api_v2_using-vehicle.yaml``.
"""

from collections.abc import Mapping

from pydantic import BaseModel, Field


class UsingVehicleSetStatusPayload(BaseModel):
    """Request body for POST /api/v2/using-vehicles/set-status/{id}."""

    status: int | None = Field(
        default=None,
        description='FMS-Status 0-9',
    )
    status_id: int | None = Field(
        default=None,
        description='ID des FMS-Status',
    )
    status_note: str | None = Field(
        default=None,
        description='Freitext-Rückmeldung',
    )
    lat: float | None = Field(default=None, description='Breitengrad')
    lng: float | None = Field(default=None, description='Längengrad')


class UsingVehicleBulkPayload(BaseModel):
    """Request body for POST /api/v2/using-vehicles/set-status-bulk.

    using_vehicles is an object keyed by vehicle identifier (ric, name, etc.)
    with status objects as values.
    """

    using_vehicles: Mapping[str, UsingVehicleSetStatusPayload] = Field(
        default_factory=dict,
        description='Fahrzeuge nach Kennung',
    )
    instructions: Mapping[str, Mapping[str, str]] | None = Field(
        default=None,
        description='z.B. using_vehicle.mapping: name',
    )


class UsingVehicleBulkResponse(BaseModel):
    """Response for POST /api/v2/using-vehicles/set-status-bulk."""

    success: bool = Field(description='Whether the request succeeded')
    data: Mapping[str, bool] = Field(
        default_factory=dict,
        description='Identifier -> success',
    )

"""Pydantic models for Divera 24/7 using-vehicle-crew API.

These models map to the schemas defined in ``api_v2_using-vehicle-crew.yaml``.
"""

from collections.abc import Sequence

from pydantic import BaseModel, Field


class UsingVehicleCrewCrew(BaseModel):
    """Crew object for add/remove endpoints."""

    add: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer zum Hinzufügen',
    )
    remove: Sequence[int] | None = Field(
        default=None,
        description='IDs der Benutzer zum Entfernen',
    )


class UsingVehicleCrewPayload(BaseModel):
    """Request body for POST /api/v2/using-vehicle-crew/add/{id} and remove/{id}."""

    Crew: UsingVehicleCrewCrew = Field(description='Crew data')

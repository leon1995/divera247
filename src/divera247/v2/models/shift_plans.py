"""Pydantic models for Divera 24/7 shift-plans API.

These models map to the schemas defined in ``api_v2_shift-plans.yaml``.
"""

from collections.abc import Mapping

from pydantic import BaseModel, Field


class ShiftPlanItem(BaseModel):
    """Shift plan item."""

    id: int | None = Field(default=None, description='Eindeutige Id des Dienstplans')
    name: str | None = Field(default=None, description='Name des Dienstplans')
    config: Mapping[str, object] | None = Field(
        default=None,
        description='Konfiguration',
    )
    ts_start: int | None = Field(
        default=None,
        description='Start als UNIX-Timestamp',
    )
    ts_end: int | None = Field(
        default=None,
        description='Ende als UNIX-Timestamp',
    )

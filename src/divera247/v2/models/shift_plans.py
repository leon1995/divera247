"""Pydantic models for Divera 24/7 shift-plans API.

These models map to the schemas defined in ``api_v2_shift-plans.yaml``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Mapping


class ShiftPlanItem(BaseModel):
    """Shift plan item."""

    model_config = ConfigDict(extra='allow')

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

"""Pydantic models for Divera 24/7 using-vehicle-property API.

These models map to the schemas defined in ``api_v2_using-vehicle-property.yaml``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Sequence


class UsingVehiclePropertyPayload(BaseModel):
    """Request body for POST /api/v2/using-vehicle-property/set/{id}.

    LATLNG is the fixed param; additional properties vary by cluster setup.
    """

    model_config = ConfigDict(extra='allow')

    LATLNG: Sequence[float] = Field(
        description='[Längengrad, Breitengrad]',
    )

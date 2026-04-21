"""Pydantic models for Divera 24/7 using-vehicle-property API.

These models map to the schemas defined in ``api_v2_using-vehicle-property.yaml``.
"""

from collections.abc import Sequence

from pydantic import BaseModel, Field


class UsingVehiclePropertyPayload(BaseModel):
    """Request body for POST /api/v2/using-vehicle-property/set/{id}.

    LATLNG is the fixed param; additional properties vary by cluster setup.
    """

    LATLNG: Sequence[float] = Field(
        description='[Längengrad, Breitengrad]',
    )

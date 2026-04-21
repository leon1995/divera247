"""Pydantic models for Divera 24/7 dashboard API.

These models map to the schemas defined in ``api_v2_dashboard.yaml``.
"""

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, Field


class DashboardResult(BaseModel):
    """Dashboard result schema (dashboard-result)."""

    id: int | None = Field(default=None, description='ID/Primärschlüssel')
    cluster_id: int | None = Field(default=None, description='ID der Einheit')
    template_type: int | None = Field(default=None, description='Templatetyp')
    access_type: int | None = Field(default=None, description='Berechtigungstyp')
    name: str | None = Field(default=None, description='Name des Dashboard')
    config: Mapping[str, object] | None = Field(default=None, description='Konfiguration')


class DashboardsData(BaseModel):
    """Data payload for GET /api/v2/dashboards."""

    items: Mapping[str, DashboardResult] = Field(
        default_factory=dict,
        description='Dashboards by ID',
    )
    sorting: Sequence[int] = Field(
        default_factory=list,
        description='Reihenfolge der Dashboards',
    )


class DashboardsResponse(BaseModel):
    """Response schema for GET /api/v2/dashboards."""

    success: bool = Field(description='Whether the request succeeded')
    data: DashboardsData | None = Field(default=None, description='Dashboards payload')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class DashboardSingleResponse(BaseModel):
    """Response schema for GET/POST/PUT /api/v2/dashboards/{id}."""

    success: bool = Field(description='Whether the request succeeded')
    data: DashboardResult | None = Field(default=None, description='Dashboard data')
    ucr: int | None = Field(
        default=None,
        description='ID der UserClusterRelation im aktuellen Request',
    )


class DashboardInputDashboard(BaseModel):
    """Dashboard object for create/update (dashboard-input.Dashboard)."""

    template_type: int | None = Field(default=None, description='Templatetyp')
    access_type: int | None = Field(default=None, description='Berechtigungstyp')
    name: str | None = Field(default=None, description='Name des Dashboard')
    config: Mapping[str, object] | None = Field(default=None, description='Konfiguration')


class DashboardInput(BaseModel):
    """Request body for creating/updating dashboards (dashboard-input)."""

    Dashboard: DashboardInputDashboard = Field(description='Dashboard data')

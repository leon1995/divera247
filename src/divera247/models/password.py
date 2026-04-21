"""Pydantic models for Divera 24/7 password API.

These models map to the schemas defined in ``api_v2_password.yaml``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PasswordValidatePayload(BaseModel):
    """Request body for POST/GET /api/v2/password/validate."""

    user_id: str = Field(description='Benutzer ID')
    cluster_id: str = Field(description='Cluster ID')
    password: str = Field(description='Passwort')
    password_repeat: str = Field(description='Passwort wiederholung')
    email: str = Field(description='Benutzer Emailadresse')


class PasswordValidateResponse(BaseModel):
    """Response schema for POST/GET /api/v2/password/validate."""

    error: bool = Field(
        description='False wenn Fehler in der Validierung',
    )
    errors: str | None = Field(
        default=None,
        description='Fehler der Validierung',
    )

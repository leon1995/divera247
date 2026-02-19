"""Pydantic models for Divera 24/7 auth API.

These models map to the schemas defined in ``api_v2_auth.yaml``:
login and JWT endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Mapping


class AuthLoginUser(BaseModel):
    """User object in login response."""

    model_config = ConfigDict(extra='allow')

    access_token: str | None = Field(default=None, description='API-Accesskey')
    autologin: bool | None = Field(default=None, description='Automatischer Login erlaubt')
    auth_key: str | None = Field(default=None, description='Autologin-Schlüssel')
    default_user_cluster_relation: int | None = Field(
        default=None,
        description='UserClusterRelation (UCR)',
    )


class AuthLoginData(BaseModel):
    """Data payload for POST /api/v2/auth/login."""

    model_config = ConfigDict(extra='allow')

    user: AuthLoginUser | None = Field(default=None, description='User data')
    ucr: Mapping[str, object] | None = Field(
        default=None,
        description='Verknüpfungen des Anwenders',
    )
    errors: Mapping[str, str] | None = Field(default=None, description='Validation errors')


class AuthLoginResponse(BaseModel):
    """Response schema for POST /api/v2/auth/login."""

    success: bool = Field(description='Whether the request succeeded')
    data: AuthLoginData | None = Field(default=None, description='Login data')


class AuthLoginPayload(BaseModel):
    """Request body for POST /api/v2/auth/login."""

    Login: AuthLoginLogin = Field(description='Login credentials')


class AuthLoginLogin(BaseModel):
    """Login credentials."""

    username: str = Field(description='E-Mail-Adresse')
    password: str = Field(description='Passwort')
    jwt: bool = Field(default=False, description='JWT zusätzlich abfragen')


class AuthJwtData(BaseModel):
    """Data payload for GET /api/v2/auth/jwt."""

    jwt: str | None = Field(default=None, description='JSON-Web-Token')


class AuthJwtResponse(BaseModel):
    """Response schema for GET /api/v2/auth/jwt."""

    success: bool = Field(description='Whether the request succeeded')
    data: AuthJwtData | None = Field(default=None, description='JWT data')

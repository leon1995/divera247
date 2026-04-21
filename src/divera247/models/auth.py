"""Pydantic models for Divera 24/7 auth API.

These models map to the schemas defined in ``api_v2_auth.yaml``:
login and JWT endpoints.
"""

import base64
import datetime
import json
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AuthLoginUser(BaseModel):
    """User object in login response."""

    access_token: str | None = Field(default=None, description='API-Accesskey')
    autologin: bool | None = Field(default=None, description='Automatischer Login erlaubt')
    auth_key: str | None = Field(default=None, description='Autologin-Schlüssel')
    default_user_cluster_relation: int | None = Field(
        default=None,
        description='UserClusterRelation (UCR)',
    )


class AuthLoginData(BaseModel):
    """Data payload for POST /api/v2/auth/login."""

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


class AuthLoginLogin(BaseModel):
    """Login credentials."""

    username: str = Field(description='E-Mail-Adresse')
    password: str = Field(description='Passwort')
    jwt: bool = Field(default=False, description='JWT zusätzlich abfragen')


class AuthLoginPayload(BaseModel):
    """Request body for POST /api/v2/auth/login."""

    Login: AuthLoginLogin = Field(description='Login credentials')


class AuthJwtAllowedUcr(BaseModel):
    """One entry in a JWT's ``allowed_ucr`` claim: permissions for a single UCR."""

    cluster_id: int | None = Field(default=None, description='ID der Einheit')
    usergroup_id: int | None = Field(default=None, description='ID der Benutzergruppe')
    name: str | None = Field(default=None, description='Name der Einheit')
    shortname: str | None = Field(default=None, description='Abkürzung der Einheit')
    status_id: int | None = Field(default=None, description='ID des aktuellen Status')


class AuthJwtPayload(BaseModel):
    """Decoded claims of a Divera 24/7 JWT.

    The signature is **not** verified; parse only tokens you obtained yourself
    (e.g. via ``GET /api/v2/auth/jwt``). ``iat`` / ``exp`` are coerced from
    unix timestamps to timezone-aware UTC :class:`datetime.datetime` by
    Pydantic so callers can compare them to ``datetime.now(tz=UTC)`` directly.

    When constructed via :meth:`from_token` the original JWT string is kept in :attr:`token`.
    """

    token: str = Field(
        exclude=True,
        description='Original JWT string (populated by from_token(), excluded from model_dump)',
    )
    iss: str | None = Field(default=None, description='Aussteller (issuer)')
    aud: str | None = Field(default=None, description='Ziel-Audience')
    jti: str | None = Field(default=None, description='Eindeutige Token-ID')
    iat: datetime.datetime | None = Field(default=None, description='Ausgestellt am (UTC)')
    exp: datetime.datetime | None = Field(default=None, description='Gültig bis (UTC)')
    ucr: int | None = Field(default=None, description='Aktive UserClusterRelation')
    ucr_id: int | None = Field(default=None, description='Aktive UserClusterRelation (alias von ucr)')
    allowed_ucr: Mapping[str, AuthJwtAllowedUcr] = Field(
        default_factory=dict,
        description='Zugängliche UCRs mit Berechtigungen (Schlüssel = ucr_id)',
    )
    allowed_cluster: Sequence[int] = Field(
        default_factory=tuple,
        description='IDs zugänglicher Einheiten',
    )
    user: int | None = Field(default=None, description='User-ID')
    user_id: int | None = Field(default=None, description='User-ID (alias von user)')
    usergroup_id: int | None = Field(default=None, description='ID der Benutzergruppe')
    cluster_id: int | None = Field(default=None, description='ID der aktiven Einheit')
    rmb: bool | None = Field(default=None, description='Remember-Me-Flag')
    api_key_id: int | None = Field(default=None, description='ID des verwendeten API-Keys')

    @classmethod
    def from_token(cls, token: str) -> 'AuthJwtPayload':
        """Parse a JWT string into its decoded claims.

        The signature is **not** verified; the three-segment shape is only
        inspected to extract and base64url-decode the middle (payload)
        segment. The original ``token`` string is preserved on the returned
        instance so ``str(payload)`` yields it back. Raises :class:`ValueError`
        if the token is malformed and :class:`TypeError` if the decoded
        payload is not a JSON object.
        """
        try:
            _, payload_b64, _ = token.split('.')
        except ValueError as err:
            msg = 'invalid jwt: expected three dot-separated segments'
            raise ValueError(msg) from err
        padded = payload_b64 + '=' * (-len(payload_b64) % 4)
        try:
            raw = json.loads(base64.urlsafe_b64decode(padded))
        except (ValueError, json.JSONDecodeError) as err:
            msg = 'invalid jwt: payload is not base64url-encoded json'
            raise ValueError(msg) from err
        if not isinstance(raw, dict):
            msg = 'invalid jwt: payload is not a json object'
            raise TypeError(msg)
        raw['token'] = token
        return cls.model_validate(raw)


class AuthJwtData(BaseModel):
    """Data payload for GET /api/v2/auth/jwt.

    The server returns ``jwt`` as a raw token string; a ``before`` validator
    decodes it into an :class:`AuthJwtPayload` so consumers get the claims
    directly. If you need the original token, extract it from the HTTP
    response body before validating, or use :class:`RefreshingJwtAuth`.
    """

    jwt: AuthJwtPayload = Field(description='Geparste Claims des JSON-Web-Tokens')

    @field_validator('jwt', mode='before')
    @classmethod
    def _decode_jwt(cls, value: Any) -> Any:
        if isinstance(value, str):
            return AuthJwtPayload.from_token(value)
        return value


class AuthJwtResponse(BaseModel):
    """Response schema for GET /api/v2/auth/jwt."""

    success: bool = Field(description='Whether the request succeeded')
    data: AuthJwtData | None = Field(default=None, description='JWT data')

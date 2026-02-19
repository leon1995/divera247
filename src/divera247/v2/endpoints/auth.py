"""Divera 24/7 auth API endpoints."""

from divera247.client import Divera247Client
from divera247.v2.models.auth import (
    AuthJwtResponse,
    AuthLoginPayload,
    AuthLoginResponse,
)


class AuthEndpoint:
    """Divera 24/7 auth API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def login(self, payload: AuthLoginPayload) -> AuthLoginResponse:
        """Get API key via username/password (POST /api/v2/auth/login).

        :param payload: Login credentials (include jwt=True to also receive JWT).
        """
        response = await self.client.post(
            'v2/auth/login',
            data=payload.model_dump(by_alias=False),
        )
        return AuthLoginResponse.model_validate(response.json())

    async def get_jwt(self) -> AuthJwtResponse:
        """Get JWT for Bearer token auth (GET /api/v2/auth/jwt).

        Requires accesskey in query (set via client).
        """
        response = await self.client.get('v2/auth/jwt')
        return AuthJwtResponse.model_validate(response.json())

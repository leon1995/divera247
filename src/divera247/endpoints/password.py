"""Divera 24/7 password API endpoints."""

from divera247.client import Divera247Client
from divera247.models.password import (
    PasswordValidatePayload,
    PasswordValidateResponse,
)


class PasswordEndpoint:
    """Divera 24/7 password API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def validate_post(
        self,
        payload: PasswordValidatePayload,
    ) -> PasswordValidateResponse:
        """Validate password (POST /api/v2/password/validate)."""
        response = await self.client.post(
            'v2/password/validate',
            data=payload.model_dump(by_alias=False),
        )
        return PasswordValidateResponse.model_validate(response.json())

    async def validate_get(
        self,
        payload: PasswordValidatePayload,
    ) -> PasswordValidateResponse:
        """Validate password (GET /api/v2/password/validate)."""
        response = await self.client.get(
            'v2/password/validate',
            params=payload.model_dump(by_alias=False),
        )
        return PasswordValidateResponse.model_validate(response.json())

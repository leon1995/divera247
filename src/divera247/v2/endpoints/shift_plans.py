"""Divera 24/7 shift-plans API endpoints."""

from collections.abc import Sequence

from divera247.client import Divera247Client
from divera247.v2.models.shift_plans import ShiftPlanItem


class ShiftPlansEndpoint:
    """Divera 24/7 shift-plans API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_shift_plans(self) -> Sequence[ShiftPlanItem]:
        """Get shift plans (GET /api/v2/shift-plans)."""
        response = await self.client.get('v2/shift-plans')
        return [ShiftPlanItem.model_validate(item) for item in response.json()]

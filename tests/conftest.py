from collections.abc import AsyncGenerator

import pytest

from divera247.client import Divera247Client


@pytest.fixture
async def api_client() -> AsyncGenerator[Divera247Client]:
    async with Divera247Client(access_key='') as client:
        yield client

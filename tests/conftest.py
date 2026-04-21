from collections.abc import AsyncGenerator

import pytest

from divera247.auth import AccessKeyAuth
from divera247.client import Divera247Client


@pytest.fixture
async def api_client() -> AsyncGenerator[Divera247Client]:
    """Yield a ``Divera247Client`` for tests (async context lifecycle)."""
    async with Divera247Client(auth=AccessKeyAuth('')) as client:
        yield client

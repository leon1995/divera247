"""News API fixture and endpoint tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from divera247.endpoints import NewsEndpoint
from divera247.models.alarm import SuccessResponse
from divera247.models.news import (
    NewsConfirmPayload,
    NewsInput,
    NewsResponse,
    NewsSingleResponse,
    ReachResponse,
)
from tests._helpers import EXAMPLE_ID, load_v2_json

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client


@pytest.fixture
def news_endpoint(api_client: Divera247Client) -> NewsEndpoint:
    """Provide ``NewsEndpoint`` using the shared mock client."""
    return NewsEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('post_news_request.json', NewsInput),
        ('post_news_response.json', NewsSingleResponse),
        ('get_news_response.json', NewsResponse),
        ('get_news_id_response.json', NewsSingleResponse),
        ('put_news_id_request.json', NewsInput),
        ('put_news_id_response.json', NewsSingleResponse),
        ('delete_news_id_response.json', SuccessResponse),
        ('post_news_attachment_id_response.json', SuccessResponse),
        ('post_news_archive_id_response.json', SuccessResponse),
        ('post_news_confirm_id_request.json', NewsConfirmPayload),
        ('post_news_confirm_id_response.json', SuccessResponse),
        ('post_news_read_id_response.json', SuccessResponse),
        ('get_news_reach_id_response.json', ReachResponse),
        ('get_news_download_id_response.json', SuccessResponse),
        ('delete_news_reset-responses_id_response.json', SuccessResponse),
    ],
)
def test_news_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    model.model_validate(load_v2_json('news', filename))


async def test_get_news(news_endpoint: NewsEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    """GET news returns success."""
    httpx_mock.add_response(json=load_v2_json('news', 'get_news_response.json'))
    response = await news_endpoint.get_news()
    assert response.success is True


async def test_download_news(news_endpoint: NewsEndpoint, httpx_mock: pytest_httpx.HTTPXMock) -> None:
    """Download news returns raw bytes from mock."""
    payload = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'
    httpx_mock.add_response(content=payload)
    content = await news_endpoint.download_news(EXAMPLE_ID)
    assert content == payload

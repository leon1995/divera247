"""Divera 24/7 news API endpoints."""

from typing import TYPE_CHECKING

from divera247.client import Divera247Client
from divera247.models.alarm import SuccessResponse
from divera247.models.news import (
    NewsConfirmPayload,
    NewsInput,
    NewsResponse,
    NewsSingleResponse,
    ReachResponse,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class NewsEndpoint:
    """Divera 24/7 news API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_news(self) -> NewsResponse:
        """Get all non-archived news (GET /api/v2/news)."""
        response = await self.client.get('v2/news')
        return NewsResponse.model_validate(response.json())

    async def create_news(self, payload: NewsInput) -> NewsSingleResponse:
        """Create a new news item (POST /api/v2/news)."""
        response = await self.client.post(
            'v2/news',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return NewsSingleResponse.model_validate(response.json())

    async def get_news_item(self, news_id: int) -> NewsSingleResponse:
        """Get a single news item by ID (GET /api/v2/news/{id})."""
        response = await self.client.get(f'v2/news/{news_id}')
        return NewsSingleResponse.model_validate(response.json())

    async def update_news(
        self,
        news_id: int,
        payload: NewsInput,
    ) -> NewsSingleResponse:
        """Update a news item (PUT /api/v2/news/{id})."""
        response = await self.client.put(
            f'v2/news/{news_id}',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return NewsSingleResponse.model_validate(response.json())

    async def delete_news(self, news_id: int) -> SuccessResponse:
        """Delete a news item (DELETE /api/v2/news/{id})."""
        response = await self.client.delete(f'v2/news/{news_id}')
        return SuccessResponse.model_validate(response.json())

    async def add_attachment(
        self,
        news_id: int,
        *,
        upload: bytes,
        title: str,
        description: str,
        filename: str = 'attachment',
    ) -> SuccessResponse:
        """Add an attachment to a news item (POST /api/v2/news/attachment/{id})."""
        files: Mapping[str, object] = {
            'Attachment[upload]': (filename, upload, 'application/octet-stream'),
        }
        data: Mapping[str, str] = {
            'Attachment[title]': title,
            'Attachment[description]': description,
        }
        response = await self.client.post_multipart(
            f'v2/news/attachment/{news_id}',
            files=files,
            data=data,
        )
        return SuccessResponse.model_validate(response.json())

    async def archive_news(self, news_id: int) -> SuccessResponse:
        """Archive a news item (POST /api/v2/news/archive/{id})."""
        response = await self.client.post(f'v2/news/archive/{news_id}')
        return SuccessResponse.model_validate(response.json())

    async def confirm_news(
        self,
        news_id: int,
        payload: NewsConfirmPayload | None = None,
    ) -> SuccessResponse:
        """Create a response to news (POST /api/v2/news/confirm/{id})."""
        data = payload.model_dump(by_alias=False, exclude_none=True) if payload else None
        response = await self.client.post(
            f'v2/news/confirm/{news_id}',
            data=data,
        )
        return SuccessResponse.model_validate(response.json())

    async def read_news(self, news_id: int) -> SuccessResponse:
        """Mark news as read (POST /api/v2/news/read/{id})."""
        response = await self.client.post(f'v2/news/read/{news_id}')
        return SuccessResponse.model_validate(response.json())

    async def get_news_reach(self, news_id: int) -> ReachResponse:
        """Get news reach stats (GET /api/v2/news/reach/{id})."""
        response = await self.client.get(f'v2/news/reach/{news_id}')
        return ReachResponse.model_validate(response.json())

    async def download_news(self, news_id: int) -> bytes:
        """Download news as PDF (GET /api/v2/news/download/{id})."""
        response = await self.client.get(f'v2/news/download/{news_id}')
        return response.content

    async def reset_responses(self, news_id: int) -> SuccessResponse:
        """Reset all survey responses (DELETE /api/v2/news/reset-responses/{id})."""
        response = await self.client.delete(
            f'v2/news/reset-responses/{news_id}',
        )
        return SuccessResponse.model_validate(response.json())

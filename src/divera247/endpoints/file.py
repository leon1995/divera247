"""Divera 24/7 file API endpoints."""

from divera247.client import Divera247Client


class FileEndpoint:
    """Divera 24/7 file API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def open_file(self, file_id: int) -> bytes:
        """Download file content (GET /api/v2/file/open/{id}).

        Returns raw binary. Content is typically encrypted.
        """
        response = await self.client.get(f'v2/file/open/{file_id}')
        return response.content

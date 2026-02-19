"""Divera 24/7 reporttype API endpoints."""

from divera247.client import Divera247Client
from divera247.v2.models.alarm import SuccessResponse
from divera247.v2.models.reporttype import (
    ReportInput,
    ReportsResponse,
    ReportStatusPayload,
    ReporttypeResult,
    ReporttypeSingleResponse,
    ReporttypesResponse,
)


class ReporttypeEndpoint:
    """Divera 24/7 reporttype API endpoints."""

    def __init__(self, client: Divera247Client):
        self.client = client

    async def get_reporttypes(self) -> ReporttypesResponse:
        """Get all reporttypes (GET /api/v2/reporttypes)."""
        response = await self.client.get('v2/reporttypes')
        return ReporttypesResponse.model_validate(response.json())

    async def get_reporttype(self, reporttype_id: int) -> ReporttypeSingleResponse:
        """Get a reporttype (GET /api/v2/reporttypes/{id})."""
        response = await self.client.get(f'v2/reporttypes/{reporttype_id}')
        return ReporttypeSingleResponse.model_validate(response.json())

    async def delete_reporttype(self, reporttype_id: int) -> SuccessResponse:
        """Delete a reporttype (DELETE /api/v2/reporttypes/{id})."""
        response = await self.client.delete(f'v2/reporttypes/{reporttype_id}')
        return SuccessResponse.model_validate(response.json())

    async def get_reports(
        self,
        reporttype_id: int,
        *,
        offset: int | None = None,
    ) -> ReportsResponse:
        """Get reports (GET /api/v2/reporttypes/{id}/reports)."""
        params = {'offset': offset} if offset is not None else None
        response = await self.client.get(
            f'v2/reporttypes/{reporttype_id}/reports',
            params=params,
        )
        return ReportsResponse.model_validate(response.json())

    async def copy_reporttype(self, reporttype_id: int) -> ReporttypeSingleResponse:
        """Copy reporttype (POST /api/v2/reporttypes/{id}/copy)."""
        response = await self.client.post(f'v2/reporttypes/{reporttype_id}/copy')
        data = response.json()
        rt_data = ReporttypeResult.model_validate({'id': data['reporttype_id']}) if 'reporttype_id' in data else None
        return ReporttypeSingleResponse(
            success=data.get('success', True),
            data=rt_data,
            ucr=data.get('ucr'),
        )

    async def download_json(self, reporttype_id: int) -> object:
        """Download reporttype as JSON (GET /api/v2/reporttypes/{id}/download/json)."""
        response = await self.client.get(
            f'v2/reporttypes/{reporttype_id}/download/json',
        )
        return response.json()

    async def download_csv(self, reporttype_id: int) -> bytes:
        """Download reporttype as CSV (GET /api/v2/reporttypes/{id}/download/csv)."""
        response = await self.client.get(
            f'v2/reporttypes/{reporttype_id}/download/csv',
        )
        return response.content

    async def download_xls(self, reporttype_id: int) -> bytes:
        """Download reporttype as XLS (GET /api/v2/reporttypes/{id}/download/xls)."""
        response = await self.client.get(
            f'v2/reporttypes/{reporttype_id}/download/xls',
        )
        return response.content

    async def download_xlsx(self, reporttype_id: int) -> bytes:
        """Download reporttype as XLSX (GET /api/v2/reporttypes/{id}/download/xlsx)."""
        response = await self.client.get(
            f'v2/reporttypes/{reporttype_id}/download/xlsx',
        )
        return response.content

    async def create_report(self, payload: ReportInput) -> SuccessResponse:
        """Create report (POST /api/v2/reports)."""
        response = await self.client.post(
            'v2/reports',
            data=payload.model_dump(by_alias=False, exclude_none=True),
        )
        return SuccessResponse.model_validate(response.json())

    async def update_report_status(
        self,
        report_id: int,
        payload: ReportStatusPayload,
    ) -> SuccessResponse:
        """Update report status (POST /api/v2/reports/{id}/status)."""
        response = await self.client.post(
            f'v2/reports/{report_id}/status',
            data=payload.model_dump(by_alias=False),
        )
        return SuccessResponse.model_validate(response.json())

    async def delete_report(self, report_id: int) -> SuccessResponse:
        """Delete report (DELETE /api/v2/reports/{id})."""
        response = await self.client.delete(f'v2/reports/{report_id}')
        return SuccessResponse.model_validate(response.json())

    async def delete_report_attachment(self, attachment_id: int) -> SuccessResponse:
        """Delete report attachment (DELETE /api/v2/reports/{id}/attachment).

        :param attachment_id: ID der Datei (ID of the file/attachment).
        """
        response = await self.client.delete(
            f'v2/reports/{attachment_id}/attachment',
        )
        return SuccessResponse.model_validate(response.json())

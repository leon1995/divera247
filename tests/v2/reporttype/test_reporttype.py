"""Reporttype API fixture and endpoint tests."""

from __future__ import annotations

import pytest
import pytest_httpx
from pydantic import BaseModel
from tests.v2._helpers import EXAMPLE_ID, load_v2_json

from divera247.client import Divera247Client
from divera247.v2.endpoints.reporttype import ReporttypeEndpoint
from divera247.v2.models.alarm import SuccessResponse
from divera247.v2.models.reporttype import (
    ReportInput,
    ReportsResponse,
    ReportStatusPayload,
    ReporttypeSingleResponse,
    ReporttypesResponse,
)


@pytest.fixture
def reporttype_endpoint(api_client: Divera247Client) -> ReporttypeEndpoint:
    return ReporttypeEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('get_reporttypes_response.json', ReporttypesResponse),
        ('get_reporttypes_id_response.json', ReporttypeSingleResponse),
        ('get_reporttypes_id_reports_response.json', ReportsResponse),
        ('post_reports_request.json', ReportInput),
        ('post_reports_id_status_request.json', ReportStatusPayload),
        ('delete_reporttypes_id_response.json', SuccessResponse),
        ('post_reports_response.json', SuccessResponse),
        ('post_reports_id_status_response.json', SuccessResponse),
        ('delete_reports_id_response.json', SuccessResponse),
        ('delete_reports_id_attachment_response.json', SuccessResponse),
    ],
)
def test_reporttype_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    model.model_validate(load_v2_json('reporttype', filename))


async def test_get_reporttypes(
    reporttype_endpoint: ReporttypeEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    httpx_mock.add_response(json=load_v2_json('reporttype', 'get_reporttypes_response.json'))
    response = await reporttype_endpoint.get_reporttypes()
    assert response.success is True


async def test_download_xls(
    reporttype_endpoint: ReporttypeEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    data = b'xls-binary'
    httpx_mock.add_response(content=data)
    content = await reporttype_endpoint.download_xls(EXAMPLE_ID)
    assert content == data

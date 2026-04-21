"""Alarm API: JSON fixtures against Pydantic models and mocked HTTP tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from divera247.endpoints import AlarmEndpoint
from divera247.models.alarm import (
    AlarmInput,
    AlarmSingleResponse,
    AlarmsListResponse,
    AlarmsResponse,
    CloseAlarmPayload,
    ConfirmPayload,
    ReachResponse,
    SuccessResponse,
)

if TYPE_CHECKING:
    import pytest_httpx
    from pydantic import BaseModel

    from divera247.client import Divera247Client

ALARM_FIXTURE_DIR = Path(__file__).resolve().parent
ALARM_EXAMPLE_ID = 123


def load_alarm_json(name: str) -> Any:
    """Load a JSON file from ``tests/v2/alarm/``."""
    return json.loads(ALARM_FIXTURE_DIR.joinpath(name).read_text(encoding='utf-8'))


@pytest.fixture
def alarm_endpoint(api_client: Divera247Client) -> AlarmEndpoint:
    """AlarmEndpoint backed by the mock HTTP client."""
    return AlarmEndpoint(api_client)


@pytest.mark.parametrize(
    ('filename', 'model'),
    [
        ('get_alarms_response.json', AlarmsResponse),
        ('get_alarms_list_response.json', AlarmsListResponse),
        ('get_alarms_id_response.json', AlarmSingleResponse),
        ('get_alarms_reach_id_response.json', ReachResponse),
        ('post_alarms_response.json', AlarmSingleResponse),
        ('post_alarms_request.json', AlarmInput),
        ('put_alarms_id_response.json', AlarmSingleResponse),
        ('put_alarms_id_request.json', AlarmInput),
        ('delete_alarms_id_response.json', SuccessResponse),
        ('post_alarms_archive_id_response.json', SuccessResponse),
        ('post_alarms_attachment_id_response.json', SuccessResponse),
        ('post_alarms_confirm_id_request.json', ConfirmPayload),
        ('post_alarms_confirm_id_response.json', SuccessResponse),
        ('post_alarms_read_id_response.json', SuccessResponse),
        ('post_alarms_close_id_request.json', CloseAlarmPayload),
        ('post_alarms_close_id_response.json', SuccessResponse),
        ('delete_alarms_reset-responses_id_response.json', SuccessResponse),
    ],
)
def test_alarm_fixture_parses(filename: str, model: type[BaseModel]) -> None:
    """Example JSON must parse with the expected Pydantic model."""
    data = load_alarm_json(filename)
    model.model_validate(data)


async def test_get_alarms(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET alarms list parses and returns items."""
    httpx_mock.add_response(
        json=load_alarm_json('get_alarms_response.json'),
    )
    response = await alarm_endpoint.get_alarms()
    assert response.success is True
    assert response.data is not None
    assert response.data.items


async def test_get_alarms_list(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET alarms list endpoint returns a non-empty list."""
    httpx_mock.add_response(json=load_alarm_json('get_alarms_list_response.json'))
    response = await alarm_endpoint.get_alarms_list()
    assert response.success is True
    assert len(response.data) >= 1


async def test_get_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET single alarm by id matches fixture id."""
    httpx_mock.add_response(json=load_alarm_json('get_alarms_id_response.json'))
    response = await alarm_endpoint.get_alarm(ALARM_EXAMPLE_ID)
    assert response.success is True
    assert response.data is not None
    assert response.data.id == ALARM_EXAMPLE_ID


async def test_create_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST alarm creates alarm from fixture payload."""
    payload = AlarmInput.model_validate(load_alarm_json('post_alarms_request.json'))
    httpx_mock.add_response(json=load_alarm_json('post_alarms_response.json'))
    response = await alarm_endpoint.create_alarm(payload)
    assert response.success is True
    assert response.data is not None
    assert response.data.title == 'FEUER3'


async def test_update_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """PUT alarm updates alarm from fixture payload."""
    payload = AlarmInput.model_validate(load_alarm_json('put_alarms_id_request.json'))
    httpx_mock.add_response(json=load_alarm_json('put_alarms_id_response.json'))
    response = await alarm_endpoint.update_alarm(ALARM_EXAMPLE_ID, payload)
    assert response.success is True
    assert response.data is not None


async def test_delete_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """DELETE alarm returns success."""
    httpx_mock.add_response(json=load_alarm_json('delete_alarms_id_response.json'))
    response = await alarm_endpoint.delete_alarm(ALARM_EXAMPLE_ID)
    assert response.success is True


async def test_archive_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST archive alarm returns success."""
    httpx_mock.add_response(json=load_alarm_json('post_alarms_archive_id_response.json'))
    response = await alarm_endpoint.archive_alarm(ALARM_EXAMPLE_ID)
    assert response.success is True


async def test_add_attachment(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST alarm attachment returns success."""
    httpx_mock.add_response(json=load_alarm_json('post_alarms_attachment_id_response.json'))
    response = await alarm_endpoint.add_attachment(
        ALARM_EXAMPLE_ID,
        upload=b'x',
        title='t',
        description='d',
    )
    assert response.success is True


async def test_confirm_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST confirm alarm returns success."""
    payload = ConfirmPayload.model_validate(load_alarm_json('post_alarms_confirm_id_request.json'))
    httpx_mock.add_response(json=load_alarm_json('post_alarms_confirm_id_response.json'))
    response = await alarm_endpoint.confirm_alarm(ALARM_EXAMPLE_ID, payload)
    assert response.success is True


async def test_read_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST read alarm returns success."""
    httpx_mock.add_response(json=load_alarm_json('post_alarms_read_id_response.json'))
    response = await alarm_endpoint.read_alarm(ALARM_EXAMPLE_ID)
    assert response.success is True


async def test_close_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """POST close alarm returns success."""
    payload = CloseAlarmPayload.model_validate(load_alarm_json('post_alarms_close_id_request.json'))
    httpx_mock.add_response(json=load_alarm_json('post_alarms_close_id_response.json'))
    response = await alarm_endpoint.close_alarm(ALARM_EXAMPLE_ID, payload)
    assert response.success is True


async def test_get_alarm_reach(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """GET alarm reach parses transports map."""
    httpx_mock.add_response(json=load_alarm_json('get_alarms_reach_id_response.json'))
    response = await alarm_endpoint.get_alarm_reach(ALARM_EXAMPLE_ID)
    assert response.success is True
    assert response.data is not None
    assert response.data.transports == {}


async def test_reset_responses(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """DELETE reset responses returns success."""
    httpx_mock.add_response(json=load_alarm_json('delete_alarms_reset-responses_id_response.json'))
    response = await alarm_endpoint.reset_responses(ALARM_EXAMPLE_ID)
    assert response.success is True


async def test_download_alarm(
    alarm_endpoint: AlarmEndpoint,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """Download alarm returns raw PDF bytes from mock."""
    pdf_bytes = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'
    httpx_mock.add_response(content=pdf_bytes)
    content = await alarm_endpoint.download_alarm(ALARM_EXAMPLE_ID)
    assert content == pdf_bytes

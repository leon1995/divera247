"""Unit tests for :mod:`divera247.errors`.

Exercises the status-code -> exception-class mapping of
:func:`raise_from_response` and the envelope check in
:func:`ensure_success` without hitting any network.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from divera247.errors import (
    DiveraAPIError,
    DiveraAuthError,
    DiveraRateLimitError,
    DiveraValidationError,
    ensure_success,
    raise_from_response,
)


def _response(status: int, json: Any = None, *, headers: dict[str, str] | None = None) -> httpx.Response:
    """Build a detached :class:`httpx.Response` for error-mapping tests."""
    request = httpx.Request('GET', 'https://app.divera247.com/test')
    return httpx.Response(status, json=json, request=request, headers=headers or {})


def test_raise_from_response_ignores_2xx() -> None:
    """Success responses must not raise."""
    raise_from_response(_response(200, {'success': True}))


@pytest.mark.parametrize('status', [401, 403])
def test_raise_from_response_maps_401_403_to_auth_error(status: int) -> None:
    """Unauthorized / forbidden map to :class:`DiveraAuthError`."""
    with pytest.raises(DiveraAuthError) as excinfo:
        raise_from_response(_response(status, {'success': False, 'errors': {'auth': 'denied'}}))
    assert excinfo.value.status_code == status
    assert excinfo.value.errors == {'auth': 'denied'}


def test_raise_from_response_maps_429_with_retry_after() -> None:
    """429 responses populate ``retry_after`` from the header."""
    with pytest.raises(DiveraRateLimitError) as excinfo:
        raise_from_response(_response(429, {'success': False}, headers={'Retry-After': '42'}))
    assert excinfo.value.retry_after == pytest.approx(42.0)


def test_raise_from_response_maps_422_to_validation_error() -> None:
    """422 maps to :class:`DiveraValidationError` with errors preserved."""
    with pytest.raises(DiveraValidationError) as excinfo:
        raise_from_response(_response(422, {'success': False, 'errors': {'name': 'required'}}))
    assert excinfo.value.errors == {'name': 'required'}


def test_raise_from_response_generic_5xx() -> None:
    """Other error codes fall through to the generic :class:`DiveraAPIError`."""
    with pytest.raises(DiveraAPIError) as excinfo:
        raise_from_response(_response(503, {'success': False}))
    assert excinfo.value.status_code == 503
    assert not isinstance(excinfo.value, (DiveraAuthError, DiveraRateLimitError, DiveraValidationError))


class _Envelope:
    """Stand-in for a parsed Pydantic response model."""

    def __init__(self, success: bool, errors: dict[str, Any] | None = None) -> None:
        self.success = success
        self.errors = errors


def test_ensure_success_accepts_success_true() -> None:
    """Happy-path envelopes are not disturbed."""
    ensure_success(_Envelope(success=True))


def test_ensure_success_raises_on_success_false() -> None:
    """``success=false`` envelopes raise :class:`DiveraAPIError` with ``errors`` intact."""
    with pytest.raises(DiveraAPIError) as excinfo:
        ensure_success(_Envelope(success=False, errors={'field': 'bad'}))
    assert excinfo.value.errors == {'field': 'bad'}

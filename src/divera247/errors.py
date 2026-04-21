"""Exception hierarchy for the Divera 24/7 client.

The API uses two error channels that callers usually want to handle the same
way:

1. Plain HTTP error status codes (4xx / 5xx).
2. ``200 OK`` responses whose JSON envelope has ``success: false`` and an
   ``errors`` object describing what went wrong.

Both are mapped to the :class:`DiveraError` hierarchy here so callers can
``except DiveraAPIError`` instead of having to know whether a failure happened
at the HTTP or the envelope layer.

Public API:

* :class:`DiveraError` -- catch-all base for anything this library raises.
* :class:`DiveraAPIError` -- HTTP or envelope error from the Divera API, with
  access to status, body and the underlying :class:`httpx.Response`.
* :class:`DiveraAuthError` -- 401/403 or ``success=false`` with an auth-ish
  failure.
* :class:`DiveraRateLimitError` -- 429, exposes ``retry_after`` when known.
* :class:`DiveraValidationError` -- 422 or ``success=false`` with a populated
  ``errors`` mapping (request body rejected).
* :func:`raise_from_response` -- convert an ``httpx.Response`` into the right
  subclass, preserving body and headers.
* :func:`ensure_success` -- enforce the envelope ``success`` flag on a parsed
  Pydantic response model.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    import httpx


class DiveraError(Exception):
    """Base exception for every error this library raises intentionally."""


class DiveraAPIError(DiveraError):
    """Raised when the Divera 24/7 API returns an HTTP or envelope error.

    Preserves the originating :class:`httpx.Response` plus the decoded JSON
    body so callers can inspect ``errors`` / ``message`` fields without
    re-parsing.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: httpx.Response | None = None,
        body: Any = None,
        errors: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.body = body
        self.errors = errors


class DiveraAuthError(DiveraAPIError):
    """Raised on 401/403 responses or auth-scoped envelope errors."""


class DiveraRateLimitError(DiveraAPIError):
    """Raised on 429 responses.

    ``retry_after`` is populated from the ``Retry-After`` response header when
    the server provides it (seconds).
    """

    def __init__(self, message: str, *, retry_after: float | None = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class DiveraValidationError(DiveraAPIError):
    """Raised when the API rejects a request body (422 or ``success=false`` with field errors)."""


_STATUS_TO_EXCEPTION: Mapping[int, type[DiveraAPIError]] = {
    401: DiveraAuthError,
    403: DiveraAuthError,
    422: DiveraValidationError,
    429: DiveraRateLimitError,
}
"""Map HTTP status codes to the exception subclass they should raise."""


def _parse_retry_after(response: httpx.Response) -> float | None:
    """Parse the ``Retry-After`` header (delta-seconds form) as a float."""
    raw = response.headers.get('Retry-After')
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def raise_from_response(response: httpx.Response) -> None:
    """Raise the appropriate :class:`DiveraAPIError` subclass for an HTTP error.

    No-op for 2xx responses. The API always replies with a JSON body, so the
    decoded envelope is attached to the raised exception as ``body`` and its
    ``errors`` key (if any) as ``errors``.
    """
    if not response.is_error:
        return
    body = response.json()
    errors = body.get('errors') if isinstance(body, dict) else None
    status = response.status_code
    message = f'Divera API request failed with HTTP {status}'
    exc_cls = _STATUS_TO_EXCEPTION.get(status, DiveraAPIError)
    kwargs: dict[str, Any] = {'status_code': status, 'response': response, 'body': body, 'errors': errors}
    if exc_cls is DiveraRateLimitError:
        kwargs['retry_after'] = _parse_retry_after(response)
    raise exc_cls(message, **kwargs)


def ensure_success(parsed: Any, *, response: httpx.Response | None = None) -> None:
    """Raise a :class:`DiveraAPIError` if a parsed envelope reports failure.

    Accepts any object with a truthy ``success`` attribute; use on Pydantic
    response models that wrap the standard Divera ``{"success": ..., "data":
    ...}`` envelope. ``response`` is optional context for the exception.
    """
    if getattr(parsed, 'success', True):
        return
    errors = getattr(parsed, 'errors', None) or getattr(getattr(parsed, 'data', None), 'errors', None)
    raise DiveraAPIError(
        'Divera API reported success=false',
        status_code=response.status_code if response is not None else None,
        response=response,
        errors=errors if isinstance(errors, dict) else None,
    )

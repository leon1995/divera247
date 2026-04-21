"""Tests for the Pydantic event models and :func:`parse_event` dispatcher."""

from __future__ import annotations

import pytest

from divera247.websocket.models import (
    UnknownEvent,
    UserStatusEvent,
    parse_event,
)

SAMPLE_UCR = 527459
SAMPLE_STATUS_ID = 33035
SAMPLE_CLUSTER = 8381
SAMPLE_PULL_ID = 2029889
SAMPLE_REF_ID = 42

_USER_STATUS_SAMPLE: dict = {
    'type': 'user-status',
    'payload': {
        'status_id': SAMPLE_STATUS_ID,
        'status_skip_statusplan': False,
        'status_skip_geofence': False,
        'status_set_date': 1776767153,
        'status_reset_date': '',
        'status_reset_id': 0,
        'status_log': [],
        'status_changes': [
            {'ts': 1776767114, 'status': 33035, 'note': '', 'vehicle': 0, 'event': 0, 'type': 0},
            {'ts': 1776767152, 'status': 33036, 'note': '', 'vehicle': 0, 'event': 0, 'type': 0},
        ],
        'note': '',
        'vehicle': 0,
        'ts': 1776767153,
        'cached': False,
    },
    'ucr': SAMPLE_UCR,
}


def test_user_status_event_parses_sample() -> None:
    """UserStatusEvent accepts the documented envelope + pull status payload."""
    event = UserStatusEvent.model_validate(_USER_STATUS_SAMPLE)
    assert event.type == 'user-status'
    assert event.ucr == SAMPLE_UCR
    assert event.payload.status_id == SAMPLE_STATUS_ID


def test_user_status_event_rejects_wrong_type_literal() -> None:
    """Non-matching ``type`` value must not validate as UserStatusEvent."""
    bad = dict(_USER_STATUS_SAMPLE, type='something-else')
    with pytest.raises(ValueError, match='user-status'):
        UserStatusEvent.model_validate(bad)


def test_unknown_event_keeps_arbitrary_type() -> None:
    """UnknownEvent stores the original ``type`` string instead of overwriting it."""
    event = UnknownEvent.model_validate({'type': 'cluster-vehicle'})
    assert event.type == 'cluster-vehicle'


def test_unknown_event_preserves_extras_in_model_extra() -> None:
    """Unknown top-level fields end up in ``model_extra`` untouched."""
    raw = {'type': 'cluster-vehicle', 'payload': {'id': SAMPLE_REF_ID}, 'cluster': SAMPLE_CLUSTER}
    event = UnknownEvent.model_validate(raw)
    assert event.model_extra == {'payload': {'id': SAMPLE_REF_ID}, 'cluster': SAMPLE_CLUSTER}


def test_unknown_event_requires_type_field() -> None:
    """A frame without a ``type`` is malformed and must fail validation."""
    with pytest.raises(ValueError, match='type'):
        UnknownEvent.model_validate({'foo': 'bar'})


def test_parse_event_dispatches_user_status() -> None:
    """``parse_event`` routes ``user-status`` frames to UserStatusEvent."""
    parsed = parse_event(_USER_STATUS_SAMPLE)
    assert isinstance(parsed, UserStatusEvent)
    assert parsed.ucr == SAMPLE_UCR


@pytest.mark.parametrize(
    'event_type',
    ['cluster-pull', 'cluster-message', 'cluster-vehicle', 'some-brand-new-event'],
)
def test_parse_event_falls_back_to_unknown_and_preserves_type(event_type: str) -> None:
    """Unknown ``type`` values route to UnknownEvent with the original string + extras intact.

    ``cluster-pull`` is included here explicitly: it is a known server event
    but has no typed envelope yet (awaiting a real live-API sample), so it
    must currently flow through the unknown-event fallback.
    """
    raw = {'type': event_type, 'foo': 1, 'bar': [1, 2]}
    parsed = parse_event(raw)
    assert isinstance(parsed, UnknownEvent)
    assert parsed.type == event_type
    assert parsed.model_extra == {'foo': 1, 'bar': [1, 2]}


def test_parse_event_missing_type_still_raises() -> None:
    """Frames without any ``type`` are malformed and must not be silently swallowed."""
    with pytest.raises(ValueError, match='type'):
        parse_event({'foo': 'bar'})


def test_parse_event_non_string_type_still_raises() -> None:
    """A numeric ``type`` is not a valid tag and must not be coerced into UnknownEvent."""
    with pytest.raises(ValueError, match='type'):
        parse_event({'type': 123})


def test_parse_event_falls_back_when_known_type_has_malformed_payload(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Known ``type`` with an unexpectedly shaped body degrades to UnknownEvent with a warning.

    Guards against the subscribe loop dying on a single malformed frame when
    the server starts sending a slightly different shape; the raw frame is
    logged so the typed model can be updated.
    """
    malformed = {'type': 'user-status', 'ucr': SAMPLE_UCR, 'payload': 'not-a-status-object'}

    with caplog.at_level('WARNING', logger='divera247.websocket.models'):
        parsed = parse_event(malformed)

    assert isinstance(parsed, UnknownEvent)
    assert parsed.type == 'user-status'
    assert parsed.model_extra == {'ucr': SAMPLE_UCR, 'payload': 'not-a-status-object'}
    assert any('user-status' in record.message for record in caplog.records)

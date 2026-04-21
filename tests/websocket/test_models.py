"""Tests for the Pydantic event models and :func:`parse_event` dispatcher."""

from __future__ import annotations

import pytest

from divera247.websocket.models import (
    ClusterPullEvent,
    ClusterPullRef,
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

_CLUSTER_PULL_SAMPLE: dict = {
    'type': 'cluster-pull',
    'pull': {'type': 'news', 'id': SAMPLE_PULL_ID},
    'cluster': SAMPLE_CLUSTER,
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


def test_cluster_pull_ref_parses_minimal_fields() -> None:
    """ClusterPullRef exposes ``type`` + ``id`` from the nested ``pull`` block."""
    ref = ClusterPullRef.model_validate({'type': 'news', 'id': SAMPLE_REF_ID})
    assert ref.type == 'news'
    assert ref.id == SAMPLE_REF_ID


def test_cluster_pull_event_parses_sample() -> None:
    """ClusterPullEvent exposes both the cluster id and the typed reference."""
    event = ClusterPullEvent.model_validate(_CLUSTER_PULL_SAMPLE)
    assert event.type == 'cluster-pull'
    assert event.cluster == SAMPLE_CLUSTER
    assert event.pull.type == 'news'
    assert event.pull.id == SAMPLE_PULL_ID


def test_cluster_pull_event_rejects_wrong_type_literal() -> None:
    """Non-matching ``type`` value must not validate as ClusterPullEvent."""
    bad = dict(_CLUSTER_PULL_SAMPLE, type='user-status')
    with pytest.raises(ValueError, match='cluster-pull'):
        ClusterPullEvent.model_validate(bad)


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


def test_parse_event_dispatches_cluster_pull() -> None:
    """``parse_event`` routes ``cluster-pull`` frames to ClusterPullEvent."""
    parsed = parse_event(_CLUSTER_PULL_SAMPLE)
    assert isinstance(parsed, ClusterPullEvent)
    assert parsed.cluster == SAMPLE_CLUSTER


@pytest.mark.parametrize('event_type', ['cluster-vehicle', 'cluster-message', 'some-brand-new-event'])
def test_parse_event_falls_back_to_unknown_and_preserves_type(event_type: str) -> None:
    """Unknown ``type`` values route to UnknownEvent with the original string + extras intact."""
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

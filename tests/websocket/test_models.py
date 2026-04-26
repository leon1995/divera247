"""Tests for the Pydantic event models and :func:`parse_event` dispatcher."""

from __future__ import annotations

import pytest

from divera247.websocket.models import (
    ClusterMonitorEvent,
    ClusterPullEvent,
    ClusterPullRef,
    ClusterVehicleEvent,
    ClusterVehicleState,
    UnknownEvent,
    UserStatusEvent,
    parse_event,
)

SAMPLE_UCR = 1234
SAMPLE_STATUS_ID = 1001
SAMPLE_CLUSTER = 1234
SAMPLE_PULL_ID = 1234
SAMPLE_PULL_TYPE = 'alarm'
SAMPLE_VEHICLE_ID = 1234
SAMPLE_VEHICLE_FMS = 6
SAMPLE_REF_ID = 42

_STATUS_BLOCK: dict = {
    'status_id': SAMPLE_STATUS_ID,
    'status_skip_statusplan': False,
    'status_skip_geofence': False,
    'status_set_date': 1700000000,
    'status_reset_date': '',
    'status_reset_id': 0,
    'status_log': [],
    'status_changes': [
        {'ts': 1700000000, 'status': 1001, 'note': '', 'vehicle': 0, 'event': 0, 'type': 0},
        {'ts': 1700000060, 'status': 1002, 'note': '', 'vehicle': 0, 'event': 0, 'type': 0},
    ],
    'note': '',
    'vehicle': 0,
    'ts': 1700000060,
    'cached': False,
}

_USER_STATUS_SAMPLE: dict = {
    'type': 'user-status',
    'payload': {
        'type': 'user-status',
        'status': _STATUS_BLOCK,
        'ucr': SAMPLE_UCR,
    },
}

_CLUSTER_PULL_SAMPLE: dict = {
    'type': 'cluster-pull',
    'payload': {
        'type': 'cluster-pull',
        'pull': {'type': SAMPLE_PULL_TYPE, 'id': SAMPLE_PULL_ID},
        'cluster': SAMPLE_CLUSTER,
    },
}

_CLUSTER_VEHICLE_SAMPLE: dict = {
    'type': 'cluster-vehicle',
    'payload': {
        'type': 'cluster-vehicle',
        'vehicle': {
            'id': SAMPLE_VEHICLE_ID,
            'fmsstatus_id': SAMPLE_VEHICLE_FMS,
            'fmsstatus_note': '',
            'fmsstatus_ts': 1700000120,
        },
        'cluster': SAMPLE_CLUSTER,
    },
}

_CLUSTER_MONITOR_SAMPLE: dict = {
    'type': 'cluster-monitor',
    'payload': {
        'type': 'cluster-monitor',
        'monitor': {
            '1': {
                '1001': {'all': 10, 'qualification': {'2': 4, '3': 2}},
                '1002': {'all': 3, 'qualification': {'2': 1}},
            }
        },
        'cluster': SAMPLE_CLUSTER,
    },
}


def test_user_status_event_flattens_nested_payload() -> None:
    """UserStatusEvent hoists ``status`` and ``ucr`` out of the nested payload via AliasPath."""
    event = UserStatusEvent.model_validate(_USER_STATUS_SAMPLE)
    assert event.type == 'user-status'
    assert event.ucr == SAMPLE_UCR
    assert event.status.status_id == SAMPLE_STATUS_ID


def test_user_status_event_rejects_wrong_outer_type_literal() -> None:
    """Non-matching outer ``type`` value must not validate as UserStatusEvent."""
    bad = dict(_USER_STATUS_SAMPLE, type='something-else')
    with pytest.raises(ValueError, match='user-status'):
        UserStatusEvent.model_validate(bad)


def test_user_status_event_requires_nested_payload_keys() -> None:
    """Missing ``payload.status`` or ``payload.ucr`` breaks validation.

    Guards the :class:`~pydantic.AliasPath` flattening: if the server ever
    drops the nested structure, we want a hard failure (and thus a
    fallback to :class:`UnknownEvent` via :func:`parse_event`) instead of
    silently producing an event with dummy fields.
    """
    bad = dict(_USER_STATUS_SAMPLE, payload={'type': 'user-status'})
    with pytest.raises(ValueError, match=r'status|ucr'):
        UserStatusEvent.model_validate(bad)


def test_cluster_pull_event_flattens_nested_payload() -> None:
    """ClusterPullEvent hoists ``pull`` and ``cluster`` out of the nested payload via AliasPath."""
    event = ClusterPullEvent.model_validate(_CLUSTER_PULL_SAMPLE)
    assert event.type == 'cluster-pull'
    assert event.cluster == SAMPLE_CLUSTER
    assert isinstance(event.pull, ClusterPullRef)
    assert event.pull.type == SAMPLE_PULL_TYPE
    assert event.pull.id == SAMPLE_PULL_ID


def test_cluster_pull_event_rejects_wrong_outer_type_literal() -> None:
    """Non-matching outer ``type`` value must not validate as ClusterPullEvent."""
    bad = dict(_CLUSTER_PULL_SAMPLE, type='something-else')
    with pytest.raises(ValueError, match='cluster-pull'):
        ClusterPullEvent.model_validate(bad)


def test_cluster_pull_ref_preserves_unknown_fields() -> None:
    """Extra fields on the pull reference round-trip via ``model_extra``.

    The server is free to enrich the ``pull`` reference (e.g. with a
    ``title`` or ``updated_at``) without breaking this model.
    """
    raw = {'type': SAMPLE_PULL_TYPE, 'id': SAMPLE_PULL_ID, 'title': 'Einsatz', 'prio': 1}
    ref = ClusterPullRef.model_validate(raw)
    assert ref.type == SAMPLE_PULL_TYPE
    assert ref.id == SAMPLE_PULL_ID
    assert ref.model_extra == {'title': 'Einsatz', 'prio': 1}


def test_cluster_vehicle_event_flattens_nested_payload() -> None:
    """ClusterVehicleEvent hoists ``vehicle`` + ``cluster`` via AliasPath."""
    event = ClusterVehicleEvent.model_validate(_CLUSTER_VEHICLE_SAMPLE)
    assert event.type == 'cluster-vehicle'
    assert event.cluster == SAMPLE_CLUSTER
    assert isinstance(event.vehicle, ClusterVehicleState)
    assert event.vehicle.id == SAMPLE_VEHICLE_ID
    assert event.vehicle.fmsstatus_id == SAMPLE_VEHICLE_FMS


def test_cluster_vehicle_state_preserves_unknown_fields() -> None:
    """Extra vehicle fields are tolerated and kept in ``model_extra``."""
    raw = {
        'id': SAMPLE_VEHICLE_ID,
        'fmsstatus_id': SAMPLE_VEHICLE_FMS,
        'fmsstatus_note': '',
        'fmsstatus_ts': 1700000120,
        'name': 'LF 20',
    }
    state = ClusterVehicleState.model_validate(raw)
    assert state.id == SAMPLE_VEHICLE_ID
    assert state.model_extra == {'name': 'LF 20'}


def test_cluster_monitor_event_flattens_nested_payload() -> None:
    """ClusterMonitorEvent hoists ``monitor`` + ``cluster`` via AliasPath."""
    event = ClusterMonitorEvent.model_validate(_CLUSTER_MONITOR_SAMPLE)
    assert event.type == 'cluster-monitor'
    assert event.cluster == SAMPLE_CLUSTER
    assert '1' in event.monitor
    assert event.monitor['1']['1001']['all'] == 10


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
    assert parsed.status.status_id == SAMPLE_STATUS_ID


def test_parse_event_dispatches_cluster_pull() -> None:
    """``parse_event`` routes ``cluster-pull`` frames to ClusterPullEvent."""
    parsed = parse_event(_CLUSTER_PULL_SAMPLE)
    assert isinstance(parsed, ClusterPullEvent)
    assert parsed.cluster == SAMPLE_CLUSTER
    assert parsed.pull.type == SAMPLE_PULL_TYPE
    assert parsed.pull.id == SAMPLE_PULL_ID


def test_parse_event_dispatches_cluster_vehicle() -> None:
    """``parse_event`` routes ``cluster-vehicle`` frames to ClusterVehicleEvent."""
    parsed = parse_event(_CLUSTER_VEHICLE_SAMPLE)
    assert isinstance(parsed, ClusterVehicleEvent)
    assert parsed.cluster == SAMPLE_CLUSTER
    assert parsed.vehicle.id == SAMPLE_VEHICLE_ID
    assert parsed.vehicle.fmsstatus_id == SAMPLE_VEHICLE_FMS


def test_parse_event_dispatches_cluster_monitor() -> None:
    """``parse_event`` routes ``cluster-monitor`` frames to ClusterMonitorEvent."""
    parsed = parse_event(_CLUSTER_MONITOR_SAMPLE)
    assert isinstance(parsed, ClusterMonitorEvent)
    assert parsed.cluster == SAMPLE_CLUSTER
    assert parsed.monitor['1']['1002']['all'] == 3


@pytest.mark.parametrize(
    'event_type',
    ['cluster-message', 'some-brand-new-event'],
)
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


def test_parse_event_falls_back_when_known_type_has_malformed_payload(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Known ``type`` with an unexpectedly shaped body degrades to UnknownEvent with a warning.

    Guards against the subscribe loop dying on a single malformed frame when
    the server starts sending a slightly different shape; the raw frame is
    logged so the typed model can be updated.
    """
    malformed = {'type': 'user-status', 'payload': 'not-a-payload-object'}

    with caplog.at_level('WARNING', logger='divera247.websocket.models'):
        parsed = parse_event(malformed)

    assert isinstance(parsed, UnknownEvent)
    assert parsed.type == 'user-status'
    assert parsed.model_extra == {'payload': 'not-a-payload-object'}
    assert any('user-status' in record.message for record in caplog.records)

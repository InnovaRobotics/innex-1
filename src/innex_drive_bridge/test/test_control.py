"""Exercise watchdog boundaries without ROS or hardware."""

import math

from innex_drive_bridge.control import COMMAND_TIMEOUT_NS, CommandState
import pytest


def update(state, stamp=1_000_000_000, ros_now=1_000_000_000, mono=100, **kwargs):
    """Supply deterministic command times."""
    return state.update(0.077, 0, stamp, 'base_link', ros_now, mono, **kwargs)


def test_timeout_exact_boundary():
    """Keep motion at 499999999 ns, then produce zero at 500000000 ns."""
    state = CommandState()
    assert state.targets(0) == (0, 0)
    assert update(state)
    assert state.targets(100 + COMMAND_TIMEOUT_NS - 1) == (500, 500)
    assert state.targets(100 + COMMAND_TIMEOUT_NS) == (0, 0)
    assert state.reason == 'command_timeout'


def test_delayed_message_has_only_remaining_lifetime():
    """A 400 ms old command must not receive a new 500 ms lifetime."""
    state = CommandState()
    assert update(state, ros_now=1_400_000_000)
    assert state.targets(100 + 99_999_999) == (500, 500)
    assert state.targets(100 + 100_000_000) == (0, 0)


@pytest.mark.parametrize('stamp,now', [
    (0, 1), (1_000_000_001, 1_000_000_000), (1, 500_000_001),
])
def test_bad_timestamps(stamp, now):
    """Reject zero stamps, future stamps and commands already 500 ms old."""
    state = CommandState()
    assert not update(state, stamp=stamp, ros_now=now)
    assert state.targets(100) == (0, 0)


def test_repeated_old_and_invalid_messages_stop():
    """Rejected input never preserves or extends an existing motion target."""
    state = CommandState()
    assert update(state)
    assert not update(state, ros_now=1_100_000_000)
    assert state.targets(200) == (0, 0)
    assert not update(state, stamp=999_999_999)
    assert update(state, stamp=1_000_000_001, ros_now=1_000_000_001)
    assert not update(state, stamp=1_000_000_002, ros_now=1_000_000_002,
                      unsupported=(0, math.nan, 0, 0))


def test_margin_and_frame_validation():
    """Reserve scheduling time and reject unrecognised coordinate frames."""
    state = CommandState(stop_margin_ns=35_000_000)
    assert update(state)
    assert state.targets(465_000_100) == (0, 0)
    assert not state.update(0.1, 0, 2_000_000_000, 'map', 2_000_000_000, 200)
    assert not update(state, stamp=3_000_000_000, ros_now=3_480_000_000)

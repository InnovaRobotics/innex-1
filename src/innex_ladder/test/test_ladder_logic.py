"""Tests for the drive decision."""

from innex_ladder.ladder_logic import decide_drive
from innex_ladder.ladder_rules import LadderState


def test_stops_when_command_is_too_old():
    """No command for longer than 0.25 s means stop both."""
    assert decide_drive('lower', 0.3, LadderState.UP) == ('stop', 'stop')


def test_fresh_command_still_works():
    """A command heard 0.2 s ago is still obeyed."""
    assert decide_drive('lower', 0.2, LadderState.UP) == ('lower', 'stop')


def test_no_command_means_stop():
    """Before any command has arrived, both machines are told to stop."""
    assert decide_drive(None, 0.0, LadderState.UP) == ('stop', 'stop')


def test_chain_runs_when_in_position():
    """The chain runs when the ladder is in position."""
    result = decide_drive('chain', 0.1, LadderState.IN_POSITION)
    assert result == ('stop', 'run')


def test_chain_blocked_unless_in_position():
    """The chain is told to stop in every state except in position."""
    for state in LadderState:
        if state != LadderState.IN_POSITION:
            assert decide_drive('chain', 0.1, state) == ('stop', 'stop')

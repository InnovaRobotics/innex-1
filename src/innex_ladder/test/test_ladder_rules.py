"""Tests for the ladder rules."""

from innex_ladder.ladder_rules import can_run_chain, LadderState


def test_chain_allowed_in_position():
    """The chain may run when the ladder is in position."""
    assert can_run_chain(LadderState.IN_POSITION) is True


def test_chain_blocked_in_every_other_state():
    """The chain must not run in any other state."""
    for state in LadderState:
        if state != LadderState.IN_POSITION:
            assert can_run_chain(state) is False

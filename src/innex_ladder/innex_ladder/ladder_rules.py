"""Rules for the bucket ladder and its chain."""

from enum import Enum


class LadderState(Enum):
    """The states the ladder can be in."""

    UP = 'up'
    LOWERING = 'lowering'
    IN_POSITION = 'in_position'
    RAISING = 'raising'
    STOPPED = 'stopped'


class ChainState(Enum):
    """The states the chain can be in."""

    STOPPED = 'stopped'
    TURNING = 'turning'


def can_run_chain(ladder):
    """Return True only when the ladder is in position."""
    return ladder == LadderState.IN_POSITION

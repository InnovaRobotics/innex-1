"""Decide what the ladder and chain should do right now."""

from innex_ladder.ladder_rules import can_run_chain

COMMAND_TIMEOUT_S = 0.25


def decide_drive(command, age, ladder):
    """Return the (ladder_drive, chain_drive) words to publish."""
    if command is None or age > COMMAND_TIMEOUT_S:
        return ('stop', 'stop')
    if command == 'lower':
        return ('lower', 'stop')
    if command == 'raise':
        return ('raise', 'stop')
    if command == 'chain':
        if can_run_chain(ladder):
            return ('stop', 'run')
        return ('stop', 'stop')
    return ('stop', 'stop')

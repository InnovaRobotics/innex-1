"""Check sender fault handling."""

from innex_drive_bridge.control import CommandState
from innex_drive_bridge.protocol import decode
from innex_drive_bridge.sender import Sender
from innex_drive_bridge.sequence import SequenceCounter
from innex_drive_bridge.transport import DryRunTransport
import pytest


def test_startup_timeout_shutdown_and_sequence():
    """Send a startup zero, then movement, timed-out zero and shutdown zero."""
    state = CommandState()
    transport = DryRunTransport()
    sender = Sender(state, transport, SequenceCounter())
    state.update(.077, 0, 1, 'base_link', 1, 100)
    assert sender.tick(100) == (0, 0)
    assert state.target == (0, 0)
    assert state.update(.077, 0, 2, 'base_link', 2, 200)
    assert sender.tick(200) == (500, 500)
    assert decode(transport.last_frame) == (1, 500, 500)
    assert sender.tick(500_000_200) == (0, 0)
    sender.close()
    assert decode(transport.last_frame) == (3, 0, 0)


def test_fault_latches_and_drops_old_target():
    """A write failure cannot cause queued retries or automatic rearming."""
    class Broken(DryRunTransport):
        def write(self, frame):
            raise OSError('disconnected')

    state = CommandState()
    sender = Sender(state, Broken(), SequenceCounter())
    assert sender.tick(0) is None
    assert sender.fault == 'disconnected'
    assert not sender.ready
    assert state.target == (0, 0)
    assert sender.tick(1) is None
    sender.close()


def test_persistent_sequence_restart_and_lock(tmp_path):
    """Skip reserved values after a crash/restart and exclude a second sender."""
    path = tmp_path / 'sequence'
    first = SequenceCounter(path, block_size=4)
    assert first.take() == 0
    with pytest.raises(BlockingIOError):
        SequenceCounter(path, block_size=4)
    first.close()
    second = SequenceCounter(path, block_size=4)
    assert [second.take() for _ in range(5)] == [4, 5, 6, 7, 8]
    second.close()


def test_corrupt_state_and_wrap(tmp_path):
    """Fail closed on corrupt state and support uint32 sequence wrap."""
    path = tmp_path / 'sequence'
    path.write_text('broken')
    with pytest.raises(ValueError):
        SequenceCounter(path)
    path.write_text('4294967295')
    counter = SequenceCounter(path, block_size=4)
    assert [counter.take(), counter.take()] == [0xFFFFFFFF, 0]
    counter.close()

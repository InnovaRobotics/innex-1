"""Exercise real pySerial code against a virtual POSIX terminal only."""

import os
import pty

from innex_drive_bridge.protocol import encode
from innex_drive_bridge.transport import SerialTransport
import pytest
import serial


def test_virtual_serial_roundtrip_and_disconnect():
    """Transfer exact bytes and report unplug without any physical USB device."""
    master, slave = pty.openpty()
    transport = SerialTransport(os.ttyname(slave))
    try:
        frame = encode(1, 0, 0)
        transport.write(frame)
        assert os.read(master, 18) == frame
        os.close(master)
        master = None
        with pytest.raises((OSError, serial.SerialException)):
            transport.write(frame)
    finally:
        try:
            transport.close()
        except OSError:
            pass
        if master is not None:
            os.close(master)
        os.close(slave)


def test_partial_and_backlogged_write():
    """Never retry a partial frame or append motion behind an older frame."""
    class Port:
        out_waiting = 0

        def write(self, frame):
            return len(frame) - 1

    transport = SerialTransport.__new__(SerialTransport)
    transport.port = Port()
    with pytest.raises(serial.SerialTimeoutException, match='Partial'):
        transport.write(encode(1, 0, 0))
    transport.port.out_waiting = 1
    with pytest.raises(serial.SerialTimeoutException, match='queued'):
        transport.write(encode(2, 0, 0))

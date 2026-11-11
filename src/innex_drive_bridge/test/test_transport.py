# Copyright 2026 Leo-P-1109
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

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

"""Provide bounded serial writes with no automatic motion retry."""

import termios

import serial


class DryRunTransport:
    """Store only the latest encoded frame without opening any device."""

    def __init__(self):
        """Start without an encoded command."""
        self.last_frame = None

    def write(self, frame):
        """Replace the previous diagnostic frame."""
        self.last_frame = frame

    def close(self):
        """Leave hardware untouched."""


class SerialTransport:
    """Open one exclusive POSIX port and reject pending/partial writes."""

    def __init__(self, port, baudrate=115200, write_timeout=0.01):
        """Use nonblocking reads and a finite write timeout."""
        if not port or not 0 < write_timeout <= 0.01:
            raise ValueError('A port and a write timeout of at most 10 ms are required')
        self.port = serial.Serial(
            port=port, baudrate=baudrate, timeout=0,
            write_timeout=write_timeout, exclusive=True)
        try:
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
        except (OSError, termios.error) as exc:
            self.port.close()
            raise serial.SerialException(str(exc)) from exc

    def write(self, frame):
        """Fail on backlog or a partial frame rather than queueing/retrying motion."""
        try:
            if self.port.out_waiting:
                raise serial.SerialTimeoutException('Previous frame is still queued')
            if self.port.write(frame) != len(frame):
                raise serial.SerialTimeoutException('Partial frame write')
        except serial.SerialException:
            raise
        except (OSError, termios.error) as exc:
            raise serial.SerialException(str(exc)) from exc

    def close(self):
        """Discard queued bytes and close without an unbounded flush."""
        try:
            if self.port.is_open:
                self.port.reset_output_buffer()
        except (OSError, termios.error):
            # An unplug can make tcflush fail; still release the file descriptor.
            pass
        finally:
            self.port.close()

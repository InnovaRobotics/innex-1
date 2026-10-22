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

"""Send startup/idle zero targets and latch communication failures."""

from innex_drive_bridge.protocol import encode


class Sender:
    """Apply the same serial behaviour in the ROS node and isolated tests."""

    def __init__(self, state, transport, sequence):
        """Require a transmitted zero before considering motion input."""
        self.state = state
        self.transport = transport
        self.sequence = sequence
        self.ready = False
        self.fault = None

    def tick(self, now_ns):
        """Send one current target; after any failure stop and require restart."""
        if self.fault is not None:
            return None
        target = self.state.targets(now_ns) if self.ready else (0, 0)
        try:
            frame = encode(self.sequence.take(), *target)
            self.transport.write(frame)
        except (OSError, ValueError) as exc:
            self.fault = str(exc)
            self.state.clear('serial_fault')
            self.ready = False
            try:
                self.transport.close()
            except OSError:
                pass
            return None
        if not self.ready:
            self.state.clear('startup_zero_sent')
            self.ready = True
        return target

    def close(self):
        """Attempt one zero frame and close; the firmware watchdog is independent."""
        try:
            if self.fault is None:
                self.transport.write(encode(self.sequence.take(), 0, 0))
        except (OSError, ValueError):
            pass
        finally:
            try:
                self.transport.close()
            finally:
                self.sequence.close()

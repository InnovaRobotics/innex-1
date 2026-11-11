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

"""Keep only fresh, valid body commands and enforce a monotonic watchdog."""

import math

from innex_drive_bridge.kinematics import Geometry, wheel_targets

COMMAND_TIMEOUT_NS = 500_000_000


class CommandState:
    """Maintain a single target; never queue commands or extend their lifetime."""

    def __init__(self, geometry=None, frame='base_link', stop_margin_ns=0):
        """Use explicit times so boundary and clock-jump cases are testable."""
        if not 0 <= stop_margin_ns < COMMAND_TIMEOUT_NS:
            raise ValueError('Invalid watchdog safety margin')
        self.geometry = geometry or Geometry()
        self.frame = frame
        self.margin = stop_margin_ns
        self.last_stamp_ns = 0
        self.deadline_ns = 0
        self.target = (0, 0)
        self.reason = 'waiting_for_command'

    def clear(self, reason='stopped'):
        """Discard motion without resetting the timestamp ordering watermark."""
        self.target = (0, 0)
        self.deadline_ns = 0
        self.reason = reason

    def update(self, linear_x, angular_z, stamp_ns, frame_id, ros_now_ns,
               monotonic_ns, unsupported=(0.0, 0.0, 0.0, 0.0)):
        """Accept only fresh increasing stamps in the expected body frame."""
        age = ros_now_ns - stamp_ns
        valid = (
            frame_id == self.frame and stamp_ns > self.last_stamp_ns
            and stamp_ns > 0 and 0 <= age < COMMAND_TIMEOUT_NS - self.margin
            and all(math.isfinite(v) and v == 0 for v in unsupported)
        )
        if not valid:
            self.clear('invalid_or_stale_command')
            return False
        try:
            target = wheel_targets(linear_x, angular_z, self.geometry)
        except ValueError:
            self.clear('invalid_velocity')
            return False
        self.last_stamp_ns = stamp_ns
        # A delayed command gets only its remaining lifetime, not a fresh 500 ms.
        self.deadline_ns = monotonic_ns + COMMAND_TIMEOUT_NS - age - self.margin
        self.target = target
        self.reason = 'active'
        return True

    def targets(self, monotonic_ns):
        """Return zero at the deadline, even if ROS simulation time is paused."""
        if monotonic_ns >= self.deadline_ns:
            if self.deadline_ns:
                self.clear('command_timeout')
            return (0, 0)
        return self.target

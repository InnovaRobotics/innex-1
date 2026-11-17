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

"""Convert body velocity into bounded skid-steer wheel targets."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Geometry:
    """Store wheel geometry in metres and the prototype limit in rad/s."""

    radius: float = 0.154
    track: float = 0.614
    max_wheel_rad_s: float = 1.0

    def __post_init__(self):
        """Reject invalid geometry or limits exceeding the firmware bound."""
        for value in (self.radius, self.track, self.max_wheel_rad_s):
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Geometry and wheel limit must be finite and positive')
        if self.max_wheel_rad_s > 1.0:
            raise ValueError('Protocol v1 prototype supports at most 1 rad/s')


def wheel_targets(linear_x: float, angular_z: float, geometry: Geometry):
    """Return integer mrad/s, scaling both wheels together to retain curvature."""
    if not math.isfinite(linear_x) or not math.isfinite(angular_z):
        raise ValueError('Body velocities must be finite')
    left = (linear_x - angular_z * geometry.track / 2) / geometry.radius
    right = (linear_x + angular_z * geometry.track / 2) / geometry.radius
    if not math.isfinite(left) or not math.isfinite(right):
        raise ValueError('Wheel conversion overflowed')
    scale = max(1.0, abs(left) / geometry.max_wheel_rad_s,
                abs(right) / geometry.max_wheel_rad_s)
    return round(left / scale * 1000), round(right / scale * 1000)

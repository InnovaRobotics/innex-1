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

"""Bridge fresh ROS body commands to the draft Teensy v1 protocol."""

import math
import signal
import threading
import time

from geometry_msgs.msg import TwistStamped
from innex_drive_bridge.control import CommandState
from innex_drive_bridge.kinematics import Geometry
from innex_drive_bridge.sender import Sender
from innex_drive_bridge.sequence import SequenceCounter
from innex_drive_bridge.transport import DryRunTransport, SerialTransport
from rcl_interfaces.msg import ParameterDescriptor
import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions


class DriveBridge(Node):
    """Use one executor thread, a steady timer and no command queue."""

    def __init__(self):
        """Validate read-only configuration before opening a transport."""
        super().__init__('drive_bridge')
        defaults = {
            'dry_run': True,
            'legacy_protocol_reviewed': False,
            'serial_port': '',
            'baudrate': 115200,
            'sequence_state_file': '',
            'send_rate_hz': 50.0,
            'wheel_radius_m': 0.154,
            'track_width_m': 0.614,
            'max_wheel_rad_s': 1.0,
            'command_frame': 'base_link',
        }
        values = {}
        for name, default in defaults.items():
            values[name] = self.declare_parameter(
                name, default, ParameterDescriptor(read_only=True)).value
        rate = values['send_rate_hz']
        if not math.isfinite(rate) or not 20 <= rate <= 100:
            raise ValueError('send_rate_hz must be between 20 and 100 Hz')
        if not values['command_frame']:
            raise ValueError('command_frame must not be empty')
        self.dry_run = values['dry_run']
        if not self.dry_run:
            if not values['legacy_protocol_reviewed']:
                raise ValueError('Legacy v1 limitations must be reviewed before serial use')
            if self.get_parameter('use_sim_time').value:
                raise ValueError('Serial mode cannot use simulation time')
            if not values['sequence_state_file']:
                raise ValueError('Serial mode requires persistent sequence_state_file')
        # Stop early enough to reserve one send period, a 10 ms write and 5 ms slack.
        # Linux scheduling still needs bench validation; this is not hard real time.
        margin = math.ceil((1.0 / rate + 0.015) * 1e9)
        self.state = CommandState(
            Geometry(values['wheel_radius_m'], values['track_width_m'],
                     values['max_wheel_rad_s']), values['command_frame'], margin)
        counter = SequenceCounter(
            None if self.dry_run else values['sequence_state_file'])
        try:
            transport = DryRunTransport() if self.dry_run else SerialTransport(
                values['serial_port'], values['baudrate'])
        except BaseException:
            counter.close()
            raise
        self.sender = Sender(self.state, transport, counter)
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST, depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE)
        self.subscription = self.create_subscription(
            TwistStamped, '/cmd_vel', self.on_command, qos)
        self.timer = self.create_timer(
            1.0 / rate, self.on_timer, clock=Clock(clock_type=ClockType.STEADY_TIME))
        self.last_report = None
        self.fault_reported = False
        self.get_logger().info(
            f'Drive bridge started; dry_run={self.dry_run}; watchdog=500 ms')

    def on_command(self, message):
        """Replace the latest target only after startup zero and validation."""
        if not self.sender.ready or self.sender.fault is not None:
            return
        stamp = message.header.stamp
        twist = message.twist
        if not 0 <= stamp.nanosec < 1_000_000_000:
            self.state.clear('invalid_stamp')
            return
        self.state.update(
            twist.linear.x, twist.angular.z,
            stamp.sec * 1_000_000_000 + stamp.nanosec,
            message.header.frame_id, self.get_clock().now().nanoseconds,
            time.monotonic_ns(),
            (twist.linear.y, twist.linear.z, twist.angular.x, twist.angular.y))

    def on_timer(self):
        """Transmit current targets or zero and report a latched link fault once."""
        target = self.sender.tick(time.monotonic_ns())
        if self.sender.fault is not None and not self.fault_reported:
            self.get_logger().error(
                f'Serial fault latched; restart after inspection: {self.sender.fault}')
            self.fault_reported = True
        report = (target, self.state.reason)
        if report != self.last_report:
            self.get_logger().info(f'Targets mrad/s={target}; state={self.state.reason}')
            self.last_report = report

    def stop(self):
        """Cancel sends and attempt zero before releasing the serial connection."""
        self.timer.cancel()
        self.state.clear('shutdown')
        self.sender.close()


def main(args=None):
    """Run until interrupted and release ROS resources on exit."""
    # launch may signal both the process group and the child. Signal handlers
    # only request a stop, so repeated signals cannot interrupt zero/close cleanup.
    stopping = threading.Event()
    previous = {}
    for signum in (signal.SIGINT, signal.SIGTERM):
        previous[signum] = signal.signal(signum, lambda *_: stopping.set())
    node = None
    try:
        rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
        node = DriveBridge()
        while rclpy.ok() and not stopping.is_set():
            rclpy.spin_once(node, timeout_sec=0.05)
    finally:
        try:
            if node is not None:
                try:
                    node.stop()
                finally:
                    node.destroy_node()
        finally:
            if rclpy.ok():
                rclpy.shutdown()
            for signum, handler in previous.items():
                signal.signal(signum, handler)


if __name__ == '__main__':
    main()

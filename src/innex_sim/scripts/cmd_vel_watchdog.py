#!/usr/bin/env python3
"""Stop the simulated rover when /cmd_vel stops arriving.

Gazebo's DiffDrive system keeps acting on the last command it received. On the rover, the drive
bridge on the Jetson sends zero when no /cmd_vel arrives for 500 ms (INX-140). This node does the
same for the sim. It forwards each /cmd_vel to Gazebo, and sends zero when commands stop.
"""

import signal

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.clock import Clock, ClockType
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

# Layer 2 in docs/system/teleop-and-control.md. Do not lengthen it.
TIMEOUT = 0.5  # s


def is_zero(command):
    twist = command.twist
    return not any((twist.linear.x, twist.linear.y, twist.linear.z,
                    twist.angular.x, twist.angular.y, twist.angular.z))


class CmdVelWatchdog(Node):

    def __init__(self):
        super().__init__('cmd_vel_watchdog')
        # The same QoS as the drive bridge on the Jetson (INX-140), so an old command never
        # arrives late.
        self.create_subscription(
            TwistStamped, '/cmd_vel', self.forward,
            QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT))
        self.publisher = self.create_publisher(TwistStamped, '~/cmd_vel', 1)
        # The commands come from the laptop, which runs on wall-clock time, not simulation time.
        self.timer = self.create_timer(
            TIMEOUT, self.stop, clock=Clock(clock_type=ClockType.STEADY_TIME))
        self.moving = False

    def forward(self, command):
        self.timer.reset()
        self.publisher.publish(command)
        self.moving = not is_zero(command)

    def stop(self):
        # Runs TIMEOUT after the last command, then every TIMEOUT until commands return.
        if self.moving:
            self.get_logger().warning(f'No /cmd_vel for {TIMEOUT} s. Stopping the rover.')
            self.moving = False
        command = TwistStamped()
        command.header.stamp = self.get_clock().now().to_msg()
        command.header.frame_id = 'base_link'
        self.publisher.publish(command)


def main():
    rclpy.init()
    node = CmdVelWatchdog()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        # Ctrl+C in a launch terminal sends SIGINT twice: once from the terminal, once from launch.
        # Ignore the second, so it can't interrupt the clean-up. Launch still escalates to SIGTERM.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

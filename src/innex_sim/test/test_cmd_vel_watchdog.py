import os
import signal
import subprocess
import time

import pytest
import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.executors import SingleThreadedExecutor

START_TIMEOUT = 60
# The watchdog must send zero this long after the last command (INX-155).
TIMEOUT = 0.5
# Allowance for the timer and for message delivery on one machine.
TOLERANCE = 0.05
COMMAND_RATE = 10.0


def command(linear_x=0.0, angular_z=0.0):
    message = TwistStamped()
    message.header.frame_id = 'base_link'
    message.twist.linear.x = linear_x
    message.twist.angular.z = angular_z
    return message


def is_zero(message):
    twist = message.twist
    return not any((twist.linear.x, twist.linear.y, twist.linear.z,
                    twist.angular.x, twist.angular.y, twist.angular.z))


class Watchdog:
    """Talks to cmd_vel_watchdog. Stands in for teleop on /cmd_vel and for the Gazebo bridge."""

    def __init__(self, domain_id):
        self.context = rclpy.Context()
        rclpy.init(context=self.context, domain_id=domain_id)
        self.node = rclpy.create_node('test_watchdog', context=self.context)
        self.executor = SingleThreadedExecutor(context=self.context)
        self.executor.add_node(self.node)
        self.publisher = self.node.create_publisher(TwistStamped, '/cmd_vel', 1)
        self.received = []
        self.node.create_subscription(
            TwistStamped, '/cmd_vel_watchdog/cmd_vel',
            lambda message: self.received.append((time.monotonic(), message)), 10)

    def spin(self, duration):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            self.executor.spin_once(timeout_sec=0.005)

    def wait_for_start(self):
        deadline = time.monotonic() + START_TIMEOUT
        while time.monotonic() < deadline:
            if self.publisher.get_subscription_count() and self.received:
                return
            self.spin(0.1)
        pytest.fail('cmd_vel_watchdog did not start')

    def drive(self, message, duration):
        """Publish one command at the teleop rate, then stop without sending zero."""
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            self.publisher.publish(message)
            self.spin(1.0 / COMMAND_RATE)

    def close(self):
        self.executor.shutdown()
        self.node.destroy_node()
        rclpy.shutdown(context=self.context)


@pytest.fixture(scope='module')
def watchdog(tmp_path_factory):
    env = dict(os.environ)
    # Keep these commands away from a rover or simulation that is running on the default domain.
    env['ROS_DOMAIN_ID'] = str(1 + os.getpid() % 49)
    log = (tmp_path_factory.mktemp('watchdog') / 'watchdog.log').open('w')
    process = subprocess.Popen(
        ['ros2', 'run', 'innex_sim', 'cmd_vel_watchdog'],
        env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    watchdog = Watchdog(int(env['ROS_DOMAIN_ID']))
    try:
        watchdog.wait_for_start()
        yield watchdog
    finally:
        watchdog.close()
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        log.close()


def test_forwards_each_command(watchdog):
    watchdog.received.clear()
    watchdog.drive(command(0.2, -0.3), 0.5)
    forwarded = [message for _, message in watchdog.received]
    assert forwarded
    for message in forwarded:
        assert message.header.frame_id == 'base_link'
        assert message.twist.linear.x == pytest.approx(0.2)
        assert message.twist.angular.z == pytest.approx(-0.3)


def test_no_zero_while_commands_arrive(watchdog):
    watchdog.drive(command(0.2), 0.5)
    watchdog.received.clear()
    watchdog.drive(command(0.2), 2.0)
    assert len(watchdog.received) >= 10
    assert not any(is_zero(message) for _, message in watchdog.received)


def test_sends_zero_when_commands_stop(watchdog):
    watchdog.received.clear()
    watchdog.drive(command(0.2, 0.3), 1.0)
    watchdog.spin(TIMEOUT + 1.0)
    last_command = max(t for t, message in watchdog.received if not is_zero(message))
    zeros = [(t, message) for t, message in watchdog.received if t > last_command]
    assert zeros, 'no command after the last drive command'
    assert all(is_zero(message) for _, message in zeros)
    assert zeros[0][1].header.frame_id == 'base_link'
    assert zeros[0][0] - last_command == pytest.approx(TIMEOUT, abs=TOLERANCE)


def test_keeps_sending_zero_while_commands_stay_stopped(watchdog):
    watchdog.drive(command(0.2), 0.5)
    watchdog.spin(TIMEOUT + TOLERANCE)
    watchdog.received.clear()
    watchdog.spin(3 * TIMEOUT)
    assert len(watchdog.received) >= 2
    assert all(is_zero(message) for _, message in watchdog.received)


def test_drives_again_when_commands_return(watchdog):
    watchdog.drive(command(0.2), 0.5)
    watchdog.spin(TIMEOUT + 0.5)
    watchdog.received.clear()
    watchdog.drive(command(-0.1), 1.0)
    forwarded = [message for _, message in watchdog.received if not is_zero(message)]
    assert forwarded
    assert forwarded[-1].twist.linear.x == pytest.approx(-0.1)

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
# Allowance for the timer and for message delivery on one loaded machine.
TOLERANCE = 0.1
COMMAND_RATE = 10.0


def test_stops_when_commands_stop_and_drives_again(tmp_path):
    env = dict(os.environ)
    # Keep these commands away from a rover or simulation that is running on the default domain.
    env['ROS_DOMAIN_ID'] = str(1 + os.getpid() % 49)
    log = (tmp_path / 'watchdog.log').open('w')
    process = subprocess.Popen(['ros2', 'run', 'innex_sim', 'cmd_vel_watchdog'], env=env,
                               stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    context = rclpy.Context()
    rclpy.init(context=context, domain_id=int(env['ROS_DOMAIN_ID']))
    node = rclpy.create_node('test_watchdog', context=context)
    executor = SingleThreadedExecutor(context=context)
    executor.add_node(node)
    publisher = node.create_publisher(TwistStamped, '/cmd_vel', 1)
    received = []
    node.create_subscription(TwistStamped, '/cmd_vel_watchdog/cmd_vel',
                             lambda message: received.append((time.monotonic(), message)), 10)

    def spin(duration):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.005)

    def drive(linear_x, angular_z, duration):
        """Publish one command at the teleop rate, then stop without sending zero."""
        command = TwistStamped()
        command.header.frame_id = 'base_link'
        command.twist.linear.x = linear_x
        command.twist.angular.z = angular_z
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            publisher.publish(command)
            spin(1.0 / COMMAND_RATE)

    def twists(since):
        return [(t, message.twist.linear.x, message.twist.angular.z)
                for t, message in received if t > since]

    try:
        # The watchdog sends zero while nothing drives, so a message means it is connected.
        deadline = time.monotonic() + START_TIMEOUT
        while not (publisher.get_subscription_count() and received):
            if time.monotonic() > deadline:
                pytest.fail('cmd_vel_watchdog did not start')
            spin(0.1)

        drive(0.2, -0.3, 0.5)
        start = time.monotonic()
        drive(0.2, -0.3, 2.0)
        driving = twists(start)
        assert len(driving) >= 10
        assert all((x, z) == pytest.approx((0.2, -0.3)) for _, x, z in driving)

        last_command = driving[-1][0]
        spin(TIMEOUT + 1.0)
        zeros = twists(last_command)
        assert len(zeros) >= 2, 'the watchdog did not keep sending zero'
        assert all((x, z) == (0.0, 0.0) for _, x, z in zeros)
        assert zeros[0][0] - last_command == pytest.approx(TIMEOUT, abs=TOLERANCE)
        assert received[-1][1].header.frame_id == 'base_link'

        start = time.monotonic()
        drive(-0.1, 0.0, 1.0)
        again = twists(start)
        assert again and again[-1][1] == pytest.approx(-0.1), 'the watchdog did not drive again'
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown(context=context)
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        log.close()

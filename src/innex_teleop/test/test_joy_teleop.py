import os
import signal
import subprocess
import time
from pathlib import Path

import pytest
import rclpy
import yaml
from geometry_msgs.msg import TwistStamped
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Joy

CONFIG = Path(__file__).resolve().parent.parent / 'config' / 'joy.yaml'
START_TIMEOUT = 60
# game_controller_node always publishes this many axes and buttons.
AXIS_COUNT = 6
BUTTON_COUNT = 21
REPEAT_RATE = 20.0


@pytest.fixture(scope='module')
def params():
    return yaml.safe_load(CONFIG.read_text())['teleop_twist_joy_node']['ros__parameters']


def joy_state(params, forward=0.0, left=0.0, enable=False, other_buttons=False):
    message = Joy()
    message.axes = [0.0] * AXIS_COUNT
    message.axes[params['axis_linear']['x']] = forward
    message.axes[params['axis_angular']['yaw']] = left
    message.buttons = [int(other_buttons)] * BUTTON_COUNT
    message.buttons[params['enable_button']] = int(enable)
    return message


def is_zero(command):
    twist = command.twist
    return not any((twist.linear.x, twist.linear.y, twist.linear.z,
                    twist.angular.x, twist.angular.y, twist.angular.z))


class Controller:
    """Stands in for the controller driver on /joy and for the rover on /cmd_vel."""

    def __init__(self, domain_id):
        self.context = rclpy.Context()
        rclpy.init(context=self.context, domain_id=domain_id)
        self.node = rclpy.create_node('test_controller', context=self.context)
        self.executor = SingleThreadedExecutor(context=self.context)
        self.executor.add_node(self.node)
        self.publisher = self.node.create_publisher(Joy, '/joy', 10)
        self.commands = []
        # The same QoS as the bridge on the Jetson (INX-140).
        self.node.create_subscription(
            TwistStamped, '/cmd_vel', self.commands.append,
            QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT))

    def spin(self, duration):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            self.executor.spin_once(timeout_sec=0.01)

    def wait_for_teleop(self):
        deadline = time.monotonic() + START_TIMEOUT
        while time.monotonic() < deadline:
            if self.publisher.get_subscription_count() and self.node.count_publishers('/cmd_vel'):
                return
            self.spin(0.1)
        pytest.fail('teleop_twist_joy did not start')

    def hold(self, state, duration=0.5):
        """Publish one controller state at the driver's repeat rate. Return the commands it causes."""
        self.commands.clear()
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            state.header.stamp = self.node.get_clock().now().to_msg()
            self.publisher.publish(state)
            self.spin(1.0 / REPEAT_RATE)
        self.spin(0.2)
        return list(self.commands)

    def close(self):
        self.executor.shutdown()
        self.node.destroy_node()
        rclpy.shutdown(context=self.context)


@pytest.fixture(scope='module')
def controller(tmp_path_factory):
    env = dict(os.environ)
    # Keep these commands away from a rover or simulation that is running on the default domain.
    env['ROS_DOMAIN_ID'] = str(50 + os.getpid() % 50)
    # Hide any real controller from the driver, so only this test publishes /joy.
    env['SDL_GAMECONTROLLER_IGNORE_DEVICES_EXCEPT'] = '0xffff/0xffff'
    log = (tmp_path_factory.mktemp('launch') / 'launch.log').open('w')
    process = subprocess.Popen(
        ['ros2', 'launch', 'innex_teleop', 'joy.launch.py'],
        env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    controller = Controller(int(env['ROS_DOMAIN_ID']))
    try:
        controller.wait_for_teleop()
        yield controller
    finally:
        controller.close()
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
        log.close()


def test_no_motion_without_enable_button(controller, params):
    commands = controller.hold(joy_state(params, forward=1.0, left=1.0, other_buttons=True))
    assert all(is_zero(command) for command in commands)


def test_drives_at_config_speeds_while_enable_held(controller, params):
    commands = controller.hold(joy_state(params, forward=1.0, left=1.0, enable=True))
    assert commands
    command = commands[-1]
    assert command.header.frame_id == 'base_link'
    assert command.twist.linear.x == pytest.approx(params['scale_linear']['x'])
    assert command.twist.angular.z == pytest.approx(params['scale_angular']['yaw'])
    assert not any((command.twist.linear.y, command.twist.linear.z,
                    command.twist.angular.x, command.twist.angular.y))

    commands = controller.hold(joy_state(params, forward=-1.0, left=-1.0, enable=True))
    assert commands[-1].twist.linear.x == pytest.approx(-params['scale_linear']['x'])
    assert commands[-1].twist.angular.z == pytest.approx(-params['scale_angular']['yaw'])


def test_releasing_enable_button_sends_zero(controller, params):
    controller.hold(joy_state(params, forward=1.0, left=1.0, enable=True))
    commands = controller.hold(joy_state(params, forward=1.0, left=1.0))
    assert commands
    assert is_zero(commands[-1])

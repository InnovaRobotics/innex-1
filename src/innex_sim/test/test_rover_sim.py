import math
import os
import re
import signal
import subprocess
import time
from typing import NamedTuple

import pytest
import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.executors import SingleThreadedExecutor
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener

from helpers import CRATERS, START_ZONE

SPAWN_TIMEOUT = 120
CLI_TIMEOUT = 60
WHEEL_JOINTS = ('front_left_wheel_joint', 'front_right_wheel_joint',
                'rear_left_wheel_joint', 'rear_right_wheel_joint')
COMMAND_RATE = 10.0
WHEELBASE = 0.705
TRACK = 0.614
OPEN_GROUND = (5.6, 2.3)
# The rover must start to stop this long after the last command (INX-155).
STOP_TIMEOUT = 0.5
STOP_TEST_SPEED = 0.25
# DiffDrive limits slowing down in reverse to 0.3 m/s² (innex_1.gazebo.xacro).
REVERSE_BRAKING = 0.3
# Allowance for the timer and for message delivery on one loaded machine.
TIMING_ALLOWANCE = 0.1


class Sim(NamedTuple):
    env: dict
    settled_pose: tuple


def read_pose(env):
    result = subprocess.run(['gz', 'model', '-m', 'innex_1', '-p'], env=env,
                            capture_output=True, text=True, timeout=CLI_TIMEOUT)
    values = [float(value) for value in re.findall(r'-?\d+\.\d+(?:e[+-]?\d+)?', result.stdout)]
    return tuple(values[:6]) if len(values) >= 6 else None


def wait_for(condition, timeout, message):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = condition()
        if value:
            return value
        time.sleep(1.0)
    pytest.fail(message)


def echo_once(env, topic, field):
    def attempt():
        result = subprocess.run(['ros2', 'topic', 'echo', '--once', '--field', field, topic],
                                env=env, capture_output=True, text=True, timeout=CLI_TIMEOUT)
        return result if result.returncode == 0 else None

    return wait_for(attempt, SPAWN_TIMEOUT, f'no message on {topic}').stdout


def place_rover(env, x, y):
    request = f'name: "innex_1", position: {{x: {x}, y: {y}, z: 0.05}}, orientation: {{w: 1}}'
    subprocess.run(['gz', 'service', '-s', '/world/moon_yard/set_pose',
                    '--reqtype', 'gz.msgs.Pose', '--reptype', 'gz.msgs.Boolean',
                    '--timeout', '5000', '--req', request],
                   env=env, check=True, capture_output=True, timeout=CLI_TIMEOUT)


def odom_yaw(env):
    text = echo_once(env, '/odom', 'pose.pose.orientation')
    z, w = (float(re.search(rf'^{axis}: (\S+)', text, re.MULTILINE).group(1)) for axis in 'zw')
    return 2.0 * math.atan2(z, w)


def angle_between(start, end):
    return (end - start + math.pi) % (2.0 * math.pi) - math.pi


def drive(env, linear_x, duration, angular_z=0.0):
    context = rclpy.Context()
    rclpy.init(context=context, domain_id=int(env['ROS_DOMAIN_ID']))
    node = rclpy.create_node('test_driver', context=context)
    publisher = node.create_publisher(TwistStamped, '/cmd_vel', 1)
    command = TwistStamped()
    command.header.frame_id = 'base_link'
    try:
        wait_for(publisher.get_subscription_count, SPAWN_TIMEOUT, 'nothing subscribed to /cmd_vel')
        command.twist.linear.x = linear_x
        command.twist.angular.z = angular_z
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            publisher.publish(command)
            time.sleep(1.0 / COMMAND_RATE)
    finally:
        command.twist.linear.x = 0.0
        command.twist.angular.z = 0.0
        publisher.publish(command)
        time.sleep(1.0 / COMMAND_RATE)
        node.destroy_node()
        rclpy.shutdown(context=context)


@pytest.fixture(scope='module')
def sim(tmp_path_factory):
    env = dict(os.environ)
    env['ROS_DOMAIN_ID'] = str(100 + os.getpid() % 100)
    env['GZ_PARTITION'] = f'innex_sim_test_{os.getpid()}'
    log = (tmp_path_factory.mktemp('launch') / 'launch.log').open('w')
    process = subprocess.Popen(
        ['ros2', 'launch', 'innex_sim', 'moon_yard.launch.py', 'gui:=false'],
        env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        wait_for(lambda: read_pose(env), SPAWN_TIMEOUT, 'the rover did not spawn')
        echo_once(env, '/odom', 'child_frame_id')

        def settled():
            first = read_pose(env)
            time.sleep(1.0)
            second = read_pose(env)
            return second if first and second and abs(first[2] - second[2]) < 1e-3 else None

        yield Sim(env, wait_for(settled, SPAWN_TIMEOUT, 'the rover did not settle'))
    finally:
        subprocess.run(['ros2', 'daemon', 'stop'], env=env, capture_output=True, timeout=CLI_TIMEOUT)
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        log.close()


def test_rover_settles_in_start_zone(sim):
    x, y, _, roll, pitch, _ = sim.settled_pose
    assert START_ZONE.x_min <= x <= START_ZONE.x_max
    assert START_ZONE.y_min <= y <= START_ZONE.y_max
    assert abs(roll) < 0.05
    assert abs(pitch) < 0.05


def test_joint_states_has_wheel_joints(sim):
    names = echo_once(sim.env, '/joint_states', 'name')
    for joint in WHEEL_JOINTS:
        assert joint in names


def test_front_camera_publishes(sim):
    topic = '/oak_front/rgb/image_raw'
    frame_id = echo_once(sim.env, topic, 'header.frame_id').splitlines()[0].strip()
    assert frame_id == 'oak_front_rgb_camera_optical_frame'


def test_rear_camera_publishes(sim):
    topic = '/oak_rear/rgb/image_raw'
    frame_id = echo_once(sim.env, topic, 'header.frame_id').splitlines()[0].strip()
    assert frame_id == 'oak_rear_rgb_camera_optical_frame'


def test_ouster_points_publishes(sim):
    topic = '/ouster/points'
    frame_id = echo_once(sim.env, topic, 'header.frame_id').splitlines()[0].strip()
    assert frame_id == 'os_sensor'


def test_odom_to_base_link_transform(sim):
    context = rclpy.Context()
    rclpy.init(context=context, domain_id=int(sim.env['ROS_DOMAIN_ID']))
    node = rclpy.create_node('test_tf_listener', context=context)
    executor = SingleThreadedExecutor(context=context)
    executor.add_node(node)
    buffer = Buffer()
    TransformListener(buffer, node, spin_thread=False)
    try:
        deadline = time.monotonic() + SPAWN_TIMEOUT
        while time.monotonic() < deadline and not buffer.can_transform('odom', 'base_link', Time()):
            executor.spin_once(timeout_sec=0.1)
        assert buffer.can_transform('odom', 'base_link', Time())
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown(context=context)


def test_rover_drives_forward(sim):
    start = read_pose(sim.env)
    drive(sim.env, 0.25, 2.5)
    time.sleep(1.5)
    end = read_pose(sim.env)
    assert 0.45 <= end[0] - start[0] <= 0.72
    assert abs(end[1] - start[1]) < 0.1


def test_rover_stops_when_commands_stop(sim):
    """Kill the command publisher mid-drive, as if teleop crashed, and check that the rover stops."""
    context = rclpy.Context()
    rclpy.init(context=context, domain_id=int(sim.env['ROS_DOMAIN_ID']))
    node = rclpy.create_node('test_stop_watcher', context=context)
    executor = SingleThreadedExecutor(context=context)
    executor.add_node(node)
    odometry = []
    commands = []
    node.create_subscription(
        Odometry, '/odom',
        lambda message: odometry.append((time.monotonic(), message.twist.twist.linear.x,
                                         message.pose.pose.position)), 10)
    # The commands that reach Gazebo.
    node.create_subscription(
        TwistStamped, '/cmd_vel_watchdog/cmd_vel',
        lambda message: commands.append((time.monotonic(), message.twist.linear.x)), 10)

    def spin(duration):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.005)

    # Reverse, so the rover stays in the start zone, clear of the rock to the east.
    publisher = subprocess.Popen(
        ['ros2', 'topic', 'pub', '--rate', str(COMMAND_RATE), '/cmd_vel',
         'geometry_msgs/msg/TwistStamped',
         f'{{header: {{frame_id: base_link}}, twist: {{linear: {{x: {-STOP_TEST_SPEED}}}}}}}'],
        env=sim.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        deadline = time.monotonic() + SPAWN_TIMEOUT
        while not odometry or odometry[-1][1] > -0.95 * STOP_TEST_SPEED:
            if time.monotonic() > deadline:
                pytest.fail('the rover did not reach the test speed')
            spin(0.1)
        # Keep the drive short, so the rover stays clear of the west wall when this test runs alone.
        spin(0.2)
        # SIGKILL, so the publisher cannot send a last zero command.
        killed = time.monotonic()
        os.killpg(publisher.pid, signal.SIGKILL)
        publisher.wait(timeout=CLI_TIMEOUT)
        spin(STOP_TIMEOUT + STOP_TEST_SPEED / REVERSE_BRAKING + 2.0)
    finally:
        if publisher.poll() is None:
            os.killpg(publisher.pid, signal.SIGKILL)
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown(context=context)

    stopped = [t for t, speed, _ in odometry if t > killed and abs(speed) < 0.01]
    assert stopped, 'the rover kept driving after the commands stopped'
    assert stopped[0] - killed <= STOP_TIMEOUT + STOP_TEST_SPEED / REVERSE_BRAKING + 0.5

    last_second = [position for t, _, position in odometry if t > odometry[-1][0] - 1.0]
    assert math.dist((last_second[0].x, last_second[0].y),
                     (last_second[-1].x, last_second[-1].y)) < 0.005

    last_command = max(t for t, linear_x in commands if linear_x)
    zeros = [t for t, linear_x in commands if t > last_command]
    assert zeros, 'no zero command reached Gazebo'
    assert zeros[0] - last_command <= STOP_TIMEOUT + TIMING_ALLOWANCE


def test_rover_turns_as_far_as_its_odometry_says(sim):
    place_rover(sim.env, *OPEN_GROUND)
    time.sleep(2.0)
    truth_start, odom_start = read_pose(sim.env)[5], odom_yaw(sim.env)
    drive(sim.env, 0.0, 4.0, angular_z=0.4)
    time.sleep(2.0)
    truth = angle_between(truth_start, read_pose(sim.env)[5])
    odom = angle_between(odom_start, odom_yaw(sim.env))
    assert odom > 0.5
    assert truth == pytest.approx(odom, rel=0.1)


def test_rover_holds_with_a_wheel_on_a_crater_slope(sim):
    crater = CRATERS[1]
    x = crater.x - WHEELBASE / 2
    y = crater.y + crater.diameter / 4 - TRACK / 2
    place_rover(sim.env, x, y)
    time.sleep(8.0)
    end = read_pose(sim.env)
    assert math.hypot(end[3], end[4]) > 0.02, 'no wheel is on the slope'
    assert math.hypot(end[0] - x, end[1] - y) < 0.02

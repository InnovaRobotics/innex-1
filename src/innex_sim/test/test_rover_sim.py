import os
import re
import signal
import subprocess
import time
from typing import NamedTuple

import pytest
import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.executors import SingleThreadedExecutor
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener

from helpers import START_ZONE

SPAWN_TIMEOUT = 120
CLI_TIMEOUT = 60
WHEEL_JOINTS = ('front_left_wheel_joint', 'front_right_wheel_joint',
                'rear_left_wheel_joint', 'rear_right_wheel_joint')
COMMAND_RATE = 10.0


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


def drive(env, linear_x, duration):
    context = rclpy.Context()
    rclpy.init(context=context, domain_id=int(env['ROS_DOMAIN_ID']))
    node = rclpy.create_node('test_driver', context=context)
    publisher = node.create_publisher(TwistStamped, '/cmd_vel', 1)
    command = TwistStamped()
    command.header.frame_id = 'base_link'
    try:
        wait_for(publisher.get_subscription_count, SPAWN_TIMEOUT, 'the bridge did not subscribe')
        command.twist.linear.x = linear_x
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            publisher.publish(command)
            time.sleep(1.0 / COMMAND_RATE)
    finally:
        command.twist.linear.x = 0.0
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

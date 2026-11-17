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

"""Verify Jazzy DDS input, steady timers and USB encoding using a virtual port."""

import os
import pty
import time

from geometry_msgs.msg import TwistStamped
from innex_drive_bridge.bridge_node import DriveBridge
from innex_drive_bridge.protocol import decode
import pytest
import rclpy
from rclpy.qos import HistoryPolicy, ReliabilityPolicy


def spin_until(node, predicate, seconds=3):
    """Run callbacks with a bounded wait."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.01)
        if predicate():
            return
    raise AssertionError('Condition did not become true')


def test_dry_run_qos_and_ros_watchdog():
    """Use actual DDS delivery, then verify zero after the command stream ends."""
    rclpy.init()
    node = DriveBridge()
    try:
        qos = node.subscription.qos_profile
        assert qos.depth == 1
        assert qos.reliability == ReliabilityPolicy.BEST_EFFORT
        assert qos.history == HistoryPolicy.KEEP_LAST
        publisher = node.create_publisher(TwistStamped, '/cmd_vel', qos)
        spin_until(node, lambda: node.sender.ready and publisher.get_subscription_count() > 0)
        message = TwistStamped()
        message.header.frame_id = 'base_link'
        message.header.stamp = node.get_clock().now().to_msg()
        message.twist.linear.x = .077
        publisher.publish(message)
        spin_until(node, lambda: decode(node.sender.transport.last_frame)[1:] == (500, 500))
        spin_until(node, lambda: node.state.reason == 'command_timeout')
        assert decode(node.sender.transport.last_frame)[1:] == (0, 0)
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


def test_paused_sim_clock_still_sends_zeros():
    """A paused ROS clock must not pause the safety send timer."""
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:=true'])
    node = DriveBridge()
    try:
        assert node.get_clock().now().nanoseconds == 0
        spin_until(node, lambda: node.sender.ready)
        assert decode(node.sender.transport.last_frame)[1:] == (0, 0)
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


def test_ros_node_with_virtual_serial(tmp_path):
    """Run serial mode only against a newly allocated /dev/pts device."""
    master, slave = pty.openpty()
    port = os.ttyname(slave)
    assert port.startswith('/dev/pts/')
    os.set_blocking(master, False)
    rclpy.init(args=[
        '--ros-args', '-p', 'dry_run:=false', '-p', 'legacy_protocol_reviewed:=true',
        '-p', f'serial_port:={port}', '-p', f'sequence_state_file:={tmp_path / "seq"}',
    ])
    node = DriveBridge()
    received = bytearray()
    frames = []

    def read_frames():
        try:
            received.extend(os.read(master, 4096))
        except BlockingIOError:
            pass
        while len(received) >= 18:
            frames.append(decode(bytes(received[:18])))
            del received[:18]
        return frames

    try:
        spin_until(node, read_frames)
        assert frames[0][1:] == (0, 0)
        publisher = node.create_publisher(TwistStamped, '/cmd_vel',
                                          node.subscription.qos_profile)
        spin_until(node, lambda: publisher.get_subscription_count() > 0)
        message = TwistStamped()
        message.header.frame_id = 'base_link'
        message.header.stamp = node.get_clock().now().to_msg()
        message.twist.linear.x = .077
        publisher.publish(message)
        spin_until(node, lambda: read_frames()[-1][1:] == (500, 500))
        spin_until(node, lambda: node.state.reason == 'command_timeout')
        read_frames()
        assert frames[-1][1:] == (0, 0)
        assert all(b[0] > a[0] for a, b in zip(frames, frames[1:]))
        os.close(master)
        master = None
        spin_until(node, lambda: node.sender.fault is not None)
        assert not node.sender.ready
        assert node.state.target == (0, 0)
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        if master is not None:
            os.close(master)
        os.close(slave)


def test_serial_requires_reviewed_protocol():
    """Reject accidental live-port enablement before any port is opened."""
    rclpy.init(args=['--ros-args', '-p', 'dry_run:=false'])
    try:
        with pytest.raises(ValueError, match='reviewed'):
            DriveBridge()
    finally:
        rclpy.shutdown()

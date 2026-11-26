"""Test ROS 2 QoS, arrival watchdog, virtual serial writes, and XML launch shutdown."""

import math
import os
import pty
import selectors
import signal
import subprocess
import time

from geometry_msgs.msg import TwistStamped
from innex_drive_bridge.drive_bridge import DriveBridge
from innex_drive_bridge.protocol import decode, FRAME_SIZE
import rclpy
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy


def spin_until(node, predicate, timeout_s=3.0):
    """Spin node until predicate returns truthy or raise AssertionError."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.01)
        if predicate():
            return
    raise AssertionError('Timed out waiting for condition')


def make_cmd(frame_id='base_link', linear_x=0.0765, angular_z=0.0, sec=100, nanosec=0):
    """Build a TwistStamped command with an explicit header timestamp."""
    msg = TwistStamped()
    msg.header.frame_id = frame_id
    msg.header.stamp.sec = sec
    msg.header.stamp.nanosec = nanosec
    msg.twist.linear.x = linear_x
    msg.twist.angular.z = angular_z
    return msg


def test_qos_arrival_watchdog_and_clock_skew():
    """Accept commands despite laptop clock skew, reject bad frames, and stop after 500 ms."""
    rclpy.init()
    node = DriveBridge()
    try:
        qos = node.subscription.qos_profile
        assert qos.depth == 1
        assert qos.reliability == ReliabilityPolicy.BEST_EFFORT
        assert qos.history == HistoryPolicy.KEEP_LAST

        pub_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE)
        publisher = node.create_publisher(TwistStamped, '/cmd_vel', pub_qos)
        spin_until(node, lambda: node.armed and publisher.get_subscription_count() > 0)
        assert decode(node.last_frame)[1:] == (0, 0)

        # Future laptop stamp (+60 s) and stepped-back stamp (1 s) must both work.
        now_sec = node.get_clock().now().seconds_nanoseconds()[0]
        publisher.publish(make_cmd(sec=now_sec + 60, linear_x=0.0765))
        spin_until(node, lambda: decode(node.last_frame)[1:] == (500, 500))

        publisher.publish(make_cmd(sec=1, linear_x=-0.0765))
        spin_until(node, lambda: decode(node.last_frame)[1:] == (-500, -500))

        # Wrong frame_id or NaN velocity clears motion on the next timer tick.
        publisher.publish(make_cmd(frame_id='map', linear_x=0.0765))
        spin_until(
            node,
            lambda: node.state == 'invalid_frame' and decode(node.last_frame)[1:] == (0, 0),
        )

        publisher.publish(make_cmd(linear_x=0.0765))
        spin_until(node, lambda: decode(node.last_frame)[1:] == (500, 500))
        publisher.publish(make_cmd(linear_x=math.nan))
        spin_until(
            node,
            lambda: node.state == 'invalid_velocity' and decode(node.last_frame)[1:] == (0, 0),
        )

        # Re-drive, then stop publishing and verify the 500 ms arrival timeout.
        publisher.publish(make_cmd(linear_x=0.0765))
        spin_until(node, lambda: decode(node.last_frame)[1:] == (500, 500))
        spin_until(
            node,
            lambda: node.state == 'command_timeout' and decode(node.last_frame)[1:] == (0, 0),
        )
    finally:
        node.close()
        node.destroy_node()
        rclpy.shutdown()


def test_paused_sim_clock_still_sends_zeros():
    """Keep the 50 Hz safety timer running on STEADY_TIME when /clock is paused."""
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:=true'])
    node = DriveBridge()
    try:
        assert node.get_clock().now().nanoseconds == 0
        spin_until(node, lambda: node.armed)
        assert decode(node.last_frame)[1:] == (0, 0)
    finally:
        node.close()
        node.destroy_node()
        rclpy.shutdown()


def test_virtual_serial_shutdown_zero_and_unplug():
    """Deliver startup zero, motion, and shutdown zero over /dev/pts, and latch unplug."""
    master, slave = pty.openpty()
    port = os.ttyname(slave)
    os.set_blocking(master, False)
    received = bytearray()
    frames = []

    def read_frames():
        while True:
            try:
                chunk = os.read(master, 4096)
                if not chunk:
                    break
                received.extend(chunk)
            except (BlockingIOError, OSError):
                break
        while len(received) >= FRAME_SIZE:
            frames.append(decode(bytes(received[:FRAME_SIZE])))
            del received[:FRAME_SIZE]
        return frames

    rclpy.init(args=['--ros-args', '-p', 'dry_run:=false', '-p', f'serial_port:={port}'])
    node = DriveBridge()
    try:
        spin_until(node, read_frames)
        assert frames[0][1:] == (0, 0)

        pub_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE)
        publisher = node.create_publisher(TwistStamped, '/cmd_vel', pub_qos)
        spin_until(node, lambda: publisher.get_subscription_count() > 0)
        publisher.publish(make_cmd(linear_x=0.0765))
        spin_until(node, lambda: read_frames()[-1][1:] == (500, 500))

        # Shut down while moving and verify the final (0, 0) frame reaches /dev/pts.
        node.close()
        read_frames()
        assert frames[-1][1:] == (0, 0)
        assert all(b[0] > a[0] for a, b in zip(frames, frames[1:]))
    finally:
        node.destroy_node()
        rclpy.shutdown()
        os.close(master)
        os.close(slave)

    # Separate check: unplugging the virtual USB peer latches serial_fault.
    master2, slave2 = pty.openpty()
    port2 = os.ttyname(slave2)
    rclpy.init(args=['--ros-args', '-p', 'dry_run:=false', '-p', f'serial_port:={port2}'])
    node2 = DriveBridge()
    try:
        spin_until(node2, lambda: node2.armed)
        os.close(master2)
        master2 = None
        spin_until(node2, lambda: node2.fault is not None)
        assert not node2.armed
        assert node2.target == (0, 0)
        assert node2.state == 'serial_fault'
    finally:
        node2.close()
        node2.destroy_node()
        rclpy.shutdown()
        if master2 is not None:
            os.close(master2)
        os.close(slave2)


def test_restart_sequence_stays_ahead():
    """Start a new bridge session with a sequence number higher than the prior run."""
    rclpy.init()
    first = DriveBridge()
    try:
        for _ in range(3):
            first.on_timer()
        last_sent = (first.sequence - 1) & 0xFFFFFFFF
    finally:
        first.close()
        first.destroy_node()

    time.sleep(0.1)
    second = DriveBridge()
    try:
        delta = (second.sequence - last_sent) & 0xFFFFFFFF
        assert 0 < delta < 0x80000000
    finally:
        second.close()
        second.destroy_node()
        rclpy.shutdown()


def test_partial_and_backlogged_write_latch_fault():
    """Latch serial_fault rather than queueing behind old bytes or sending half a frame."""
    class FakePort:
        is_open = True
        out_waiting = 1

        def write(self, frame):
            return len(frame)

        def reset_output_buffer(self):
            self.out_waiting = 0

        def close(self):
            self.is_open = False

    rclpy.init()
    node = DriveBridge()
    try:
        node.port = FakePort()
        node.on_timer()
        assert node.state == 'serial_fault'
        assert node.fault is not None
    finally:
        node.close()
        node.destroy_node()
        rclpy.shutdown()


def test_xml_launch_ctrl_c():
    """Start drive_bridge.launch.xml and confirm clean exit on Ctrl+C."""
    process = subprocess.Popen(
        ['ros2', 'launch', 'innex_drive_bridge', 'drive_bridge.launch.xml'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    output = ''
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        deadline = time.monotonic() + 10.0
        while 'state=startup_zero_sent' not in output and time.monotonic() < deadline:
            if selector.select(timeout=0.1):
                line = process.stdout.readline()
                if not line:
                    break
                output += line
        assert 'dry_run=True' in output, output
        assert 'state=startup_zero_sent' in output, output

        os.killpg(process.pid, signal.SIGINT)
        tail, _ = process.communicate(timeout=10)
        output += tail
        assert process.returncode == 0, output
        assert 'process has finished cleanly' in output, output
        assert '[drive_bridge-1] Traceback' not in output, output
    finally:
        selector.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()

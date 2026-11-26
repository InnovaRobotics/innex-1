import importlib.util
from pathlib import Path
import time

import av
from foxglove_msgs.msg import CompressedVideo
from innex_video.video_messages import nal_types
import numpy as np
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image

RELAY_SCRIPT = Path(__file__).resolve().parent.parent / 'scripts' / 'sim_video_relay.py'


def load_relay_module():
    spec = importlib.util.spec_from_file_location('sim_video_relay', RELAY_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def count_slice_nals(data):
    slices = 0
    index = 0
    length = len(data)
    while index < length - 3:
        if data[index] == 0 and data[index + 1] == 0:
            if data[index + 2] == 1:
                if (data[index + 3] & 0x1F) in (1, 5):
                    slices += 1
                index += 4
                continue
            if index + 4 < length and data[index + 2] == 0 and data[index + 3] == 1:
                if (data[index + 4] & 0x1F) in (1, 5):
                    slices += 1
                index += 5
                continue
        index += 1
    return slices


def make_image(shade, sec):
    msg = Image()
    msg.header.stamp.sec = sec
    msg.header.frame_id = 'oak_front_rgb_camera_optical_frame'
    msg.width = 160
    msg.height = 120
    msg.encoding = 'rgb8'
    msg.step = 160 * 3
    msg.data = np.full((120, 160, 3), shade, dtype=np.uint8).tobytes()
    return msg


def test_sim_video_relay_keyframes_slices_and_timestamps():
    relay_module = load_relay_module()
    context = rclpy.Context()
    rclpy.init(context=context, domain_id=77)
    relay = relay_module.SimVideoRelay(context=context)
    harness = rclpy.create_node('test_sim_video_relay', context=context)
    executor = SingleThreadedExecutor(context=context)
    executor.add_node(relay)
    executor.add_node(harness)

    publisher = harness.create_publisher(
        Image,
        '/oak_front/rgb/image_raw',
        QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT),
    )
    received = []
    subscription = harness.create_subscription(
        CompressedVideo,
        '/oak_front/video',
        received.append,
        QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE),
    )

    def spin_until(predicate, timeout=5.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            executor.spin_once(timeout_sec=0.01)
        return predicate()

    try:
        assert spin_until(
            lambda: (publisher.get_subscription_count() > 0
                     and subscription.get_publisher_count() > 0)
        )

        publisher.publish(make_image(40, sec=50))
        assert spin_until(lambda: len(received) >= 1)
        publisher.publish(make_image(80, sec=10))
        assert spin_until(lambda: len(received) >= 2)

        time.sleep(1.05)
        publisher.publish(make_image(120, sec=11))
        assert spin_until(lambda: len(received) >= 3)

        assert {5, 7, 8} <= nal_types(received[0].data)
        assert nal_types(received[1].data) == {1}
        assert {5, 7, 8} <= nal_types(received[2].data)

        for msg in received:
            assert count_slice_nals(msg.data) == 1

        stamps_ns = [
            msg.timestamp.sec * 1_000_000_000 + msg.timestamp.nanosec
            for msg in received
        ]
        assert stamps_ns[0] < stamps_ns[1] < stamps_ns[2]

        decoder = av.CodecContext.create('h264', 'r')
        decoded = []
        for msg in received:
            decoded.extend(decoder.decode(av.Packet(bytes(msg.data))))
        decoded.extend(decoder.decode(None))
        assert len(decoded) == 3
    finally:
        executor.shutdown()
        harness.destroy_node()
        relay.destroy_node()
        rclpy.shutdown(context=context)

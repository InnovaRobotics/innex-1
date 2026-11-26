#!/usr/bin/env python3
"""Encode simulated Gazebo camera images as Foxglove H.264 video."""

from fractions import Fraction
import signal
import time

from foxglove_msgs.msg import CompressedVideo
from innex_video.video_messages import make_compressed_video
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image

KEYFRAME_INTERVAL_NS = 1_000_000_000


class SimVideoRelay(Node):
    """Subscribe to one simulated image topic and publish H.264 video."""

    def __init__(self, **kwargs):
        super().__init__('sim_video_relay', **kwargs)

        self.declare_parameter('input_topic', '/oak_front/rgb/image_raw')
        self.declare_parameter('output_topic', '/oak_front/video')
        self.declare_parameter(
            'frame_id', 'oak_front_rgb_camera_optical_frame')
        self.declare_parameter('fps', 15)
        self.declare_parameter('bitrate', 1000)

        self.frame_id = self.get_parameter('frame_id').value
        self.fps = int(self.get_parameter('fps').value)
        self.bitrate = int(self.get_parameter('bitrate').value)
        self.encoder = None
        self.frame_number = 0
        self.last_keyframe_ns = 0
        self.last_timestamp_ns = 0

        output_topic = self.get_parameter('output_topic').value
        self.publisher_ = self.create_publisher(
            CompressedVideo,
            output_topic,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE),
        )
        self.create_subscription(
            Image,
            self.get_parameter('input_topic').value,
            self._on_image,
            QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT),
        )
        self.get_logger().info(
            f'Publishing simulated Foxglove video on {output_topic}')

    def _create_encoder(self, width, height):
        import av

        encoder = av.CodecContext.create('libx264', 'w')
        encoder.width = width
        encoder.height = height
        encoder.pix_fmt = 'yuv420p'
        encoder.time_base = Fraction(1, self.fps)
        encoder.framerate = Fraction(self.fps, 1)
        encoder.bit_rate = self.bitrate * 1000
        encoder.gop_size = self.fps
        encoder.thread_count = 1
        encoder.options = {
            'profile': 'baseline',
            'preset': 'ultrafast',
            'tune': 'zerolatency',
            'x264-params': 'annexb=1:repeat-headers=1:bframes=0:sliced-threads=0',
        }
        encoder.open()
        return encoder

    def _on_image(self, image_msg):
        import av

        if (self.encoder is None
                or self.encoder.width != image_msg.width
                or self.encoder.height != image_msg.height):
            self.encoder = self._create_encoder(
                image_msg.width, image_msg.height)
            self.frame_number = 0
            self.last_keyframe_ns = 0

        rows = np.frombuffer(image_msg.data, dtype=np.uint8).reshape(
            image_msg.height, image_msg.step)
        pixels = rows[:, :image_msg.width * 3].reshape(
            image_msg.height, image_msg.width, 3)

        pix_fmt = 'bgr24' if image_msg.encoding == 'bgr8' else 'rgb24'
        frame = av.VideoFrame.from_ndarray(pixels, format=pix_fmt)
        frame.pts = self.frame_number
        frame.time_base = self.encoder.time_base
        self.frame_number += 1

        now_mono_ns = time.monotonic_ns()
        if (self.last_keyframe_ns == 0
                or now_mono_ns - self.last_keyframe_ns >= KEYFRAME_INTERVAL_NS):
            frame.pict_type = av.video.frame.PictureType.I

        timestamp_ns = max(time.time_ns(), self.last_timestamp_ns + 1_000)
        self.last_timestamp_ns = timestamp_ns

        for packet in self.encoder.encode(frame):
            if packet.is_keyframe:
                self.last_keyframe_ns = now_mono_ns
            self.publisher_.publish(make_compressed_video(
                timestamp_ns, bytes(packet), self.frame_id))


def main():
    """Run the simulated H.264 video relay node."""
    rclpy.init()
    node = SimVideoRelay()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

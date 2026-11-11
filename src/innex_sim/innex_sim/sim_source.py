from fractions import Fraction
import queue
import threading
import time

import av

import cv2

from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class SimSource:
    def __init__(
        self,
        node,
        input_topic='/oak_front/rgb/image_raw',
        fps=15,
        bitrate=1000,
        video_size=(864, 480),
        frame_queue_size=2,
    ):
        self.node = node
        self.input_topic = input_topic
        self.fps = int(fps)
        self.bitrate = int(bitrate)
        self.video_size = tuple(video_size)

        self.bridge = CvBridge()
        self.frame_queue = queue.Queue(maxsize=frame_queue_size)
        self.closed = threading.Event()
        self.encoder = None
        self.frame_number = 0

        self.subscription = self.node.create_subscription(
            Image,
            self.input_topic,
            self._on_image,
            qos_profile_sensor_data,
        )

    def _create_encoder(self):
        width, height = self.video_size

        encoder = av.CodecContext.create('libx264', 'w')
        encoder.width = width
        encoder.height = height
        encoder.pix_fmt = 'yuv420p'
        encoder.time_base = Fraction(1, self.fps)
        encoder.framerate = Fraction(self.fps, 1)
        encoder.bit_rate = self.bitrate * 1000
        encoder.options = {
            'preset': 'ultrafast',
            'tune': 'zerolatency',
            'x264-params': 'annexb=1:repeat-headers=1:bframes=0',
        }
        encoder.open()
        return encoder

    def _on_image(self, image_msg):
        try:
            rgb = self.bridge.imgmsg_to_cv2(
                image_msg,
                desired_encoding='bgr8',
            )

            target_width, target_height = self.video_size
            if rgb.shape[1] != target_width or rgb.shape[0] != target_height:
                rgb = cv2.resize(rgb, (target_width, target_height))

            if self.encoder is None:
                self.encoder = self._create_encoder()

            frame = av.VideoFrame.from_ndarray(rgb, format='bgr24')
            frame.pts = self.frame_number
            frame.time_base = self.encoder.time_base
            self.frame_number += 1

            timestamp_ns = (
                image_msg.header.stamp.sec * 1_000_000_000
                + image_msg.header.stamp.nanosec
            )
            if timestamp_ns == 0:
                timestamp_ns = time.time_ns()

            for packet in self.encoder.encode(frame):
                self._put_latest((timestamp_ns, bytes(packet)))

        except Exception as exc:
            self.node.get_logger().error(f'Could not encode simulated image: {exc}')

    def _put_latest(self, item):

        try:
            self.frame_queue.put_nowait(item)
        except queue.Full:
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.frame_queue.put_nowait(item)
            except queue.Full:
                pass

    def frames(self):
        while not self.closed.is_set():
            try:
                yield self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

    def close(self):
        self.closed.set()
        self.node.destroy_subscription(self.subscription)

"""Tests for camera-independent H.264 message helpers."""

from innex_video.video_messages import make_compressed_video, nal_types


def test_nal_types_in_keyframe():
    keyframe = (
        b'\x00\x00\x00\x01\x67\x42\x00\x1e'
        b'\x00\x00\x01\x68\xce\x06\xe2'
        b'\x00\x00\x00\x01\x65\x88\x84')

    assert nal_types(keyframe) == {5, 7, 8}


def test_nal_types_for_single_raw_nal():
    assert nal_types(b'\x65\x88\x84') == {5}


def test_make_compressed_video():
    timestamp_ns = 12_345_678_901
    data = b'\x00\x00\x01\x65\x88'

    message = make_compressed_video(timestamp_ns, data, 'oak_front_frame')

    assert message.timestamp.sec == 12
    assert message.timestamp.nanosec == 345_678_901
    assert message.frame_id == 'oak_front_frame'
    assert message.format == 'h264'
    assert bytes(message.data) == data

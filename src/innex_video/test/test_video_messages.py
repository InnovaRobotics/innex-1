"""Tests for camera-independent H.264 message and device selection helpers."""

from innex_video.video_messages import make_compressed_video, nal_types
from innex_video.video_relay import select_device_id


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


def test_select_device_id_single_bench_camera():
    selected, reason = select_device_id(['1944A'], allow_auto_device=True)
    assert selected == '1944A'
    assert reason is None

    skipped, skip_reason = select_device_id(['1944A'], allow_auto_device=False)
    assert skipped is None
    assert 'skipping' in skip_reason


def test_select_device_id_refuses_to_guess_two_cameras():
    selected, reason = select_device_id(
        ['1944B', '1944A'], allow_auto_device=True)
    assert selected is None
    assert '1944A, 1944B' in reason


def test_select_device_id_configured_camera():
    selected, reason = select_device_id(
        ['1944A', '1944B'], configured_id='1944B')
    assert selected == '1944B'
    assert reason is None

    missing, missing_reason = select_device_id(
        ['1944A'], configured_id='1944B')
    assert missing is None
    assert 'not connected' in missing_reason

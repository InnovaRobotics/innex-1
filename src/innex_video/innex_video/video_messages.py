"""Helpers for Foxglove H.264 video messages."""

from foxglove_msgs.msg import CompressedVideo


def nal_types(data):
    """Return the H.264 NAL unit types present in Annex B encoded data."""
    data = bytes(data)
    headers = []
    offset = 0

    while offset < len(data) - 2:
        if data[offset:offset + 4] == b'\x00\x00\x00\x01':
            headers.append(offset + 4)
            offset += 4
        elif data[offset:offset + 3] == b'\x00\x00\x01':
            headers.append(offset + 3)
            offset += 3
        else:
            offset += 1

    if not headers and data:
        # Accept an individual raw NAL unit as well as Annex B byte streams.
        headers.append(0)

    return {data[index] & 0x1f for index in headers if index < len(data)}


def make_compressed_video(timestamp_ns, data, frame_id):
    """Build a Foxglove CompressedVideo message from frame data and metadata."""
    message = CompressedVideo()
    message.timestamp.sec = int(timestamp_ns) // 1_000_000_000
    message.timestamp.nanosec = int(timestamp_ns) % 1_000_000_000
    message.frame_id = frame_id
    message.format = 'h264'
    message.data = bytes(data)
    return message

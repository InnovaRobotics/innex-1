"""Stream H.264 packets from an OAK camera using DepthAI v3."""

import time

import depthai as dai


def find_camera_id(camera_role, device_id=''):
    """Find a configured OAK device, assigning sorted IDs to front/rear."""
    if camera_role not in ('front', 'rear'):
        raise ValueError("camera_role must be 'front' or 'rear'")

    devices = dai.Device.getAllAvailableDevices()
    if device_id:
        for device in devices:
            if str(device.deviceId) == str(device_id):
                return str(device.deviceId)
        available_ids = ', '.join(
            str(device.deviceId) for device in devices) or 'none'
        raise RuntimeError(
            f'Configured {camera_role} OAK ID {device_id!r} is not connected. '
            f'Available IDs: {available_ids}.')

    devices = sorted(devices, key=lambda device: str(device.deviceId))
    if len(devices) != 2:
        ids = ', '.join(str(device.deviceId) for device in devices) or 'none'
        raise RuntimeError(
            f'Expected two connected OAK cameras, found {len(devices)}: {ids}. '
            'Set front_device and rear_device explicitly if needed.')

    index = 0 if camera_role == 'front' else 1
    return str(devices[index].deviceId)


class OakH264Recorder:
    """Expose an OAK camera's H.264 encoder as a timestamped frame source."""

    def __init__(
        self,
        front_output=None,
        back_output=None,
        fps=15,
        bitrate_Kbps=1000,
        video_size=(864, 480),
        camera_socket=None,
        device_id='',
        camera_role='front',
    ):

        del front_output, back_output
        self.fps = int(fps)
        self.bitrate_Kbps = int(bitrate_Kbps)
        self.video_size = tuple(video_size)
        self.closed = False

        selected_id = find_camera_id(camera_role, device_id)
        self.device = dai.Device(dai.DeviceInfo(selected_id))
        self.pipeline = dai.Pipeline(self.device)

        camera_node = self.pipeline.create(dai.node.ColorCamera)
        encoder = self.pipeline.create(dai.node.VideoEncoder)
        camera_node.setBoardSocket(
            camera_socket or dai.CameraBoardSocket.CAM_A)
        camera_node.setVideoSize(*self.video_size)
        camera_node.setFps(self.fps)
        encoder.setDefaultProfilePreset(
            self.fps, dai.VideoEncoderProperties.Profile.H264_MAIN)
        encoder.setBitrateKbps(self.bitrate_Kbps)
        camera_node.video.link(encoder.input)
        self.output_queue = encoder.bitstream.createOutputQueue(
            maxSize=15, blocking=False)

        self.pipeline.start()

    def frames(self):
        """Yield timestamp and H.264 access-unit pairs until closed."""
        while not self.closed:
            packet = self.output_queue.tryGet()
            if packet is None:
                time.sleep(0.005)
                continue

            yield time.time_ns(), bytes(packet.getData())

    def close(self):
        """Stop the OAK pipeline and release the connected device."""
        if self.closed:
            return
        self.closed = True
        self.pipeline.stop()
        self.device.close()

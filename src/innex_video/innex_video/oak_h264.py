"""Stream H.264 packets from an OAK camera using DepthAI v3."""

import time

import depthai as dai


class OakH264:
    """Expose an OAK camera's H.264 encoder as a timestamped frame source."""

    def __init__(
        self,
        device_id=None,
        width=864,
        height=480,
        fps=15,
        bitrate_kbps=1000,
        keyframe_every=15,
    ):
        self.fps = int(fps)
        self.width = int(width)
        self.height = int(height)
        self.bitrate_kbps = int(bitrate_kbps)
        self.keyframe_every = int(keyframe_every)
        self.closed = False

        devices = dai.Device.getAllAvailableDevices()
        if device_id is None:
            if len(devices) != 1:
                available_ids = ', '.join(
                    str(device.deviceId) for device in devices) or 'none'
                raise RuntimeError(
                    'OakH264 requires a device_id when zero or multiple OAK '
                    f'cameras are connected; found {len(devices)}: '
                    f'{available_ids}.')
            selected_id = str(devices[0].deviceId)
        else:
            selected_id = str(device_id)
            if not any(str(device.deviceId) == selected_id
                       for device in devices):
                available_ids = ', '.join(
                    str(device.deviceId) for device in devices) or 'none'
                raise RuntimeError(
                    f'Configured OAK ID {selected_id!r} is not connected. '
                    f'Available IDs: {available_ids}.')

        self.device = dai.Device(dai.DeviceInfo(selected_id))
        self.pipeline = dai.Pipeline(self.device)

        camera = self.pipeline.create(dai.node.Camera).build(
            dai.CameraBoardSocket.CAM_A)
        video = camera.requestOutput(
            size=(self.width, self.height),
            type=dai.ImgFrame.Type.NV12,
            fps=self.fps)
        encoder = self.pipeline.create(dai.node.VideoEncoder).build(
            video,
            frameRate=self.fps,
            profile=dai.VideoEncoderProperties.Profile.H264_BASELINE,
            keyframeFrequency=self.keyframe_every)
        encoder.setBitrateKbps(self.bitrate_kbps)
        self.output_queue = encoder.out.createOutputQueue(
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

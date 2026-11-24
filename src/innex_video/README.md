# innex_video

Streams H.264 video from the front and rear OAK-D Pro cameras as `foxglove_msgs/msg/CompressedVideo` messages for Foxglove. Encoding runs on each camera's Myriad X processor so the Jetson spends no CPU time on compression.

## Setup on Ubuntu 24.04

1. Allow non-root USB access to Luxonis cameras:
   ```bash
   echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
   sudo udevadm control --reload-rules && sudo udevadm trigger --subsystem-match=usb --action=add
   ```
2. Install the DepthAI v3 Python library into your user site packages (`numpy` comes from Ubuntu's `python3-numpy` package):
   ```bash
   python3 -m pip install --user --break-system-packages --no-deps depthai==3.12.1
   ```

See the [Luxonis USB deployment guide](https://docs.luxonis.com/hardware/platform/deploy/usb-deployment-guide/) and [DepthAI v3 installation guide](https://docs.luxonis.com/software-v3/depthai/#installation) for other platforms.

## Launch

```bash
ros2 launch innex_video video.launch.xml
```

With one camera connected and `config/camera_ids.yaml` left blank, `front_video_relay` claims that camera and publishes `/oak_front/video`. When two cameras are mounted on the rover, put both OAK `deviceId` strings in `config/camera_ids.yaml` so front and rear feeds stay fixed to their physical mounts.

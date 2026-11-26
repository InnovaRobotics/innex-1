# innex_drive_bridge

Bridges `/cmd_vel` velocity commands on the Jetson to left and right wheel targets on the Teensy 4.1 over USB serial.

## Launch

Build and source the workspace, then start the bridge:

```bash
ros2 launch innex_drive_bridge drive_bridge.launch.xml
```

By default `dry_run` is `true`, so the node converts commands and runs its 500 ms stop timer without opening a serial device.

To connect a Teensy 4.1 on Ubuntu 24.04:

1. Add your user to the `dialout` group once so Python can open serial ports without root, then log out and back in:
   ```bash
   sudo usermod -aG dialout $USER
   ```
2. Plug in the Teensy and copy its stable path under `/dev/serial/by-id/` so USB port numbers cannot swap across reboots:
   ```bash
   ls -l /dev/serial/by-id/
   ```
3. Set `dry_run: false` and `serial_port` in `config/drive_bridge.yaml` (or pass `config:=/path/to/bridge.yaml` to `ros2 launch`).

Follow [Rover safety](../../docs/safety.md) before commanding real motors. On `main`, [firmware/teensy_drive](../../firmware/teensy_drive/README.md) uses a dry-run output adapter in `src/main.cpp` and does not drive physical motor pins until the Sabertooth wiring and session protocol are integrated.

## Parameters

The defaults live in `config/drive_bridge.yaml`. All parameters are read-only once the node starts.

| Parameter | Default | Meaning |
|---|---|---|
| `dry_run` | `true` | Run without opening a serial port |
| `serial_port` | `""` | Path to the Teensy serial device, such as `/dev/serial/by-id/...` |
| `send_rate_hz` | `50.0` | Rate at which 18-byte frames are sent to the Teensy, in Hz (20 to 100) |
| `wheel_radius_m` | `0.154` | Wheel radius in metres (CAD estimate until measured on the rover) |
| `track_width_m` | `0.614` | Distance between left and right wheel centres in metres (CAD estimate) |
| `command_frame` | `base_link` | Required `header.frame_id` on incoming `/cmd_vel` messages |

The wheel speed cap (`LIMIT_MRAD_S = 1000`, or `1.0` rad/s, which is `0.154` m/s straight ahead at a `0.154` m wheel radius) is defined in `innex_drive_bridge/protocol.py` and checked by test against `kPrototypeLimitMrad` in `DriveCore.h`. When both wheels exceed the cap during a turn, `wheel_targets` scales both sides together so the turning radius stays constant.

## Topics and stopping

| ROS topic | Type | Description |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | Body velocity command in `base_link`, subscribed with best-effort QoS and depth 1 |

Subscribing with best-effort QoS and a depth of 1 discards waiting packets if Wi-Fi stalls, so the bridge acts only on the most recent command.

On startup, the bridge sends `(0, 0)` before accepting motion so `DriveCore` on the Teensy arms cleanly. Each valid `/cmd_vel` resets a 500 ms deadline on the Jetson's monotonic clock (independent of laptop wall-clock offsets). When no `/cmd_vel` arrives for 500 ms, the bridge sends `(0, 0)` at 50 Hz. On `SIGINT` or `SIGTERM`, it finishes the active callback, writes one final `(0, 0)` frame, and waits up to 50 ms for the output buffer to drain before closing the port.

If a serial write times out or the USB cable disconnects, the bridge clears its target to `(0, 0)`, closes the port, and latches a fault until you inspect the cable and restart the node; the Teensy's independent 250 ms timer stops its outputs on its side. Sequence numbers start from Jetson monotonic uptime in milliseconds, so restarting `drive_bridge` on a running Jetson stays ahead of a USB-powered Teensy's counter. If the Jetson reboots while the Teensy stays powered from a separate supply, reset the Teensy so its sequence state clears (see [PROTOCOL.md](../../firmware/teensy_drive/PROTOCOL.md)).

## Test

```bash
colcon build --packages-select innex_drive_bridge
colcon test --packages-select innex_drive_bridge
colcon test-result --verbose
```

The tests need no Teensy or game controller. They compile `DriveCore.cpp` with `g++` to verify wire and speed-limit compatibility, and allocate a virtual `/dev/pts` serial port to check startup zero, the 500 ms stop, shutdown zero delivery, and cable unplug handling.

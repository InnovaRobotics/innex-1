# Comms and mission control

Everything the operator sees inside mission control and every gamepad command sent to the rover crosses this link. Comms and mission control cover the GL.iNet GL-A1300 router, the wireless transport between the mission control laptop and the Jetson, and the Foxglove operator dashboard. Nothing here decides how to steer or dig; this subsystem carries video, telemetry and commands cleanly inside the competition's `4,000 kbps` average cap.

On `main` today, [`innex_video`](../../src/innex_video/README.md) encodes front and rear OAK-D Pro streams into H.264 on each camera's Myriad X processor, publishes `/oak_front/video` and `/oak_rear/video` as `foxglove_msgs/msg/CompressedVideo`, and serves them over `foxglove_bridge` on port `8765` (`moon_yard.launch.xml video:=true` runs the matching H.264 pipeline in simulation). Router network reservations (`192.168.8.1` and `192.168.8.10`) are documented in [Jetson](../jetson.md#rover-router). Cross-machine gamepad transport tuning, telemetry panels and 20-minute bandwidth logging remain open.

## Staying inside the 4,000 kbps budget

Four thousand kilobits per second looks comfortable until you calculate raw sensor bitrates. A single uncompressed `1280 x 720` colour stream at `30` frames per second pushes about `330,000 kbps`, more than eighty times the entire competition allowance. One `128`-beam Ouster LiDAR scan holds tens of thousands of 3D points and repeats `10` times per second.

Raw point clouds and depth maps therefore stay onboard the Jetson where perception and localisation consume them, and cameras compress operator video to **H.264** before a single byte touches ROS. Instead of sending thirty full pictures every second, H.264 sends one complete reference image (called a **keyframe**) once per second along with stream setup headers, and for the frames in between transmits only the pixel blocks that moved. In `innex_video`, each OAK-D Pro runs that encoder inside its own Myriad X chip, capping two crisp operator views well inside the link budget while spending zero Jetson CPU time.

Because the rule caps the *average* rate across a run instead of instantaneous peaks, brief bursts when turning across textured sand are legal, though sustained congestion still delays `/cmd_vel` packets. Three streams share the `4,000 kbps` ceiling:

- Front and rear H.264 camera video (`/oak_front/video` and `/oak_rear/video`), the largest share of the link.
- Lightweight telemetry: rover pose, odometry, watchdog and Teensy armed status, and autonomous step state.
- Middleware discovery traffic from ROS 2 nodes announcing themselves across the network.

Measure average throughput across a full 20-minute rehearsal instead of extrapolating from a two-minute bench check, so reconnection bursts or unthrottled diagnostic topics cannot creep past the limit.

## Why ROS 2 discovery breaks on Wi-Fi

Out of the box, ROS 2's **DDS** (Data Distribution Service) middleware discovers nodes across machines by broadcasting UDP multicast packets to every device on the subnet. Multicast works fine over a bench Ethernet cable and breaks unpredictably over Wi-Fi, because access points routinely throttle, buffer or drop multicast frames. When discovery packets drop, topics vanish mid-run or never connect at all.

INNEX-1 avoids multicast fragility by splitting dashboard traffic from gamepad commands:

- For video and telemetry flowing to Foxglove, `foxglove_bridge` opens a single TCP WebSocket connection (`ws://192.168.8.10:8765`). In `video.launch.xml`, `topic_whitelist` exposes only explicit topics (`^/oak_(front|rear)/video$`, extended as telemetry topics land), stopping an accidental subscriber in Foxglove from pulling a raw point cloud across Wi-Fi. Setting `client_topic_whitelist`, `service_whitelist` and `param_whitelist` to match nothing (`(?!)`) locks Foxglove into a strictly read-only viewer so touching a panel cannot transmit anything to the rover.
- For `/cmd_vel` gamepad commands flowing from the laptop to the Jetson, ROS 2 Jazzy offers two multicast-free paths: configuring unicast static discovery peers using the fixed `192.168.8.x` addresses ([Improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)), or running [`rmw_zenoh`](https://github.com/ros2/rmw_zenoh) over TCP. Benchmarking command latency and reconnect recovery between those two options on the GL-A1300 router is an open task.

## Rehearsing the 15-minute comm check

Exceeding 15 minutes at the communications inspection station disqualifies the team before its first run, so rehearse the check as a timed drill. While waiting in the queue, set the router to Wi-Fi channel 1 (`20 MHz` width) and keep every wireless radio powered off until the judge starts your clock. Inside the 15-minute window:

1. Show the judges every wireless component on the rover.
2. Connect from the mission control laptop and drive the rover wirelessly.
3. Switch off the router's `2.4 GHz` band on demand.

Bring printed manufacturer datasheets listing part number, frequency and output power for any Bluetooth or non-Wi-Fi radio. See [Rover router](../jetson.md#rover-router) for the GL-A1300 tunnel command and pre-competition SSID checklist.

## What the operator sees in mission control

During a run, arena teammates cannot call out boulder positions, crater edges or berm alignment, and operating with zero arena cameras earns `120` points. That puts the entire burden of visibility on the Foxglove layout: front video has to frame the bucket ladder and obstacles ahead, rear video has to frame the dump chute and red berm target zone when reversing, and status indicators have to show link health, Teensy armed state and whether the rover is in teleop, hands-free autonomy or stopped.

## Requirements and competition rules

Subsystem requirements:

- Deliver gamepad commands from the mission control laptop to the Jetson with low latency and no stale queueing.
- Stream front and rear H.264 video plus read-only telemetry to Foxglove inside an average `4,000 kbps` budget over a 20-minute run.
- Establish cross-machine ROS 2 communication over Wi-Fi without relying on UDP multicast.
- Show clearly when the link drops and confirm that the rover has disarmed.
- Pass the 15-minute communications check cleanly.

Applicable rules:

- [Communications](../rules.md#communications): dual-band router (`2.4 GHz` at `20 MHz` width plus `5 GHz`), assigned broadcast SSID, WPA2/WPA3 encryption, and `4,000 kbps` maximum average data rate.
- [Comm check](../rules.md#comm-check): 15-minute inspection on channel 1 showing hardware, wireless control and `2.4 GHz` shut-off.
- [Mission control](../rules.md#mission-control) and [Hands-free rules](../rules.md#hands-free-rules): operate from rover feeds alone; send zero commands, orientation data or obstacle positions during autonomous attempts.
- [Scoring](../rules.md#scoring): `120` points for using zero arena cameras.
- [Organiser clarifications](../rules.md#organiser-clarifications-provisional): under the provisional 4 November email, the arena supplies corner mains power and Ethernet back to mission control for the team's router, so the rover carries a Wi-Fi client radio only.

## Open questions

1. Which ROS 2 transport gives lower `/cmd_vel` jitter and cleaner Wi-Fi drop recovery through the GL-A1300 router: static DDS peers or `rmw_zenoh`?
2. Which telemetry topics join `/oak_front/video` and `/oak_rear/video` in `foxglove_bridge`'s `topic_whitelist`, and at what Hz?
3. What script or router counter records average kbps over a full 20-minute rehearsal so we can prove compliance?
4. Will the final 2027 rulebook confirm the corner-router and arena-Ethernet layout from the 4 November email?
5. What Foxglove panel layout gives the clearest driving cues during teleop and clear hands-free status during autonomy?

## Further reading

- [`innex_video` README](../../src/innex_video/README.md) and [Jetson router setup](../jetson.md#rover-router)
- [foxglove_bridge](https://index.ros.org/p/foxglove_bridge/) and [Foxglove Image panel](https://docs.foxglove.dev/docs/visualization/panels/image)
- [Improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)
- [rmw_zenoh](https://github.com/ros2/rmw_zenoh)
- [DepthAI v3 documentation](https://docs.luxonis.com/software-v3/depthai/)

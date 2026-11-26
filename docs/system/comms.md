# Comms and mission control

Everything the operator sees inside mission control and every gamepad command sent to the rover crosses this wireless link. Comms and mission control cover the GL.iNet GL-A1300 router, network transport between the mission control laptop and the Jetson, and the Foxglove operator display. Nothing in this subsystem makes steering or autonomy decisions; it carries video, telemetry and commands reliably within the competition's 4,000 kbps average data-rate limit.

[`innex_video`](../../src/innex_video/README.md) encodes front and rear OAK-D Pro streams into H.264 on each camera's Myriad X processor, publishes `/oak_front/video` and `/oak_rear/video` as `foxglove_msgs/msg/CompressedVideo`, and streams them through `foxglove_bridge` on port `8765`. Router addresses (`192.168.8.1` and `192.168.8.10`) are documented in [Jetson](../jetson.md#rover-router).

## Bandwidth budget

Four thousand kilobits per second looks generous until you calculate uncompressed sensor rates. A single raw 1280 × 720 colour camera stream at 30 frames per second produces roughly 330,000 kbps, more than eighty times the total competition allowance. One 128-beam Ouster LiDAR scan contains tens of thousands of 3D points and repeats 10 times per second.

Raw point clouds and depth maps therefore stay on the Jetson where perception and localisation process them, while operator cameras compress video to **H.264** in hardware. Instead of sending full images on every frame, H.264 transmits one complete reference image (**keyframe**) once per second with stream headers, and in the frames between sends only the pixel blocks that changed. Running that encoder on each camera's Myriad X chip keeps two clear operator feeds comfortably inside the link budget while using zero Jetson CPU time.

Because the rule limits the *average* rate across a run instead of short peaks, brief bitrate increases while turning across textured sand are allowed, though sustained link congestion still delays `/cmd_vel` packets. Three traffic types share the 4,000 kbps allowance:

- Front and rear H.264 video (`/oak_front/video` and `/oak_rear/video`), which accounts for most of the bandwidth.
- Compact status telemetry: rover pose, odometry, watchdog and Teensy armed state, and autonomous step status.
- ROS 2 node discovery announcements.

Always measure average link throughput across a full 20-minute rehearsal instead of scaling up a two-minute bench test, so reconnection bursts or unthrottled diagnostic topics do not push the run average over 4,000 kbps.

## Wireless discovery

By default, ROS 2's **DDS** (Data Distribution Service) middleware discovers nodes across computers by sending UDP multicast packets to every device on the local network. Multicast works reliably over Ethernet on a bench and fails unpredictably over Wi-Fi, because wireless routers routinely throttle or drop multicast traffic. When discovery packets drop, topics disappear mid-run or fail to connect at startup.

INNEX-1 separates operator display traffic from gamepad command transport to avoid multicast failures:

- For video and telemetry flowing to Foxglove, `foxglove_bridge` opens a single TCP WebSocket connection (`ws://192.168.8.10:8765`). In `video.launch.xml`, `topic_whitelist` exposes only explicitly listed topics (`^/oak_(front|rear)/video$` plus telemetry topics), preventing an accidental Foxglove subscription from pulling a raw point cloud over Wi-Fi. Setting `client_topic_whitelist`, `service_whitelist` and `param_whitelist` to `(?!)` keeps Foxglove strictly read-only so clicking a panel cannot transmit commands during hands-free autonomy.
- For `/cmd_vel` gamepad commands sent from the laptop to the Jetson, ROS 2 Jazzy provides two multicast-free options: unicast static discovery peers configured with the fixed `192.168.8.x` addresses ([Improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)), or [`rmw_zenoh`](https://github.com/ros2/rmw_zenoh) routing over TCP.

## Comm check procedure

Taking longer than 15 minutes at the communications inspection station disqualifies the team before its first run, so rehearse the procedure as a timed drill. While waiting in the queue, set the router to Wi-Fi channel 1 (20 MHz width) and keep all wireless radios powered off until the judge starts your slot. Inside the 15-minute window:

1. Show the judges every wireless component on the rover.
2. Connect from the mission control laptop and drive the rover wirelessly.
3. Switch off the router's 2.4 GHz band on demand.

Bring printed manufacturer datasheets listing part number, frequency and output power for any Bluetooth or non-Wi-Fi radio. See [Rover router](../jetson.md#rover-router) for the GL-A1300 admin tunnel command and pre-competition SSID checklist.

## Operator display

During a run, arena teammates cannot communicate boulder positions, crater edges or berm alignment to mission control, and running without arena cameras earns 120 points. The Foxglove layout therefore has to give complete situational awareness on its own: front video framing the bucket ladder and path ahead, rear video framing the dump chute and berm target area when reversing, and clear indicators for link health, Teensy armed state and active control mode (teleop, hands-free autonomy or disarmed).

## Rules and constraints

- Carry low-latency gamepad commands to the Jetson and stream front/rear H.264 video plus read-only telemetry to Foxglove inside a 4,000 kbps run average ([Communications](../rules.md#communications), [Scoring](../rules.md#scoring)).
- Complete wireless inspection and 2.4 GHz band shut-off on channel 1 within 15 minutes ([Comm check](../rules.md#comm-check)).
- Operate solely from rover feeds in mission control, and transmit zero commands, orientation data or obstacle positions during autonomous attempts ([Mission control](../rules.md#mission-control), [Hands-free rules](../rules.md#hands-free-rules)).
- Under the provisional 4 November organiser email, connect the team router to arena corner power and Ethernet back to mission control so the rover carries a Wi-Fi client radio only ([Organiser clarifications](../rules.md#organiser-clarifications-provisional)).

## Further reading

- [`innex_video` README](../../src/innex_video/README.md) and [Jetson router setup](../jetson.md#rover-router)
- [foxglove_bridge](https://index.ros.org/p/foxglove_bridge/) and [Foxglove Image panel](https://docs.foxglove.dev/docs/visualization/panels/image)
- [Improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)
- [rmw_zenoh](https://github.com/ros2/rmw_zenoh)
- [DepthAI v3 documentation](https://docs.luxonis.com/software-v3/depthai/)

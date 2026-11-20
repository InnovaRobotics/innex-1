# Comms and mission control

Everything the operator sees in mission control and every command sent back to the rover travels over this link. Comms and mission control own the router setup, the wireless link between the mission control laptop and the Jetson, and the Foxglove operator dashboard. Nothing in this subsystem makes driving or autonomy decisions; it carries messages cleanly within the competition bandwidth cap while the other subsystems decide what to send.

## Requirements

- Carry gamepad commands from the mission control laptop to the Jetson with low latency.
- Carry compressed front and rear video plus read-only telemetry from the rover to the laptop.
- Keep the average wireless data rate at or below 4,000 kbps across a full run.
- Keep ROS 2 discovery reliable over Wi-Fi without relying on multicast.
- Show clearly when the link drops and confirm that the rover has stopped.
- Pass the 15-minute communications check cleanly.

## Competition rules

- [Communications](../rules.md#communications): use a dual-band router (2.4 GHz and 5 GHz), broadcast the assigned SSID with WPA2 or WPA3 encryption, set 2.4 GHz width to 20 MHz, and keep average traffic at or below 4,000 kbps (peaks above 4,000 kbps are allowed).
- [Comm check](../rules.md#comm-check): complete the timed inspection on Wi-Fi channel 1 within 15 minutes (show every wireless part, drive the rover wirelessly and turn off 2.4 GHz on demand).
- [Mission control](../rules.md#mission-control): operate using only data and video from the rover and the arena camera monitors.
- [Hands-free rules](../rules.md#hands-free-rules): watch read-only telemetry during an autonomous attempt; send no commands, orientation data or obstacle locations.
- [Scoring](../rules.md#scoring): avoiding both arena cameras scores 120 points, so rover video has to give the operator full visibility.
- [Organiser clarifications](../rules.md#organiser-clarifications-provisional): under the 4 November email (provisional until the final 2027 rulebook), the arena provides a mains power socket and an Ethernet cable in one corner for the team's router, feeding straight to mission control so the rover carries a Wi-Fi client radio only.

## Staying inside the 4,000 kbps budget

Four thousand kilobits per second sounds generous until you look at raw robotics data. A single uncompressed 720p colour camera stream at 30 frames per second eats roughly 330,000 kbps, more than eighty times the entire competition cap. A 128-beam LiDAR publishes tens of thousands of 3D points several times every second.

Because the rule limits the *average* rate across a run instead of instantaneous peaks, short bursts are legal, though sustained congestion still delays gamepad commands. Three kinds of traffic share the budget:

- Operator video is the largest consumer, and two cameras (front and rear) double it. Each OAK-D Pro compresses its stream to H.264 inside its own hardware encoder, so you can cap bitrate directly (around 1,000 kbps per camera) without burning Jetson CPU power.
- Telemetry carries pose, odometry, command selector state, autonomous step state and Teensy health. Raw camera images, depth frames and LiDAR point clouds stay onboard the Jetson where perception and localisation consume them.
- Discovery traffic comes from ROS 2 nodes announcing themselves across the network, and it grows with every node and topic exposed over the link.

Always measure average link traffic across a full 20-minute rehearsal. Short five-minute checks miss slow growth from diagnostic topics, reconnections or bursts when driving across textured sand.

## Why ROS 2 discovery breaks on Wi-Fi

ROS 2 uses a messaging middleware called **DDS** (Data Distribution Service). Out of the box, nodes on different machines find each other by broadcasting UDP multicast packets across the local network. That works reliably over an Ethernet cable on a lab bench, and fails unpredictably over Wi-Fi because routers routinely throttle or drop multicast traffic. When multicast breaks, topics appear and vanish at random, or a topic published on the Jetson never reaches the laptop.

The architecture handles this in two layers:

- For video and telemetry, `foxglove_bridge` opens one plain WebSocket connection from the laptop to the Jetson and forwards only topics listed on an explicit allow-list. That stops an accidental subscriber from pulling a raw point cloud across Wi-Fi, and running the bridge with client publishing disabled guarantees the dashboard stays read-only during hands-free autonomy.
- For ROS 2 gamepad commands travelling to the rover, two multicast-free options exist on ROS 2 Jazzy: configuring static DDS discovery peers using fixed IP addresses (covered in the Jazzy [improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html) guide), or switching the middleware to `rmw_zenoh`, which routes traffic over TCP without multicast. Testing both on the competition router is an open item.

## The comm check

Because exceeding 15 minutes disqualifies the team, rehearse the communications inspection like a drill. While waiting in the queue, configure equipment for Wi-Fi channel 1 and keep every wireless radio powered off until your slot begins. At the inspection table:

1. Show the judges every wireless component on the rover.
2. Connect from the mission control laptop and control the rover wirelessly.
3. Turn off the router's 2.4 GHz band on demand.

Bring printed datasheets showing part number, frequency and power output for any Bluetooth or non-Wi-Fi radio.

## What the operator sees

Inside mission control, arena teammates cannot call out rocks, craters or berm alignment, and skipping both arena cameras earns 120 points. That means the Foxglove dashboard has to tell the operator everything required to drive safely, align the bucket ladder, judge a full load and dump cleanly onto the berm, while clearly indicating Teensy health, link status and whether the rover is in teleop, hands-free autonomy or stopped.

## Open questions

1. Which ROS 2 transport carries gamepad commands most reliably over the competition router: static DDS peers or `rmw_zenoh`?
2. Which exact telemetry topics cross `foxglove_bridge`, and at what publish rates?
3. How does the team measure and log average link throughput across a full 20-minute rehearsal?
4. Will the final 2027 rulebook confirm the corner-router and arena-Ethernet layout from the 4 November organiser email?
5. What exact panels and status warnings appear on the operator Foxglove layout during teleop versus hands-free autonomy?

## Further reading

- [foxglove_bridge](https://index.ros.org/p/foxglove_bridge/)
- [Foxglove Image panel](https://docs.foxglove.dev/docs/visualization/panels/image)
- [Improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)
- [rmw_zenoh](https://github.com/ros2/rmw_zenoh)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)

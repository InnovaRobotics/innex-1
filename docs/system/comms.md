# Comms and mission control

The operator sees and drives the rover over the link. This page covers the router, the link between the laptop and the Jetson, and what the operator sees in mission control.

## Requirements

- Carry operator commands from the laptop to the Jetson.
- Carry video and telemetry from the rover to the laptop.
- Keep the average data rate at or below 4,000 kbps over a whole run.
- Let ROS 2 on the laptop and on the Jetson find each other and keep talking.
- Stop the rover when the link goes quiet, and show the operator that it has stopped.
- Pass the comm check.

Nothing in this subsystem makes driving decisions. It carries messages. The other subsystems decide what to send.

## Rules

- [Communications](../rules.md#communications): a dual-band router, the assigned network name, a broadcast SSID, WPA2 or WPA3, and an average of 4,000 kbps or less with no peak limit.
- [Comm check](../rules.md#comm-check): 15 minutes on Wi-Fi channel 1. Show every wireless part, control the robot wirelessly, and turn off the router's 2.4 GHz band.
- [Mission control](../rules.md#mission-control): use only data and video from the robot and the arena camera monitors.
- [Hands-free rules](../rules.md#hands-free-rules): during an autonomous attempt, watch telemetry only. Send no commands, orientation data or obstacle locations.
- [Scoring](../rules.md#scoring): each arena camera you use costs points. Rover video gives the operator the view.
- [Undefined in v1.0](../rules.md#undefined-in-v10): the 2026 rulebook leaves arena comms, and comms between the arena and mission control, as "TBD".

## The 4,000 kbps budget

The rules limit the average rate over a run, not the peak. Short bursts above 4,000 kbps are allowed. A long burst can still delay command messages on a busy link. Three things use the budget:

- Video. It is usually the largest user. Two cameras double it.
- Telemetry and displays: status, pose, and any map or point cloud preview. A raw point cloud is far too large to send. One scan from a 128-beam LiDAR holds tens of thousands of points, and scans repeat several times a second.
- Discovery traffic. ROS 2 machines announce themselves and search for each other. This traffic grows with every node and topic on the link.

Raw images and point clouds stay on the Jetson, where the software uses them. The operator sees compressed video. The OAK-D Pro cameras encode H.264 on the camera, so the Jetson does not spend its own processing power on it.

Measure the average rate over a full run. A short test can miss a slow rise in traffic.

## DDS discovery across machines

ROS 2 uses DDS, a middleware. When nodes start, DDS finds them with multicast announcements on the local network. Multicast works well on a wired network and badly on Wi-Fi, where routers often drop or throttle it. The symptom is that topics appear and disappear, or that a topic from one machine never reaches the other.

Two fixes are common. You can give each machine a fixed address and list the other machine as a discovery peer. Or you can use a different middleware, such as `rmw_zenoh`. The Jazzy tutorial on [improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html) covers the first option.

## The comm check

The comm check follows a fixed procedure, so you can rehearse it. While you wait in the queue, set your equipment to channel 1. Keep all wireless equipment off until your check starts. At the station:

1. Show the judges every wireless part.
2. Control the rover from the laptop, over the wireless link.
3. Turn off 2.4 GHz on the router.

If you use Bluetooth or another non-Wi-Fi radio, bring printed datasheets. If the check takes more than 15 minutes, the team is disqualified.

## What the operator sees

In mission control, the operator uses only data and video from the robot. The arena camera monitors give situational awareness only. Arena team members cannot tell mission control about rocks, craters or other conditions. The dashboard must therefore show everything the operator needs to drive, and to judge the state of a dig or a dump.

## Open questions

1. Does operator video go through ROS and Foxglove, or through a separate video stream?
2. Which topics cross the link, and at what rates?
3. Do we use tuned DDS discovery settings, or `rmw_zenoh`?
4. How do we measure the average link use over a full 20-minute run?
5. Where does the router sit? Does the rover need its own client bridge? The rules leave arena comms undefined, so ask the organisers.
6. What does the operator dashboard show during teleop, and during a hands-free attempt?

## Further reading

- [foxglove_bridge](https://index.ros.org/p/foxglove_bridge/)
- [Foxglove Image panel](https://docs.foxglove.dev/docs/visualization/panels/image)
- [Improved dynamic discovery](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Improved-Dynamic-Discovery.html)
- [rmw_zenoh](https://github.com/ros2/rmw_zenoh)
- [depthai-ros](https://docs.luxonis.com/software/ros/depthai-ros/)
